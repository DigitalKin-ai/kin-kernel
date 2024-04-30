"""
This module defines a gRPC-based Trigger Service with job management capabilities.
"""

import uuid
import json
import inspect
import threading
from enum import Enum
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import Type, TypeVar, Generic, Literal, List, Dict, Any, Optional, Callable

import grpc
from opentelemetry import trace
from pydantic import BaseModel, ValidationError
from google.protobuf import json_format, struct_pb2

import proto.digitalkin.service.v1.trigger.trigger_service_pb2_grpc as trigger_service_pb2_grpc
import proto.digitalkin.service.v1.trigger.trigger_service_pb2 as trigger_service_pb2
import proto.digitalkin.service.v1.tool.tool_service_pb2_grpc as tool_service_pb2_grpc
import proto.digitalkin.service.v1.tool.tool_service_pb2 as tool_service_pb2
from kin_sdk.grpc_services import ServiceServer, ServiceModel
from kin_sdk.common import validate_grpc_request, logger, pydantic_validation_error

InputModelT = TypeVar("InputModelT", bound=BaseModel)
OutputModelT = TypeVar("OutputModelT", bound=BaseModel)
SetupModelT = TypeVar("SetupModelT", bound=BaseModel)


class JobStatus(Enum):
    STARTING = 0
    PROCESSING = 1
    CANCELED = 2
    FAILED = 3
    EXPIRED = 4
    SUCCESS = 5
    STOPPED = 6


class JobManager:
    """
    Manages the lifecycle of jobs.
    """

    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()

    def create_job(self, setup: dict, service_ids: list) -> str:
        """
        Creates a new job with the given setup and service IDs.

        :param setup: The setup configuration for the job.
        :param service_ids: List of service IDs associated with the job.
        :return: The ID of the newly created job.
        """
        job_id = f"trg:{uuid.uuid4().hex}"
        with self.lock:
            self.jobs[job_id] = {
                "setup": setup,
                "service_ids": service_ids,
                "status": JobStatus.STARTING,
            }
        return job_id

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a job by its ID.

        :param job_id: The ID of the job to retrieve.
        :return: The job data if found, None otherwise.
        """
        with self.lock:
            return self.jobs.get(job_id, None)

    def update_job_status(self, job_id: str, status: JobStatus) -> bool:
        """
        Updates the status of a job.

        :param job_id: The ID of the job to update.
        :param status: The new status of the job.
        :return: True if the job status was updated, False otherwise.
        """
        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id]["status"] = status
                return True
            return False

    def delete_job(self, job_id: str) -> bool:
        """
        Deletes a job by its ID.

        :param job_id: The ID of the job to delete.
        :return: True if the job was deleted, False otherwise.
        """
        with self.lock:
            if job_id in self.jobs:
                del self.jobs[job_id]
                return True
            return False


class TriggerService(trigger_service_pb2_grpc.TriggerServiceServicer):
    """
    gRPC service for managing triggers.
    """

    def __init__(self, trigger: "BaseTrigger", job_manager: JobManager):
        self.trigger = trigger
        self.job_manager = job_manager
        self.tracer = trace.get_tracer(self.trigger.__class__.__name__)
        self.executor = ThreadPoolExecutor(max_workers=trigger.max_workers)

    @validate_grpc_request
    def StartTrigger(
        self, request, context: grpc.ServicerContext
    ) -> trigger_service_pb2.TriggerResponse:
        """
        Starts a new trigger.

        :param request: The gRPC request containing input, setup, and service IDs.
        :param context: The gRPC context.
        :return: A TriggerResponse indicating success or failure.
        """
        with self.tracer.start_span("start_trigger"):
            try:
                json_request = json_format.MessageToDict(
                    request,
                    preserving_proto_field_name=True,
                )
                input = json_request.get("input", None)
                setup = json_request.get("setup", None)
                service_ids = json_request.get("service_ids", None)

                if not input or not setup or not service_ids:
                    raise ValueError("😵 Input, setup, and service IDs are required.")

                # Parse and validate the input, setup JSON using Pydantic model
                # and create a new job with the provided service IDs
                input_data = self.trigger.input_format.model_validate(input)
                setup_data = self.trigger.setup_format.model_validate(setup)
                job_id = self.job_manager.create_job(setup_data, service_ids)

                # Start the job in a separate thread
                self.executor.submit(self._start_job, input_data, job_id)

                # Send the response
                return trigger_service_pb2.TriggerResponse(
                    success=True,
                    message="🚀 Trigger has been started!",
                    trigger_id=job_id,
                )
            except ValidationError as e:
                error_message = pydantic_validation_error(e, context)
                logger.error(error_message)  # Validation Error
                return trigger_service_pb2.TriggerResponse(
                    success=False,
                    message=error_message,
                    trigger_id=None,
                )
            except Exception as e:
                logger.error("Exception Error: %s", e)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))

                return trigger_service_pb2.TriggerResponse(
                    success=False,
                    message=str(e),
                    trigger_id=None,
                )

    def _start_job(self, input_data: InputModelT, job_id: str) -> None:
        """
        Starts the job in a separate thread.

        :param input_data: The input data for the job.
        :param job_id: The ID of the job.
        """
        try:
            # Update job status to STARTING
            self.job_manager.update_job_status(job_id, JobStatus.STARTING)
            self.trigger.start()

            if not self.job_manager.update_job_status(job_id, JobStatus.PROCESSING):
                raise ValueError(f"😵 Trigger {job_id} not found.")

            current_job = self.job_manager.get_job(job_id)
            service_ids = current_job.get("service_ids", [])

            # Create a callback that captures the service_ids
            def callback(output: OutputModelT):
                if not self.job_manager.update_job_status(job_id, JobStatus.PROCESSING):
                    raise ValueError(f"😵 Trigger {job_id} not found.")
                self.trigger.send_output(output, service_ids)

            # Execute the job
            self.trigger.execute(
                input_data,
                current_job.get("setup", None),
                callback,
            )
            if input_data.model_fields:
                self.trigger.stop()

        except Exception as e:
            logger.error("😵 Exception Error: %s", e)
            self.job_manager.update_job_status(job_id, JobStatus.FAILED)

    @validate_grpc_request
    def StopTrigger(
        self, request, context: grpc.ServicerContext
    ) -> trigger_service_pb2.TriggerResponse:
        """
        Stops a running trigger.

        :param request: The gRPC request containing the trigger ID.
        :param context: The gRPC context.
        :return: A TriggerResponse indicating success or failure.
        """
        with self.tracer.start_span("stop_trigger"):
            try:
                json_request = json_format.MessageToDict(
                    request,
                    preserving_proto_field_name=True,
                )
                trigger_id = json_request.get("trigger_id", None)

                if not trigger_id:
                    raise ValueError("😵 Trigger ID is required.")

                # Update the job status
                if self.job_manager.update_job_status(trigger_id, JobStatus.STOPPED):
                    if self.job_manager.delete_job(trigger_id):
                        self.trigger.stop()
                        return trigger_service_pb2.TriggerResponse(
                            success=True,
                            message=f"🛑 Trigger {trigger_id} has been stopped!",
                            trigger_id=trigger_id,
                        )
                    else:
                        raise ValueError(f"😵 Trigger {trigger_id} can not be deleted.")
                else:
                    raise ValueError(f"😵 Trigger ID {trigger_id} is not found.")

            except ValidationError as e:
                error_message = pydantic_validation_error(e, context)
                logger.error(error_message)
                return trigger_service_pb2.TriggerResponse(
                    success=False,
                    message=error_message,
                    trigger_id=None,
                )
            except Exception as e:
                logger.error("😵 Exception Error: %s", e)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))

                return trigger_service_pb2.TriggerResponse(
                    success=False,
                    message=str(e),
                    trigger_id=None,
                )

    @validate_grpc_request
    def GetTriggerStatus(
        self, request, context: grpc.ServicerContext
    ) -> trigger_service_pb2.TriggerStatusResponse:
        """
        Retrieves the status of a trigger.

        :param request: The gRPC request containing the trigger ID.
        :param context: The gRPC context.
        :return: A TriggerStatusResponse indicating the status of the trigger.
        """
        with self.tracer.start_span("get_trigger_status"):
            try:
                json_request = json_format.MessageToDict(
                    request,
                    preserving_proto_field_name=True,
                )
                trigger_id = json_request.get("trigger_id", None)

                if not trigger_id:
                    raise ValueError("😵 Trigger ID is required.")

                job = self.job_manager.get_job(trigger_id)
                if job:
                    return trigger_service_pb2.TriggerStatusResponse(
                        success=True,
                        status=job["status"].name,
                        trigger_id=trigger_id,
                    )
                else:
                    raise ValueError(f"😵 Trigger ID {trigger_id} is not found.")

            except ValidationError as e:
                error_message = pydantic_validation_error(e, context)
                logger.error(error_message)  # Validation Error
                return trigger_service_pb2.TriggerStatusResponse(
                    success=False,
                    status=JobStatus.FAILED.name,
                    trigger_id=None,
                )
            except Exception as e:
                logger.error("Exception Error: %s", e)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))

                return trigger_service_pb2.TriggerStatusResponse(
                    success=False,
                    status=JobStatus.FAILED.name,
                    trigger_id=None,
                )

    def add_to_server(self, server: grpc.Server) -> None:
        """
        Adds this service to the given gRPC server.

        :param server: The gRPC server to add this service to.
        """
        trigger_service_pb2_grpc.add_TriggerServiceServicer_to_server(self, server)


class BaseTrigger(Generic[InputModelT, OutputModelT, SetupModelT], ServiceServer, ABC):
    """
    Abstract base class for defining a trigger.
    """

    name: str
    description: str
    input_format: Type[InputModelT]
    output_format: Type[OutputModelT]
    setup_format: Type[SetupModelT]
    status: Literal[
        "STARTING", "PROCESSING", "CANCELED", "FAILED", "EXPIRED", "SUCCESS", "STOPPED"
    ] = "STOPPED"

    def __init__(
        self,
        service_id: str,
        service_address: str,
        service_port: int,
        registry_address: str,
        max_workers: int = 10,
    ):
        """
        Initializes the BaseTrigger.

        :param service_id: The ID of the service.
        :param service_address: The address of the service.
        :param service_port: The port of the service.
        :param registry_address: The address of the registry.
        :param max_workers: The maximum number of worker threads.
        """
        self.max_workers = max_workers
        self.job_manager = JobManager()
        super().__init__(
            service_id=service_id,
            service_address=service_address,
            service_port=service_port,
            service_type="trigger",
            servicer_class=TriggerService,
            servicer_kwargs=dict(
                trigger=self,
                job_manager=self.job_manager,
            ),
            registry_address=registry_address,
            max_workers=max_workers,
        )

    def __init_subclass__(cls, **kwargs):
        """
        Ensures that subclasses define required attributes.
        """
        super().__init_subclass__(**kwargs)
        if not inspect.isabstract(cls):
            required_attrs = [
                "name",
                "description",
                "input_format",
                "output_format",
                "setup_format",
            ]
            for attr in required_attrs:
                if not hasattr(cls, attr) or getattr(cls, attr) is None:
                    raise TypeError(
                        f"Subclass '{cls.__name__}' must define a '{attr}' class variable."
                    )

    @classmethod
    def get_name(cls) -> str:
        """
        Get the name of the tool.

        :return: The name of the tool.
        :raises NotImplementedError: If the `name` is not defined.
        """
        if cls.name is not None:
            return cls.name
        raise NotImplementedError(f"'{cls.__name__}' class does not define a 'role'.")

    @classmethod
    def get_description(cls) -> str:
        """
        Gets the name of the tool.

        :return: The name of the tool.
        :raises NotImplementedError: If the `name` is not defined.
        """
        if cls.description is not None:
            return cls.description
        raise NotImplementedError(
            f"'{cls.__name__}' class does not define a 'description'."
        )

    @classmethod
    def get_output_format(cls) -> str:
        """
        Get the JSON schema of the output format model.

        :return: The JSON schema of the output format as a string.
        :raises NotImplementedError: If the `output_format` is not defined.
        """
        if cls.output_format is not None:
            return json.dumps(cls.output_format.model_json_schema(), indent=2)
        raise NotImplementedError(
            f"'{cls.__name__}' class does not define an 'output_format'."
        )

    @classmethod
    def get_setup_format(cls) -> str:
        """
        Gets the JSON schema of the setup format model.

        :return: The JSON schema of the setup format as a string.
        :raises NotImplementedError: If the `setup_format` is not defined.
        """
        if cls.setup_format is not None:
            return json.dumps(cls.setup_format.model_json_schema(), indent=2)
        raise NotImplementedError(
            f"'{cls.__name__}' class does not define an 'setup_format'."
        )

    @abstractmethod
    def start(self) -> None:
        """
        Starts the trigger.
        """
        raise NotImplementedError("Subclasses must implement 'start' abstract method")

    @abstractmethod
    def execute(
        self,
        input_data: InputModelT,
        setup_data: SetupModelT,
        callback: Callable[[OutputModelT], None],
    ) -> None:
        """
        Executes the trigger.

        :param input_data: The input data for the trigger.
        :param setup_data: The setup data for the trigger.
        :param callback: The callback to call with the output data.
        """
        raise NotImplementedError("Subclasses must implement 'execute' abstract method")

    @abstractmethod
    def stop(self) -> None:
        """
        Stops the trigger.
        """
        raise NotImplementedError("Subclasses must implement 'stop' abstract method")

    def send_output(self, output: OutputModelT, service_ids: List[str]) -> None:
        """
        Sends the output to the list of gRPC services.

        :param output: The output data to send.
        :param service_ids: The list of service IDs to send the output to.
        """
        try:
            # Validate and serialize the output using the output_format Pydantic model
            output_data = self.output_format.model_validate(
                output.model_dump()
            ).model_dump()
            # Convert in gRPC Struct proto format the output data in order to send it as input of a block
            struct_input = json_format.ParseDict(output_data, struct_pb2.Struct())
            # use service_ids to send the output to the right service

            for service_id in service_ids:
                service: ServiceModel = self.search_service(service_id)
                logger.info(f"Service found: \n\t{service}")

                # Send the result to the list of gRPC services
                with grpc.insecure_channel(
                    f"{service.address}:{service.port}"
                ) as channel:
                    if service.service_type == "tool":
                        try:
                            stub = tool_service_pb2_grpc.ToolServiceStub(channel)
                            request = tool_service_pb2.ExecuteRequest(
                                input=struct_input
                            )
                            stub.ExecuteTool(request)
                            logger.info(
                                f"📞 Output sent to Tool service {service_id} \n\t{service}"
                            )
                        except grpc.RpcError as e:
                            # Handle gRPC exceptions
                            message = f"😵 Error sending output to Tool service {service_id}:\n\t"
                            if e.code() == grpc.StatusCode.UNAVAILABLE:
                                message += "Server is unavailable"
                            elif e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                                message += "Deadline exceeded"
                            elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                                message += (
                                    f"Invalid argument provided: \n\t - {e.details()}"
                                )
                            else:
                                message += f"An error occurred: {e.details()} (code: {e.code()})"
                            logger.error(message)
        except Exception as e:
            logger.error("Exception during send_output: %s", e)
            raise Exception(str(e))

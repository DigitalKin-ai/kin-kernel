"""
Todo: sphinx docstring
"""

import inspect
import threading
import uuid
from abc import ABC, abstractmethod
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
from typing import TypeVar, List, Dict, Any, Optional, Type, Generic, Callable

import grpc
from opentelemetry import trace
from pydantic import BaseModel, ValidationError
from google.protobuf import json_format, struct_pb2

from kin_sdk.trigger.base import BaseTrigger
from kin_sdk.tool.base import BaseTool
from kin_sdk.grpc_services import ServiceServer
from kin_sdk.common import validate_grpc_request, logger, pydantic_validation_error

import proto.digitalkin.service.v1.kin.kin_service_pb2_grpc as kin_service_pb2_grpc
import proto.digitalkin.service.v1.kin.kin_service_pb2 as kin_service_pb2

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

    def create_job(self, setup: dict, kin_id: str, trigger_id: str) -> str:
        """
        Creates a new job with the given setup and service IDs.

        :param setup: The setup configuration for the job.
        :param kin_id: Kin ID associated with the job.
        :param trigger_id: Trigger ID associated with the job.
        :return: The ID of the newly created job.
        """
        job_id = f"trg:{uuid.uuid4().hex}"
        with self.lock:
            self.jobs[job_id] = {
                "setup": setup,
                "kin_id": kin_id,
                "trigger_id": trigger_id,
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


class KinService(kin_service_pb2_grpc.KinServiceServicer):
    """
    gRPC service for managing kins.
    """

    def __init__(self, kin: "BaseKin", job_manager: JobManager):
        self.kin = kin
        self.job_manager = job_manager
        self.tracer = trace.get_tracer(self.kin.__class__.__name__)
        self.executor = ThreadPoolExecutor(max_workers=kin.max_workers)

    @validate_grpc_request
    def StartKin(
        self, request, context: grpc.ServicerContext
    ) -> kin_service_pb2.KinResponse:
        """
        Starts a new kin.

        :param request: The gRPC request containing input, setup, and service IDs.
        :param context: The gRPC context.
        :return: A KinResponse indicating success or failure.
        """
        with self.tracer.start_span("start_kin"):
            try:
                json_request = json_format.MessageToDict(
                    request,
                    preserving_proto_field_name=True,
                )
                input = json_request.get("input", None)
                setup = json_request.get("setup", None)
                kin_id = json_request.get("kin_id", None)
                trigger_id = json_request.get("trigger_id", None)

                if not input or not setup or not kin_id or not trigger_id:
                    raise ValueError(
                        "😵 Input, setup, Kin ID, and Trigger ID are required."
                    )

                # Parse and validate the input, setup JSON using Pydantic model
                # and create a new job with the provided service IDs
                input_data = self.kin.input_format.model_validate(input)
                setup_data = self.kin.setup_format.model_validate(setup)
                job_id = self.job_manager.create_job(setup_data, kin_id, trigger_id)

                # Start the job in a separate thread
                self.executor.submit(self._start_job, input_data, job_id)

                # Send the response
                return kin_service_pb2.KinResponse(
                    success=True,
                    message="🚀 Kin has been started!",
                    kin_id=kin_id,
                )
            except ValidationError as e:
                error_message = pydantic_validation_error(e, context)
                logger.error(error_message)  # Validation Error
                return kin_service_pb2.KinResponse(
                    success=False,
                    message=error_message,
                    kin_id=None,
                )
            except Exception as e:
                logger.error("Exception Error: %s", e)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))

                return kin_service_pb2.KinResponse(
                    success=False,
                    message=str(e),
                    kin_id=None,
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
            self.kin.start()

            if not self.job_manager.update_job_status(job_id, JobStatus.PROCESSING):
                raise ValueError(f"😵 Kin {job_id} not found.")

            current_job = self.job_manager.get_job(job_id)
            # service_ids = current_job.get("service_ids", [])

            # Create a callback that captures the service_ids
            def callback(output: OutputModelT):
                if not self.job_manager.update_job_status(job_id, JobStatus.PROCESSING):
                    raise ValueError(f"😵 Kin {job_id} not found.")
                # self.kin.send_output(output, service_ids)

            # Execute the job
            self.kin.execute(
                input_data,
                current_job.get("setup", None),
                callback,
            )
            if input_data.model_fields:
                self.kin.stop()

        except Exception as e:
            logger.error("😵 Exception Error: %s", e)
            self.job_manager.update_job_status(job_id, JobStatus.FAILED)

    @validate_grpc_request
    def StopKin(
        self, request, context: grpc.ServicerContext
    ) -> kin_service_pb2.KinResponse:
        """
        Stops a running kin.

        :param request: The gRPC request containing the kin ID.
        :param context: The gRPC context.
        :return: A KinResponse indicating success or failure.
        """
        with self.tracer.start_span("stop_kin"):
            try:
                json_request = json_format.MessageToDict(
                    request,
                    preserving_proto_field_name=True,
                )
                kin_id = json_request.get("kin_id", None)

                if not kin_id:
                    raise ValueError("😵 Kin ID is required.")

                # Update the job status
                if self.job_manager.update_job_status(kin_id, JobStatus.STOPPED):
                    if self.job_manager.delete_job(kin_id):
                        self.kin.stop()
                        return kin_service_pb2.KinResponse(
                            success=True,
                            message=f"🛑 Kin {kin_id} has been stopped!",
                            kin_id=kin_id,
                        )
                    else:
                        raise ValueError(f"😵 Kin {kin_id} can not be deleted.")
                else:
                    raise ValueError(f"😵 Kin ID {kin_id} is not found.")

            except ValidationError as e:
                error_message = pydantic_validation_error(e, context)
                logger.error(error_message)
                return kin_service_pb2.KinResponse(
                    success=False,
                    message=error_message,
                    trigger_id=None,
                )
            except Exception as e:
                logger.error("😵 Exception Error: %s", e)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))

                return kin_service_pb2.KinResponse(
                    success=False,
                    message=str(e),
                    kin_id=None,
                )

    @validate_grpc_request
    def GetKinStatus(
        self, request, context: grpc.ServicerContext
    ) -> kin_service_pb2.KinStatusResponse:
        """
        Retrieves the status of a kin.

        :param request: The gRPC request containing the kin ID.
        :param context: The gRPC context.
        :return: A KinStatusResponse indicating the status of the kin.
        """
        with self.tracer.start_span("get_kin_status"):
            try:
                json_request = json_format.MessageToDict(
                    request,
                    preserving_proto_field_name=True,
                )
                kin_id = json_request.get("kin_id", None)

                if not kin_id:
                    raise ValueError("😵 Kin ID is required.")

                job = self.job_manager.get_job(kin_id)
                if job:
                    return kin_service_pb2.KinStatusResponse(
                        success=True,
                        status=job["status"].name,
                        kin_id=kin_id,
                    )
                else:
                    raise ValueError(f"😵 Kin ID {kin_id} is not found.")

            except ValidationError as e:
                error_message = pydantic_validation_error(e, context)
                logger.error(error_message)  # Validation Error
                return kin_service_pb2.KinStatusResponse(
                    success=False,
                    status=JobStatus.FAILED.name,
                    kin_id=None,
                )
            except Exception as e:
                logger.error("Exception Error: %s", e)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))

                return kin_service_pb2.KinStatusResponse(
                    success=False,
                    status=JobStatus.FAILED.name,
                    kin_id=None,
                )

    def add_to_server(self, server: grpc.Server) -> None:
        """
        Adds this service to the given gRPC server.

        :param server: The gRPC server to add this service to.
        """
        kin_service_pb2_grpc.add_KinServiceServicer_to_server(self, server)


class BaseKin(Generic[InputModelT, OutputModelT, SetupModelT], ServiceServer, ABC):
    name: str
    description: str
    triggers: List[BaseTrigger]
    tools: List[BaseTool]
    input_format: Type[InputModelT]
    output_format: Type[OutputModelT]
    setup_format: Type[SetupModelT]

    def __init__(
        self,
        service_id: str,
        service_address: str,
        service_port: int,
        registry_address: str,
        max_workers: int = 10,
    ):
        self.registry_address = registry_address
        self.max_workers = max_workers
        self.job_manager = JobManager()
        super().__init__(
            service_id=service_id,
            service_address=service_address,
            service_port=service_port,
            service_type="kin",
            servicer_class=KinService,
            servicer_kwargs=dict(
                trigger=self,
                job_manager=self.job_manager,
            ),
            registry_address=registry_address,
            max_workers=max_workers,
        )

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not inspect.isabstract(cls):
            required_attrs = ["name", "description", "triggers", "tools"]
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
        Get the description of the cell.

        :return: The description of the cell.
        :raises NotImplementedError: If the `description` is not defined.
        """
        if cls.description is not None:
            return cls.description
        raise NotImplementedError(
            f"'{cls.__name__}' class does not define a 'description'."
        )

    @abstractmethod
    def start(self) -> None:
        """
        Starts the kin.
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
        Executes the kin.
        """
        raise NotImplementedError("Subclasses must implement 'execute' abstract method")

    @abstractmethod
    def stop(self) -> None:
        """
        Stops the kin.
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
            print(struct_input)
            # for service_id in service_ids:
            #     service: ServiceModel = self.search_service(service_id)
            #     logger.info(f"Service found: \n\t{service}")

            #     # Send the result to the list of gRPC services
            #     with grpc.insecure_channel(
            #         f"{service.address}:{service.port}"
            #     ) as channel:
            #         if service.service_type == "tool":
            #             try:
            #                 stub = tool_service_pb2_grpc.ToolServiceStub(channel)
            #                 request = tool_service_pb2.ExecuteRequest(
            #                     input=struct_input
            #                 )
            #                 stub.ExecuteTool(request)
            #                 logger.info(
            #                     f"📞 Output sent to Tool service {service_id} \n\t{service}"
            #                 )
            #             except grpc.RpcError as e:
            #                 # Handle gRPC exceptions
            #                 message = f"😵 Error sending output to Tool service {service_id}:\n\t"
            #                 if e.code() == grpc.StatusCode.UNAVAILABLE:
            #                     message += "Server is unavailable"
            #                 elif e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
            #                     message += "Deadline exceeded"
            #                 elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            #                     message += (
            #                         f"Invalid argument provided: \n\t - {e.details()}"
            #                     )
            #                 else:
            #                     message += f"An error occurred: {e.details()} (code: {e.code()})"
            #                 logger.error(message)
        except Exception as e:
            logger.error("Exception during send_output: %s", e)
            raise Exception(str(e))

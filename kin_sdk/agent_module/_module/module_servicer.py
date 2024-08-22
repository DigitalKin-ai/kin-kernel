"""
TODO: sphinx docstring
"""

import json
import threading
from typing import Any, Generator

import grpc

from opentelemetry import trace
from google.protobuf import json_format, struct_pb2
from pydantic import BaseModel
from proto.digitalkin.module.v1.module_service_pb2_grpc import (
    ModuleServiceServicer,
    add_ModuleServiceServicer_to_server,
)
from proto.digitalkin.module.v1.lifecycle_pb2 import (
    StartModuleRequest,
    StartModuleResponse,
    OutputDataResponse,
    ErrorResponse,
    StopModuleRequest,
    StopModuleResponse,
)
from proto.digitalkin.module.v1.monitoring_pb2 import (
    GetModuleStatusRequest,
    GetModuleStatusResponse,
)
from proto.digitalkin.module.v1.information_pb2 import (
    GetModuleInputRequest,
    GetModuleInputResponse,
    GetModuleOutputRequest,
    GetModuleOutputResponse,
)
from kin_sdk.common.validate_grpc_request import validate_grpc_request
from kin_sdk.agent_module._module.base import BaseModule
from kin_sdk.common import (
    Rooms,
    validate_stream_request,
    JobManager,
    Job,
    JobStatus,
    logger,
)


class ModuleServicer(ModuleServiceServicer):
    """TODO: Sphinx docstring"""

    def __init__(self, module: BaseModule):
        self.module = module
        self.job_manager = JobManager(self.module.max_workers)
        self.rooms: Rooms = Rooms()  # ! TODO: remove expired rooms
        self.tracer = trace.get_tracer(self.module.__class__.__name__)
        self.lock = threading.Lock()

    def __start_job(
        self, job_id: str, *args, **kwargs  # pylint: disable=unused-argument
    ) -> None:
        """
        Starts the job in a separate thread.
        """

        try:
            # Update job status to STARTING
            self.job_manager.update_job_status(job_id, JobStatus.STARTING)

            # Get job information
            current_job: Job = self.job_manager.get_job(job_id)
            input_data = current_job.input_data
            setup_id = current_job.setup_id
            module_ids = current_job.module_ids

            # Start the module
            self.module.start()

            # Create a callback that captures the module_ids
            def callback(output: BaseModel):
                if not self.job_manager.update_job_status(job_id, JobStatus.PROCESSING):
                    raise ValueError(f"😵 Trigger {job_id} not found.")
                self.module.send_output(output, module_ids)
                print(output)
                current_job.add_to_outputs(output)

            # Execute the module
            self.module.execute(
                input_data,
                setup_id,
                callback,
            )
            self.__stop_job(job_id)

        except ValueError as e:
            logger.error("😵 Exception Error: %s", e)
            self.job_manager.update_job_status(job_id, JobStatus.FAILED)

    def __stop_job(
        self, job_id: str, *args, **kwargs  # pylint: disable=unused-argument
    ) -> None:
        try:
            self.module.stop()
            self.job_manager.update_job_status(job_id, JobStatus.STOPPED)
            self.job_manager.stop_outputs(job_id)
        except ValueError as e:
            logger.error("😵 Exception Error: %s", e)
            self.job_manager.update_job_status(job_id, JobStatus.FAILED)

    @validate_stream_request()
    def StartModule(  # pylint: disable=arguments-renamed
        self, request: StartModuleRequest, context: grpc.ServicerContext
    ) -> Generator[StartModuleResponse, Any, Any]:
        """
        https://medium.com/@iamdeepaksinghh/create-a-real-time-chat-service-using-grpc-in-python-fc63127d570c
        """
        try:
            # Convert the request to a dictionary
            json_request = json_format.MessageToDict(
                request,
                preserving_proto_field_name=True,
            )
            # Extract data from the request
            input_param = json_request.get("input", None)
            module_ids = json_request.get("module_ids", [])
            setup_id = json_request.get("setup_id", None)

            # Validate the input_param data
            input_data = self.module.input_format.model_validate(input_param)
            # Create and Start the job
            job_id = self.job_manager.start_job(
                input_data, setup_id, module_ids, self.__start_job
            )
            for output in self.job_manager.get_outputs(job_id):
                print(output)
                output_struct = json_format.Parse(
                    text=json.dumps(output.model_dump()),
                    message=struct_pb2.Struct(),  # pylint: disable=no-member
                    ignore_unknown_fields=True,
                )
                yield StartModuleResponse(
                    success=True,
                    response_type="START_RESPONSE_TYPE_OUTPUT",
                    output_response=OutputDataResponse(
                        message="New output from the module",
                        output=output_struct,
                        job_id=job_id,
                    ),
                    module_id=self.module.module_id,
                )
            # Mark the job as completed
            self.job_manager.update_job_status(job_id, JobStatus.SUCCESS)
            return
        except ValueError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            yield StartModuleResponse(
                success=False,
                response_type="START_RESPONSE_TYPE_ERROR",
                error=ErrorResponse(
                    message="An error occurred while starting the module",
                    details=str(e),
                ),
            )
            return

    def StopModule(
        self, request: StopModuleRequest, context: grpc.ServicerContext
    ) -> StopModuleResponse:
        print("Stop module")

    @validate_grpc_request
    def GetModuleStatus(
        self,
        request: GetModuleStatusRequest,
        context: grpc.ServicerContext,
    ) -> GetModuleStatusResponse:
        try:
            job_id = request.job_id

            if not job_id:
                raise ValueError("😵 Job ID is required.")

            job = self.job_manager.get_job(job_id)
            if job is not None:
                return GetModuleStatusResponse(
                    success=True,
                    status=job.status.name,
                    job_id=job_id,
                )
            raise ValueError(f"😵 Job ID {job_id} is not found.")

        except ValueError as e:
            logger.error("Exception Error: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            return GetModuleStatusResponse(
                success=False,
                status=JobStatus.FAILED.name,
                job_id=None,
            )

    def GetModuleInput(
        self, request: GetModuleInputRequest, context: grpc.ServicerContext
    ) -> GetModuleInputResponse:
        print("Get module input schema")

    def GetModuleOutput(
        self,
        _request: GetModuleOutputRequest,
        _context: grpc.ServicerContext,
    ) -> GetModuleOutputResponse:
        """TODO: Sphinx docstring"""
        print("Get module output schema")

    def add_to_server(self, server: grpc.Server) -> None:
        """TODO: Sphinx docstring"""
        add_ModuleServiceServicer_to_server(self, server)

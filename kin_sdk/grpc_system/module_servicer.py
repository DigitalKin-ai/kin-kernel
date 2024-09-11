"""
TODO: sphinx docstring
"""

import json
import threading
from typing import Any, AsyncGenerator, Type

import grpc

from opentelemetry import trace
from google.protobuf import json_format, struct_pb2
from pydantic import BaseModel
from proto.digitalkin.module.v1.module_service_pb2_grpc import (
    ModuleServiceServicer,
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
    GetModuleJobsRequest,
    GetModuleJobsResponse,
    JobInfo,
)
from proto.digitalkin.module.v1.information_pb2 import (
    GetModuleInputRequest,
    GetModuleInputResponse,
    GetModuleOutputRequest,
    GetModuleOutputResponse,
)
from kin_sdk.agent_management import AgentManagement
from kin_sdk.agent_module._module.base import BaseModule
from kin_sdk.common.logger import logger
from kin_sdk.common.job_manager import JobManager, Job, JobStatus
from kin_sdk.models.rooms import Rooms
from kin_sdk.validation.grpc_decorators import (
    validate_grpc_request,
    validate_stream_request,
)


class ModuleServicer(ModuleServiceServicer):
    """TODO: Sphinx docstring"""

    def __init__(
        self, module_class: Type[BaseModule], agent_management: AgentManagement
    ):
        self.module_class = module_class
        self.agent_management = agent_management
        self.job_manager = JobManager()
        self.rooms: Rooms = Rooms()  # ! TODO: remove expired rooms
        self.tracer = trace.get_tracer(self.module_class.__class__.__name__)
        self.lock = threading.Lock()

    async def _start_job(
        self,
        job: Job,
    ) -> None:
        """
        Starts the job in a separate thread.
        """

        try:
            # Update job status to STARTING
            update_status = self.job_manager.update_status(job.id, JobStatus.STARTING)

            if not update_status:
                raise ValueError(f"😵 Trigger {job.id} not found.")
            # self.job_manager.update_job_status(job_id, JobStatus.STARTING)

            # Get job information
            # current_job: Job = self.job_manager.get_job(job_id)
            module = job.module
            input_data = job.input_data
            setup_id = job.setup_id
            module_ids = job.module_ids

            # Start the module
            await module.start(setup_id=setup_id)

            # await job.output_queue.put(InitModel(start=True))

            # Create a callback that captures the module_ids
            async def callback(output: BaseModel) -> None:
                if not self.job_manager.update_status(job.id, JobStatus.PROCESSING):
                    raise ValueError(f"😵 Trigger {job.id} not found.")
                await module.send_output(output, module_ids)
                # await current_job.add_to_outputs(output)
                await job.output_queue.put(
                    output
                )  # Ajoute l'élément dans la file d'attente

            # Execute the module
            await module.execute(input_data, setup_id, callback)
            await self._stop_job(job)

        except ValueError as e:
            logger.error("😵 Exception Error: %s", e)
            self.job_manager.update_status(job.id, JobStatus.FAILED)

    async def _stop_job(
        self, job: Job, *args, **kwargs  # pylint: disable=unused-argument
    ) -> None:
        try:
            # Retrieve the current job and module
            # current_job: Job = self.job_manager.get_job(job_id)
            module = job.module

            # Stop the module
            await module.stop()

            # Update the job status
            self.job_manager.update_status(job.id, JobStatus.STOPPED)
            await self.job_manager.stop_job(job.id)
        except ValueError as e:
            logger.error("😵 Exception Error: %s", e)
            self.job_manager.update_status(job.id, JobStatus.FAILED)

    @validate_stream_request
    async def StartModule(  # pylint: disable=arguments-renamed
        self, request: StartModuleRequest, context: grpc.aio.ServicerContext
    ) -> AsyncGenerator[StartModuleResponse, Any]:
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
            input_data = self.module_class.validate_format(input_param, "input")

            # Create and Start the job
            job_id = await self.job_manager.start_job(
                module=self.module_class(agent_management=self.agent_management),
                input_data=input_data,
                setup_id=setup_id,
                module_ids=module_ids,
                function=self._start_job,
            )

            # Get the current job
            # current_job: Job = self.job_manager.get_job(job_id)

            async for output in self.job_manager.output(job_id):
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
                    module_id=self.agent_management.identity.id,  # ? is there any other and better way to get the module id
                )
            # Mark the job as completed
            self.job_manager.update_status(job_id, JobStatus.SUCCESS)
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

    @validate_grpc_request
    async def StopModule(
        self, request: StopModuleRequest, context: grpc.aio.ServicerContext
    ) -> StopModuleResponse:
        try:
            # Extract the job_id from the request
            job_id = request.job_id

            # Validate the job_id
            if not job_id:
                raise ValueError("😵 Job ID is required.")

            # Get the current job
            current_job = self.job_manager.get_job(job_id)
            # Check if the job is not found
            if current_job is None:
                raise ValueError("😵 Job ID is not found.")

            # Stop the job
            await self._stop_job(current_job)
            return StopModuleResponse(
                success=True,
                message=f"Job ID {job_id} has been stopped.",
                job_id=job_id,
            )

        except ValueError as e:
            logger.error("Exception Error: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"😵 Impossible to stop the job: {str(e)}")

            return StopModuleResponse(
                success=False,
                message=f"😵 Impossible to stop the job: {str(e)}",
                job_id=job_id,
            )

    @validate_grpc_request
    async def GetModuleStatus(
        self,
        request: GetModuleStatusRequest,
        context: grpc.aio.ServicerContext,
    ) -> GetModuleStatusResponse:
        try:
            # Extract the job_id from the request
            job_id = request.job_id

            # Validate the job_id
            if not job_id:
                raise ValueError("😵 Job ID is required.")

            # Retrieve the job
            job = self.job_manager.get_job(job_id)

            # Return the job status
            if job is not None:
                return GetModuleStatusResponse(
                    success=True,
                    status=job.status.name,
                    job_id=job_id,
                )

            # Raise an error if the job is not found
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

    @validate_grpc_request
    async def GetModuleJobs(
        self,
        _request: GetModuleJobsRequest,
        context: grpc.aio.ServicerContext,
    ) -> GetModuleJobsResponse:
        try:

            # Retrieve the job
            jobs = self.job_manager.get_jobs_list()
            print(f"jobs: {jobs}")
            if len(jobs) > 0:
                print(f"jobs: {jobs[0].job_id}")
                print(f"jobs: {jobs[0].job_status}")
                print(f"jobs: {jobs[0].job_status.value}")
                print(f"jobs: {jobs[0].job_status.name}")
            response_jobs = [
                JobInfo(job_id=job.job_id, job_status=job.job_status.value)
                for job in jobs
            ]

            # Return the job status
            return GetModuleJobsResponse(
                success=True,
                jobs=response_jobs,
            )

        except ValueError as e:
            logger.error("Exception Error: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            return GetModuleJobsResponse(
                success=False,
                jobs=[],
            )

    async def GetModuleInput(
        self, request: GetModuleInputRequest, context: grpc.aio.ServicerContext
    ) -> GetModuleInputResponse:
        try:
            llm_format = request.llm_format
            # ! job_id instead of module_id to get a specific module it is important for KinModel Module
            module_id = request.module_id  # pylint: disable=unused-variable # noqa

            json_string = self.module_class.get_input_format(llm_format)
            input_format_struct = json_format.Parse(
                text=json_string,
                message=struct_pb2.Struct(),  # pylint: disable=no-member
                ignore_unknown_fields=True,
            )
            return GetModuleInputResponse(
                success=True,
                input_schema=input_format_struct,
            )
        except ValueError as e:
            logger.error("Exception Error: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            return GetModuleInputResponse(
                success=False,
                input_schema=None,
            )

    async def GetModuleOutput(
        self,
        _request: GetModuleOutputRequest,
        _context: grpc.aio.ServicerContext,
    ) -> GetModuleOutputResponse:
        """TODO: Sphinx docstring"""
        logger.info("Get module output schema, Method Not implemented")

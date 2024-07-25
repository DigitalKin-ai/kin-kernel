"""
TODO: sphinx docstring
"""

import threading
import grpc

from typing import Any, Generator
from opentelemetry import trace
from google.protobuf import json_format  # , struct_pb2
from pydantic import BaseModel

from kin_sdk.common.validate_grpc_request import validate_grpc_request
import proto.digitalkin.service.v1.service_pb2 as service_pb2
import proto.digitalkin.service.v1.service_pb2_grpc as service_pb2_grpc
from kin_sdk.service.base import BaseService
from kin_sdk.common import (
    Rooms,
    validate_stream_request,
    JobManager,
    Job,
    JobStatus,
    logger,
)

COUNTER = 0


class Service(service_pb2_grpc.ServiceServicer):
    def __init__(self, service: BaseService):
        self.service = service
        self.job_manager = JobManager(self.service.max_workers)
        self.rooms: Rooms = Rooms()  # TODO: remove expired rooms
        self.tracer = trace.get_tracer(self.service.__class__.__name__)
        self.lock = threading.Lock()

    def __start_job(self, job_id: str, *args, **kwargs) -> None:
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
            service_ids = current_job.service_ids

            # Start the service
            self.service.start()

            # Create a callback that captures the service_ids
            def callback(output: BaseModel):
                if not self.job_manager.update_job_status(job_id, JobStatus.PROCESSING):
                    raise ValueError(f"😵 Trigger {job_id} not found.")
                self.service.send_output(output, service_ids)
                print(output)
                current_job.add_to_outputs(output)

            # Execute the service
            self.service.execute(
                input_data,
                setup_id,
                callback,
            )
            self.__stop_job(job_id)

        except Exception as e:
            logger.error("😵 Exception Error: %s", e)
            self.job_manager.update_job_status(job_id, JobStatus.FAILED)

    def __stop_job(self, job_id: str, *args, **kwargs) -> None:
        try:
            self.service.stop()
            self.job_manager.update_job_status(job_id, JobStatus.STOPPED)
            self.job_manager.stop_outputs(job_id)
            print("Job stopped")
        except Exception as e:
            logger.error("😵 Exception Error: %s", e)
            self.job_manager.update_job_status(job_id, JobStatus.FAILED)

    @validate_stream_request()
    def StartService(
        self, request: service_pb2.StartServiceRequest, context: grpc.ServicerContext
    ) -> Generator[service_pb2.ServiceResponse, Any, Any]:
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
            input = json_request.get("input", None)
            service_ids = json_request.get("service_ids", [])
            setup_id = json_request.get("setup_id", None)

            # Validate the input data
            input_data = self.service.input_format.model_validate(input)

            # Create and Start the job
            job_id = self.job_manager.start_job(
                input_data, setup_id, service_ids, self.__start_job
            )

            for output in self.job_manager.get_outputs(job_id):
                yield service_pb2.ServiceResponse(
                    success=True,
                    message=str(output),
                    service_id=job_id,
                )
            # Mark the job as completed
            self.job_manager.update_job_status(job_id, JobStatus.SUCCESS)
            return
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return service_pb2.ServiceResponse(
                success=False, message="Failed to start service"
            )

    def StopService(
        self, request: service_pb2.StopServiceRequest, context: grpc.ServicerContext
    ) -> service_pb2.ServiceResponse:
        print("Stop service")

    @validate_grpc_request
    def GetServiceStatus(
        self,
        request: service_pb2.GetServiceStatusRequest,
        context: grpc.ServicerContext,
    ) -> service_pb2.ServiceStatusResponse:
        try:
            job_id = request.job_id

            if not job_id:
                raise ValueError("😵 Job ID is required.")

            job = self.job_manager.get_job(job_id)
            if job is not None:
                return service_pb2.ServiceStatusResponse(
                    success=True,
                    status=job.status.name,
                    job_id=job_id,
                )
            raise ValueError(f"😵 Job ID {job_id} is not found.")

        except Exception as e:
            logger.error("Exception Error: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            return service_pb2.ServiceStatusResponse(
                success=False,
                status=JobStatus.FAILED.name,
                service_id=None,
            )

    def GetServiceInput(
        self, request: service_pb2.GetServiceInputRequest, context: grpc.ServicerContext
    ) -> service_pb2.ServiceInputResponse:
        print("Get service input schema")

    def GetServiceOutput(
        self,
        request: service_pb2.GetServiceOutputRequest,
        context: grpc.ServicerContext,
    ) -> service_pb2.ServiceOutputResponse:
        print("Get service output schema")

    def add_to_server(self, server: grpc.Server) -> None:
        service_pb2_grpc.add_ServiceServicer_to_server(self, server)

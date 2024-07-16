"""
TODO: sphinx docstring
"""

import threading
from typing import Dict, Any, Generator
import grpc
from opentelemetry import trace

import proto.digitalkin.service.v1.service_pb2 as service_pb2
import proto.digitalkin.service.v1.service_pb2_grpc as service_pb2_grpc
from kin_sdk.service.base import BaseService
from kin_sdk.common import Room, validate_stream_request, ValidatedRequest


class Service(service_pb2_grpc.ServiceServicer):
    def __init__(self, service: BaseService):
        self.service = service
        self.rooms: Dict[str, Room] = {}
        self.tracer = trace.get_tracer(self.service.__class__.__name__)
        self.lock = threading.Lock()

    @validate_stream_request()
    def StartService(
        self, validated_request: ValidatedRequest, context: grpc.ServicerContext
    ) -> Generator[service_pb2.ServiceResponse, Any, Any]:
        try:
            if not validated_request.success:
                raise Exception(validated_request.details)

            request = validated_request.request
            print("Start service")
            print(request)
            yield service_pb2.ServiceResponse(
                success=True,
                message="Service started successfully",
                service_id="service_id",
            )
            return
        except Exception as e:
            print(e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            yield service_pb2.ServiceResponse(
                success=False, message="Failed to start service"
            )

    def StopService(
        self, request: service_pb2.StopServiceRequest, context: grpc.ServicerContext
    ) -> service_pb2.ServiceResponse:
        print("Stop service")

    def GetServiceStatus(
        self,
        request: service_pb2.GetServiceStatusRequest,
        context: grpc.ServicerContext,
    ) -> service_pb2.ServiceStatusResponse:
        print("Get service status")

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

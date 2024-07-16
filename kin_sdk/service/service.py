"""
TODO: sphinx docstring
"""

import grpc
from opentelemetry import trace

import kin_sdk.service.base as base_service
import proto.digitalkin.service.v1.service_pb2 as service_pb2
import proto.digitalkin.service.v1.service_pb2_grpc as service_pb2_grpc


class Service(service_pb2_grpc.ServiceServicer):
    def __init__(self, service: base_service.BaseService):
        self.service = service
        self.tracer = trace.get_tracer(self.tool.__class__.__name__)

    def StartService(
        self, request, context: grpc.ServicerContext
    ) -> service_pb2.ServiceResponse:
        print("Start service")

    def add_to_server(self, server: grpc.Server) -> None:
        service_pb2_grpc.add_ServiceServicer_to_server(self, server)

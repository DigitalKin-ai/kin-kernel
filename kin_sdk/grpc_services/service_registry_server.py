from kin_sdk.common import validate_grpc_request
from kin_sdk.grpc_services.grpc_server_base import GRPCServerBase

# Protos gRPC
import proto.digitalkin.service.v1.registry.service_registry_pb2 as service_registry_pb2
import proto.digitalkin.service.v1.registry.service_registry_pb2_grpc as service_registry_pb2_grpc


class ServiceRegistry(service_registry_pb2_grpc.ServiceRegistryServicer):
    def __init__(self):
        # Store services in a dictionary
        # TODO replace by a bridge pattern to store services in a database
        self.services = {}

    @validate_grpc_request
    def RegisterService(self, request, context):
        self.services[request.service_id] = {
            "type": request.service_type,
            "address": request.address,
            "port": request.port,
            "status": True,  # Assume service is active when registered
        }
        return service_registry_pb2.RegisterResponse(success=True)

    @validate_grpc_request
    def DeregisterService(self, request, context):
        if request.service_id in self.services:
            del self.services[request.service_id]
            return service_registry_pb2.DeregisterResponse(success=True)
        return service_registry_pb2.DeregisterResponse(success=False)

    @validate_grpc_request
    def DiscoverService(self, request, context):
        service = self.services.get(request.service_id, None)
        print(f"Service: {service}")
        if service:
            return service_registry_pb2.DiscoverResponse(
                service_type=service["type"],
                address=service["address"],
                port=service["port"],
                status=service["status"],
            )
        return service_registry_pb2.DiscoverResponse()

    @validate_grpc_request
    def UpdateServiceStatus(self, request, context):
        if request.service_id in self.services:
            self.services[request.service_id]["status"] = request.status
            return service_registry_pb2.UpdateStatusResponse(success=True)
        return service_registry_pb2.UpdateStatusResponse(success=False)

    @classmethod
    def add_to_server(cls, server):
        service_registry_pb2_grpc.add_ServiceRegistryServicer_to_server(cls(), server)


class ServiceRegistryServer(GRPCServerBase):
    def __init__(self, port):
        super().__init__(ServiceRegistry, port)

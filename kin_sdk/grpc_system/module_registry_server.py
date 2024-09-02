"""
TODO: Add module description.
"""

from typing import Dict, Any

import grpc
from kin_sdk.common import validate_grpc_request
from kin_sdk.grpc_system.grpc_server_base import GRPCServerBase

# Protos gRPC
import proto.digitalkin.module_registry.v1.module_registry_service_pb2_grpc as module_registry_pb2_grpc
import proto.digitalkin.module_registry.v1.registration_pb2 as registration_pb2
import proto.digitalkin.module_registry.v1.action_pb2 as action_pb2


class ModuleRegistry(module_registry_pb2_grpc.ModuleRegistryServiceServicer):
    """
    ModuleRegistry service for registering, deregistering, discovering, and updating modules.
    """

    def __init__(self) -> None:
        """
        Initializes the ModuleRegistry with an empty dictionary to store modules.
        """
        # ! TODO replace by a bridge pattern to store services in a database
        self.modules: Dict[str, Dict[str, Any]] = {}

    @validate_grpc_request
    async def RegisterModule(
        self,
        request: registration_pb2.RegisterRequest,
        context: grpc.aio.ServicerContext,
    ) -> registration_pb2.RegisterResponse:
        """
        Registers a module with the given details.

        :param request: The registration request containing module details.
        :type request: registration_pb2.RegisterRequest
        :param context: The gRPC context.
        :return: The registration response indicating success.
        :rtype: registration_pb2.RegisterResponse
        """
        print("RegisterModule")
        self.modules[request.module_id] = {
            "type": request.module_type,
            "address": request.address,
            "port": request.port,
            "status": True,  # Assume service is active when registered
        }
        return registration_pb2.RegisterResponse(success=True)

    @validate_grpc_request
    async def DeregisterModule(
        self, request: registration_pb2.DeregisterRequest, context
    ) -> registration_pb2.DeregisterResponse:
        """
        Deregisters a module by its ID.

        :param request: The deregistration request containing the module ID.
        :type request: registration_pb2.DeregisterRequest
        :param context: The gRPC context.
        :return: The deregistration response indicating success or failure.
        :rtype: registration_pb2.DeregisterResponse
        """
        if request.module_id in self.modules:
            del self.modules[request.module_id]
            return registration_pb2.DeregisterResponse(success=True)
        return registration_pb2.DeregisterResponse(success=False)

    @validate_grpc_request
    async def DiscoverModule(
        self, request: action_pb2.DiscoverRequest, context
    ) -> action_pb2.DiscoverResponse:
        """
        Discovers a module by its ID.

        :param request: The discovery request containing the module ID.
        :type request: action_pb2.DiscoverRequest
        :param context: The gRPC context.
        :return: The discovery response containing module details.
        :rtype: action_pb2.DiscoverResponse
        """
        module = self.modules.get(request.module_id, None)
        if module:
            return action_pb2.DiscoverResponse(
                module_type=module["type"],
                address=module["address"],
                port=module["port"],
                status=module["status"],
            )
        return action_pb2.DiscoverResponse()

    @validate_grpc_request
    async def UpdateModuleStatus(
        self, request: action_pb2.UpdateStatusRequest, context
    ) -> action_pb2.UpdateStatusResponse:
        """
        Updates the status of a module by its ID.

        :param request: The update status request containing the module ID and new status.
        :type request: action_pb2.UpdateStatusRequest
        :param context: The gRPC context.
        :return: The update status response indicating success or failure.
        :rtype: action_pb2.UpdateStatusResponse
        """
        if request.module_id in self.modules:
            self.modules[request.module_id]["status"] = request.status
            return action_pb2.UpdateStatusResponse(success=True)
        return action_pb2.UpdateStatusResponse(success=False)


class ModuleRegistryServer(GRPCServerBase):
    """
    ModuleRegistryServer for hosting the ModuleRegistry service.
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        Initializes the ModuleRegistryServer with the given port.

        :param port: The port number on which the server will listen.
        :type port: int
        """
        super().__init__(*args, **kwargs)

    def add_to_server(self, server) -> None:
        """
        Adds the ModuleRegistry service to the gRPC server.

        :param server: The gRPC server instance.
        """
        module_registry_pb2_grpc.add_ModuleRegistryServiceServicer_to_server(
            ModuleRegistry(), server
        )

"""TODO Module docstring."""

from typing import Type

import grpc

from proto.digitalkin.module.v1.module_service_pb2_grpc import (
    add_ModuleServiceServicer_to_server,
)
from proto.digitalkin.module_registry.v1.module_registry_service_pb2_grpc import (
    ModuleRegistryServiceStub,
)
from proto.digitalkin.module_registry.v1.registration_pb2 import (
    RegisterRequest,
    RegisterResponse,
    DeregisterRequest,
    DeregisterResponse,
)

from kin_sdk.agent_management._registry import ParamsModuleRegistry
from kin_sdk.agent_management._identity import ParamsModuleIdentity
from kin_sdk.agent_management.base import AgentManagement
from kin_sdk.agent_module._module.base import BaseModule
from kin_sdk.grpc_system.module_servicer import ModuleServicer
from kin_sdk.exception import ModuleRegistrationException
from kin_sdk.grpc_system.grpc_server_base import GRPCServerBase
from kin_sdk.common.logger import logger
from kin_sdk.certificates._certificates import init_channel_credentials


class ModuleServer(GRPCServerBase):
    """
    Base class for all specific module servers (Kin, Tool, Trigger).
    This class provides common functionalities for module registration.
    """

    def __init__(
        self,
        module_class: Type[BaseModule],
        module_id: str,
        module_address: str,
        module_port: int,
        registry_address: str,
        max_workers: int = 10,
    ):
        super().__init__(
            port=module_port,
            max_workers=max_workers,
        )
        self.module_class = module_class
        self.module_id = module_id
        self.module_address = module_address
        self.module_port = module_port
        self.module_type = module_class.get_type()
        self.registry_address = registry_address
        self._credentials = init_channel_credentials()
        self.agent_management = AgentManagement(
            params_identity=ParamsModuleIdentity(
                module_id=self.module_id,
                module_type=self.module_type,
                module_address=self.module_address,
                module_port=self.module_port,
            ),
            params_registry=ParamsModuleRegistry(
                module_id=self.module_id,
                registry_address=self.registry_address,
            ),
        )

    def _secure_channel(self, target: str) -> grpc.aio.Channel:
        """
        Creates a secure gRPC channel to the Module Registry.
        """
        return grpc.aio.insecure_channel(
            target=target
        )  # , credentials=self._credentials)

    async def _register_module(self) -> bool:
        """
        Registers the module with the Module Registry.

        Args:
            module_id (str): Unique identifier for the module.
            module_type (str): Type of the module (e.g., 'trigger', 'tool', 'kin').

        Returns:
            bool: True if registration is successful, False otherwise.
        """
        try:
            channel = self._secure_channel(self.registry_address)
            stub = ModuleRegistryServiceStub(channel)
            request = RegisterRequest(
                module_id=self.module_id,
                module_type=self.module_type.value,
                address=self.module_address,
                port=self.port,
            )
            response: RegisterResponse = await stub.RegisterModule(request)
            await channel.close()
            return response.success
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error registering module: %s", e)
            return False

    async def _deregister_module(self) -> bool:
        """
        Deregisters the module from the Module Registry.

        Returns:
            bool: True if deregistration is successful, False otherwise.
        """
        try:
            channel = self._secure_channel(self.registry_address)
            stub = ModuleRegistryServiceStub(channel)
            request = DeregisterRequest(module_id=self.module_id)
            response: DeregisterResponse = await stub.DeregisterModule(request)
            return response.success
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Error deregistering module: %s, -  %s", self.module_port, str(e)
            )
            return False

    def add_to_server(self, server: grpc.Server) -> None:
        """TODO: Sphinx docstring"""
        add_ModuleServiceServicer_to_server(
            ModuleServicer(
                module_class=self.module_class,
                agent_management=self.agent_management,
            ),
            server,
        )

    async def serve(self) -> None:
        """
        Starts the module server, binds it to the specified port, and waits for termination.

        The server runs indefinitely until an external interruption or termination.
        """
        try:
            has_been_registered = await self._register_module()
            if has_been_registered:
                await super().serve()
            else:
                raise ModuleRegistrationException("Module registration failed.")
        finally:
            await self._deregister_module()
            logger.info("Module deregistered.")

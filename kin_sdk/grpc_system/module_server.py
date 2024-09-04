"""TODO Module docstring."""

import json
from typing import Any, AsyncGenerator, Dict, List, Literal, Optional, Type, Union

import grpc
from google.protobuf import json_format, struct_pb2

from kin_sdk.agent_management.identity import ParamsModuleIdentity
from proto.digitalkin.module.v1.module_service_pb2_grpc import (
    ModuleServiceStub,
    add_ModuleServiceServicer_to_server,
)
from proto.digitalkin.module_registry.v1.module_registry_service_pb2_grpc import (
    ModuleRegistryServiceStub,
)
from proto.digitalkin.module_registry.v1.action_pb2 import DiscoverRequest
from proto.digitalkin.module_registry.v1.registration_pb2 import (
    RegisterRequest,
    RegisterResponse,
    DeregisterRequest,
    DeregisterResponse,
)
from proto.digitalkin.module.v1.information_pb2 import (
    GetModuleInputRequest,
    GetModuleInputResponse,
    GetModuleOutputRequest,
    GetModuleOutputResponse,
    GetModuleSetupRequest,
    GetModuleSetupResponse,
)
from proto.digitalkin.module.v1.lifecycle_pb2 import StartModuleRequest

from kin_sdk.agent_management.base import AgentManagement
from kin_sdk.agent_module._module.base import BaseModule
from kin_sdk.agent_module._module.module_servicer import ModuleServicer
from kin_sdk.exception import (
    ModuleRegistrationException,
)
from kin_sdk.grpc_system.models import ModuleModel
from kin_sdk.grpc_system.grpc_server_base import GRPCServerBase
from kin_sdk.common import (
    logger,
    ModuleType,
    get_certificates,
    Certificates,
    CertValues,
)


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
        self._credentials = self._init_credentials()
        self.agent_management = AgentManagement(
            params_identity=ParamsModuleIdentity(
                module_id=self.module_id,
                module_type=self.module_type,
                module_address=self.module_address,
                module_port=self.module_port,
            )
        )

    def _init_credentials(self) -> grpc.ChannelCredentials:
        """
        Initializes the gRPC channel credentials.
        """
        certificates: Certificates = get_certificates()
        server_cert: CertValues = certificates.client_cert

        return grpc.ssl_channel_credentials(
            root_certificates=server_cert.root_certificates,
            private_key=server_cert.private_key,
            certificate_chain=server_cert.certificate_chain,
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

    async def search_module(self, module_id: str) -> Optional[ModuleModel]:
        """
        Searches for a module in the Module Registry.
        TODO: improve it by adding parameters to search for a module.
        Args:
            module_id (str): Unique identifier for the module.

        Returns:
            ModuleModel: ModuleModel if the module is found, None otherwise.
        """
        try:
            channel = self._secure_channel(self.registry_address)
            stub = ModuleRegistryServiceStub(channel)
            request = DiscoverRequest(module_id=module_id)
            response = await stub.DiscoverModule(request)
            json_response = json_format.MessageToDict(
                response,
                preserving_proto_field_name=True,
            )
            module_model = {
                "module_id": module_id,
                "module_type": ModuleType[
                    json_response.get("module_type", "unknown").upper()
                ],
                "address": json_response.get("address", None),
                "port": json_response.get("port", None),
            }
            return ModuleModel.model_validate(module_model)
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error searching for module: %s", e)
            return None

    async def get_module_input(
        self, module_id: str, llm_format: bool = False
    ) -> Optional[dict]:
        """
        Get the input schema of a module.

        Args:
            module_id (str): Unique identifier for the module.

        Returns:
            bool: True if the module is found, False otherwise.
        """
        try:
            module_model: Union[ModuleModel, None] = await self.search_module(module_id)

            if module_model is None:
                raise ValueError(
                    f"The module: {module_id} is not found in the module registry"
                )

            channel = self._secure_channel(
                f"{module_model.address}:{module_model.port}"
            )
            stub = ModuleServiceStub(channel)
            request = GetModuleInputRequest(
                module_id=module_model.module_id,
                llm_format=llm_format,
            )
            response: GetModuleInputResponse = await stub.GetModuleInput(request)
            json_response = json_format.MessageToDict(
                response,
                preserving_proto_field_name=True,
            )
            return json_response.get("input_schema", {})
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error retreaving inputs for module %s: %s", module_id, str(e))
            return None

    async def get_module_output(
        self, module_id: str, llm_format: bool = False
    ) -> Optional[dict]:
        """
        Get the output schema of a module.

        Args:
            module_id (str): Unique identifier for the module.

        Returns:
            bool: True if the module is found, False otherwise.
        """
        try:
            module_model: Union[ModuleModel, None] = await self.search_module(module_id)

            if module_model is None:
                raise ValueError(
                    f"The module: {module_id} is not found in the module registry"
                )

            channel = self._secure_channel(
                f"{module_model.address}:{module_model.port}"
            )
            stub = ModuleServiceStub(channel)
            request = GetModuleOutputRequest(
                module_id=module_model.module_id,
                llm_format=llm_format,
            )
            response: GetModuleOutputResponse = await stub.GetModuleOutput(request)
            json_response = json_format.MessageToDict(
                response,
                preserving_proto_field_name=True,
            )
            return json_response.get("output_schema", {})
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Error retreaving outputs for module %s: %s", module_id, str(e)
            )
            return None

    async def get_module_setup(
        self, module_id: str, llm_format: bool = False
    ) -> Optional[dict]:
        """
        Get the setup schema of a module.

        Args:
            module_id (str): Unique identifier for the module.

        Returns:
            bool: True if the module is found, False otherwise.
        """
        try:
            module_model: Union[ModuleModel, None] = await self.search_module(module_id)

            if module_model is None:
                raise ValueError(
                    f"The module: {module_id} is not found in the module registry"
                )

            channel = self._secure_channel(
                f"{module_model.address}:{module_model.port}"
            )
            stub = ModuleServiceStub(channel)
            request = GetModuleSetupRequest(
                module_id=module_model.module_id,
                llm_format=llm_format,
            )
            response: GetModuleSetupResponse = await stub.GetModuleSetup(request)
            json_response = json_format.MessageToDict(
                response,
                preserving_proto_field_name=True,
            )
            return json_response.get("setup_schema", {})
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error retreaving setups for module %s: %s", module_id, str(e))
            return None

    async def start_module(
        self,
        module_id: str,
        input_data: Dict[str, Any],
        setup_id: str,
        module_ids: Optional[List[str]] = None,
        request_type: str = "SEND",
        module_role: Literal["owner", "member"] = "owner",
    ) -> AsyncGenerator[Optional[dict], None]:
        """
        Get the input of a module.

        Args:
            module_id (str): Unique identifier for the module.

        Returns:
            bool: True if the module is found, False otherwise.
        """
        try:
            module_model: Union[ModuleModel, None] = await self.search_module(module_id)

            if module_model is None:
                raise ValueError(
                    f"The module: {module_id} is not found in the module registry"
                )
            channel = self._secure_channel(
                f"{module_model.address}:{module_model.port}"
            )
            stub = ModuleServiceStub(channel)
            request = StartModuleRequest(
                input=json_format.Parse(
                    text=json.dumps(input_data),
                    message=struct_pb2.Struct(),  # pylint: disable=no-member
                    ignore_unknown_fields=True,
                ),
                setup_id=setup_id,
                module_ids=[] if module_ids is None else module_ids,
                request_type=request_type,
            )
            metadata = [
                ("module_id", self.module_id),
                ("module_role", module_role),
            ]
            response_iterator = await stub.StartModule(
                iter([request]), metadata=metadata
            )
            for response in response_iterator:
                json_response = json_format.MessageToDict(
                    response,
                    preserving_proto_field_name=True,
                )
                yield json_response
        except Exception as e:  # pylint: disable=broad-except
            logger.error(
                "Error starting new module for module %s: %s", module_id, str(e)
            )
            yield None

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

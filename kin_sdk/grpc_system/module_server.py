"""TODO Module docstring."""

import json
from typing import Any, Dict, Generator, List, Literal, Type, Optional, Union

import grpc
from google.protobuf import json_format, struct_pb2

from proto.digitalkin.module.v1.module_service_pb2_grpc import ModuleServiceStub
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
)
from proto.digitalkin.module.v1.lifecycle_pb2 import StartModuleRequest

from kin_sdk.exception import (
    ModuleNotFoundException,
    ModuleDeregistrationException,
    ModuleRegistrationException,
)
from kin_sdk.grpc_system.models import ModuleModel
from kin_sdk.grpc_system.grpc_server_base import GRPCServerBase
from kin_sdk.common import logger, ModuleType


class ModuleServer(GRPCServerBase):
    """
    Base class for all specific module servers (Kin, Tool, Trigger).
    This class provides common functionalities for module registration.
    """

    def __init__(
        self,
        module_id: str,
        module_address: str,
        module_port: int,
        module_type: ModuleType,
        registry_address: str,
        servicer_class: Type,
        servicer_args: tuple = (),
        servicer_kwargs: dict = {},
        max_workers: int = 10,
    ):
        super().__init__(
            servicer_class=servicer_class,  # type: ignore
            port=module_port,
            servicer_args=servicer_args,
            servicer_kwargs=servicer_kwargs,
            max_workers=max_workers,
        )

        self.module_id = module_id
        self.module_address = module_address
        self.module_port = module_port
        self.module_type = module_type
        self.registry_address = registry_address

    def register_module(self) -> bool:
        """
        Registers the module with the Module Registry.

        Args:
            module_id (str): Unique identifier for the module.
            module_type (str): Type of the module (e.g., 'trigger', 'tool', 'kin').

        Returns:
            bool: True if registration is successful, False otherwise.
        """
        with grpc.insecure_channel(self.registry_address) as channel:
            stub = ModuleRegistryServiceStub(channel)
            request = RegisterRequest(
                module_id=self.module_id,
                module_type=self.module_type.value,
                address=self.module_address,
                port=self.port,
            )
            response: RegisterResponse = stub.RegisterModule(request)
            return response.success

    def search_module(self, module_id: str) -> Optional[ModuleModel]:
        """
        Searches for a module in the Module Registry.

        Args:
            module_id (str): Unique identifier for the module.

        Returns:
            ModuleModel: ModuleModel if the module is found, None otherwise.
        """
        try:
            with grpc.insecure_channel(self.registry_address) as channel:
                stub = ModuleRegistryServiceStub(channel)
                request = DiscoverRequest(module_id=module_id)
                response = stub.DiscoverModule(request)
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
        except ModuleNotFoundException as e:
            logger.error("Error searching for module: %s", e)
            return None
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error searching for module: %s", e)
            return None

    def deregister_module(self) -> bool:
        """
        Deregisters the module from the Module Registry.

        Returns:
            bool: True if deregistration is successful, False otherwise.
        """
        try:
            with grpc.insecure_channel(self.registry_address) as channel:
                stub = ModuleRegistryServiceStub(channel)
                request = DeregisterRequest(module_id=self.module_id)
                response: DeregisterResponse = stub.DeregisterModule(request)
                return response.success
        except ModuleDeregistrationException:
            logger.error("Error deregistering module: %s", self.module_port)
            return False

    def execute_module(self, module_id: str, input_data: dict) -> Optional[dict]:
        """TODO: Implement this method."""
        raise NotImplementedError

    def get_module_input(
        self, module_id: str, llm_format: bool = False
    ) -> Optional[dict]:
        """
        Get the input of a module.

        Args:
            module_id (str): Unique identifier for the module.

        Returns:
            bool: True if the module is found, False otherwise.
        """
        try:
            module_model: Union[ModuleModel, None] = self.search_module(module_id)

            if module_model is None:
                raise ValueError(
                    f"The module: {module_id} is not found in the module registry"
                )

            with grpc.insecure_channel(
                f"{module_model.address}:{module_model.port}"
            ) as channel:
                stub = ModuleServiceStub(channel)
                request = GetModuleInputRequest(
                    module_id=module_model.module_id,
                    llm_format=llm_format,
                )
                response: GetModuleInputResponse = stub.GetModuleInput(request)
                json_response = json_format.MessageToDict(
                    response,
                    preserving_proto_field_name=True,
                )
                return json_response.get("input_schema", {})
        except ModuleNotFoundException as e:
            logger.error("Error retreaving inputs for module %s: %s", module_id, e)
            return None

    def start_module(
        self,
        module_id: str,
        input: Dict[str, Any],
        setup_id: str,
        module_ids: List[str] = [],
        request_type: str = "SEND",
        module_role: Literal["owner", "member"] = "owner",
    ) -> Generator[None, None, Optional[dict]]:
        """
        Get the input of a module.

        Args:
            module_id (str): Unique identifier for the module.

        Returns:
            bool: True if the module is found, False otherwise.
        """
        try:
            module_model: Union[ModuleModel, None] = self.search_module(module_id)
            logger.info(module_model)
            if module_model is None:
                raise ValueError(
                    f"The module: {module_id} is not found in the module registry"
                )

            with grpc.insecure_channel(
                f"{module_model.address}:{module_model.port}"
            ) as channel:
                stub = ModuleServiceStub(channel)
                request = StartModuleRequest(
                    input=json_format.Parse(
                        text=json.dumps(input),
                        message=struct_pb2.Struct(),  # pylint: disable=no-member
                        ignore_unknown_fields=True,
                    ),
                    setup_id=setup_id,
                    module_ids=module_ids,
                    request_type=request_type,
                )
                logger.info("request: %s", request)
                metadata = [
                    ("module_id", self.module_id),
                    ("module_role", module_role),
                ]
                response_iterator = stub.StartModule(iter([request]), metadata=metadata)
                for response in response_iterator:
                    json_response = json_format.MessageToDict(
                        response,
                        preserving_proto_field_name=True,
                    )
                    yield json_response
        except ModuleNotFoundException as e:
            logger.error("Error starting new module for module %s: %s", module_id, e)
            yield None

    def serve(self) -> None:
        """
        Starts the module server, binds it to the specified port, and waits for termination.

        The server runs indefinitely until an external interruption or termination.
        """
        try:
            if self.register_module():
                super().serve()
            else:
                raise ModuleRegistrationException("Module registration failed.")
        finally:
            self.deregister_module()
            print("Module deregistered.")

"""
TODO: sphinx documentation
"""

from dataclasses import dataclass
import json
from typing import Any, AsyncGenerator, Dict, List, Literal, Optional, Union

import grpc
from google.protobuf import json_format, struct_pb2

from proto.digitalkin.module.v1.module_service_pb2_grpc import (
    ModuleServiceStub,
)
from proto.digitalkin.module_registry.v1.action_pb2 import DiscoverRequest
from proto.digitalkin.module_registry.v1.module_registry_service_pb2_grpc import (
    ModuleRegistryServiceStub,
)
from proto.digitalkin.module.v1.lifecycle_pb2 import StartModuleRequest
from proto.digitalkin.module.v1.information_pb2 import (
    GetModuleInputRequest,
    GetModuleInputResponse,
    GetModuleOutputRequest,
    GetModuleOutputResponse,
    GetModuleSetupRequest,
    GetModuleSetupResponse,
)
from kin_sdk.models.module import ModuleModel
from kin_sdk.common.logger import logger
from kin_sdk.common.types import ModuleType
from kin_sdk.certificates._certificates import init_channel_credentials


@dataclass
class ParamsModuleRegistry:
    """
    The ParamsModuleRegistry class represents the parameters required to create a ModuleRegistry object.
    """

    registry_address: str
    module_id: str


class ModuleRegistry:
    """
    The ModuleRegistry class allow communication with other module, this a registry adresse.
    """

    def __init__(
        self,
        registry_address: str,
        module_id: str,
    ):
        """
        Initializes the ModuleRegistry object with the given details.
        """
        self._module_id = module_id
        self._registry_address = registry_address
        self._credentials = init_channel_credentials()

    @classmethod
    def from_params(cls, params: ParamsModuleRegistry) -> "ModuleRegistry":
        """
        Creates a ModuleRegistry object from the given parameters.
        """
        return cls(**params.__dict__)

    def _secure_channel(self, target: str) -> grpc.aio.Channel:
        """
        Creates a secure gRPC channel to the Module Registry.
        """
        return grpc.aio.insecure_channel(
            target=target
        )  # , credentials=self._credentials)

    async def find_module_by_id(self, module_id: str) -> Optional[ModuleModel]:
        """
        Searches for a module in the Module Registry.
        TODO: improve it by adding parameters to search for a module.
        Args:
            module_id (str): Unique identifier for the module.

        Returns:
            ModuleModel: ModuleModel if the module is found, None otherwise.
        """
        try:
            channel = self._secure_channel(self._registry_address)
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
            module_model: Union[ModuleModel, None] = await self.find_module_by_id(
                module_id
            )

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
            module_model: Union[ModuleModel, None] = await self.find_module_by_id(
                module_id
            )

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
            module_model: Union[ModuleModel, None] = await self.find_module_by_id(
                module_id
            )

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
            module_model: Union[ModuleModel, None] = await self.find_module_by_id(
                module_id
            )

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
                ("module_id", self._module_id),
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

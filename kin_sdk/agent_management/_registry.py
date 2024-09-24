"""
This module contains the ModuleRegistry class, which allows communication with other modules.
The ModuleRegistry class is used to search for modules in the Module Registry, and to get the input, output, and setup schemas of a module.
The ModuleRegistry class also allows
- to start a new module with the given input data,
- to get the input data of a module,
- to get the output data of a module,
- to get the setup data of a module.
"""

from dataclasses import dataclass
import json
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

import grpc
from google.protobuf import json_format, struct_pb2

from digitalkin.module.v1.module_service_pb2_grpc import (
    ModuleServiceStub,
)
from digitalkin.module_registry.v1.action_pb2 import DiscoverRequest
from digitalkin.module_registry.v1.module_registry_service_pb2_grpc import (
    ModuleRegistryServiceStub,
)
from digitalkin.module.v1.lifecycle_pb2 import (
    ConnectionRequest,
    StartModuleRequest,
    InputDataRequest,
)
from digitalkin.module.v1.information_pb2 import (
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
        messages: List[Dict[str, Dict[str, Any]]],
    ) -> AsyncGenerator[Optional[dict], None]:
        """
        Get the input of a module.

        Args:
            module_id (str): Unique identifier for the module.
            messages (List[Dict[str, Dict[str, Any]]]): List of messages to send to the module.

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
            requests = []
            for message in messages:
                message_type, message_value = list(message.items())[0]

                if message_type == "connection_request":
                    request = StartModuleRequest(
                        request_type=message_value.get(
                            "request_type", "REQUEST_TYPE_UNKNOWN"
                        ),
                        connection_request=ConnectionRequest(
                            module_id=self._module_id,
                            module_role=message_value.get(
                                "module_role", "MODULE_ROLE_UNKNOWN"
                            ),
                        ),
                    )
                elif message_type == "input_request":
                    request = StartModuleRequest(
                        request_type=message_value.get(
                            "request_type", "REQUEST_TYPE_UNKNOWN"
                        ),
                        input_request=InputDataRequest(
                            module_ids=message_value.get("module_ids", []),
                            setup_id=message_value.get("setup_id", None),
                            input=json_format.Parse(
                                text=json.dumps(message_value.get("input_data", {})),
                                message=struct_pb2.Struct(),  # pylint: disable=no-member
                                ignore_unknown_fields=True,
                            ),
                        ),
                    )
                else:
                    raise ValueError("The message is not recognized")
                requests.append(request)

            response_iterator = stub.StartModule(iter(requests))  # , metadata=metadata)
            async for response in response_iterator:
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

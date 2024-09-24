"""
TODO: sphinx docstring
"""

import json
import inspect
from abc import ABC, abstractmethod
from typing import Awaitable, Literal, Type, TypeVar, Generic, List, Callable, Union

import grpc
from pydantic import BaseModel
from google.protobuf import json_format, struct_pb2

# from digitalkin.module.v1.module_service_pb2_grpc import (
#     ModuleServiceStub,
# )
# from digitalkin.module.v1.lifecycle_pb2 import StartModuleRequest
from kin_sdk.models.module import ModuleModel
from kin_sdk.agent_management.base import AgentManagement
from kin_sdk.agent_management._database import ModuleDatabase
from kin_sdk.agent_management._identity import ModuleIdentity
from kin_sdk.agent_management._registry import ModuleRegistry
from kin_sdk.common.types import ModuleType
from kin_sdk.common.logger import logger

InputModelT = TypeVar("InputModelT", bound=BaseModel)
OutputModelT = TypeVar("OutputModelT", bound=BaseModel)
SetupModelT = TypeVar("SetupModelT", bound=BaseModel)


class BaseModule(Generic[InputModelT, OutputModelT, SetupModelT], ABC):
    """
    Abstract base class for defining a module.
    """

    name: str
    description: str
    input_format: Type[InputModelT]
    output_format: Type[OutputModelT]
    setup_format: Type[SetupModelT]
    _module_type: ModuleType

    def __init__(
        self,
        agent_management: AgentManagement,
    ):
        """
        Initializes the BaseModule.

        :param agent_management: The agent management object.
        """
        self._agent_management = agent_management

    @property
    def identity(self) -> ModuleIdentity:
        """
        Gets the module identity.

        :return: The module identity.
        """
        return self._agent_management.identity

    @property
    def registry(self) -> ModuleRegistry:
        """
        Gets the module identity.

        :return: The module identity.
        """
        return self._agent_management.registry

    @property
    def database(self) -> ModuleDatabase:
        """
        Gets the module database.

        :return: The module database.
        """
        return self._agent_management.database

    @classmethod
    def validate_format(
        cls,
        data: dict,
        data_format: Literal["input", "output", "setup"],
    ) -> Union[InputModelT, OutputModelT, SetupModelT]:
        """
        Validates the input data.

        :param model: The model to validate.
        :param data: The data to validate.
        :return: The validated input data.
        """
        try:
            if data_format == "input":
                return cls.input_format.model_validate(data)
            if data_format == "output":
                return cls.output_format.model_validate(data)
            if data_format == "setup":
                return cls.setup_format.model_validate(data)
        except Exception as e:
            raise ValueError(f"Invalid model '{data_format}' : {str(e)}") from e

    def __init_subclass__(cls, **kwargs):
        """
        Ensures that subclasses define required attributes.
        """
        super().__init_subclass__(**kwargs)
        if not inspect.isabstract(cls):
            required_attrs = [
                "name",
                "description",
                "input_format",
                "output_format",
                "setup_format",
            ]
            for attr in required_attrs:
                if not hasattr(cls, attr) or getattr(cls, attr) is None:
                    raise TypeError(
                        f"Subclass '{cls.__name__}' must define a '{attr}' class variable."
                    )

    @classmethod
    def get_name(cls) -> str:
        """
        Get the name of the tool.

        :return: The name of the tool.
        :raises NotImplementedError: If the `name` is not defined.
        """
        if cls.name is not None:
            return cls.name
        raise NotImplementedError(f"'{cls.__name__}' class does not define a 'role'.")

    @classmethod
    def get_description(cls) -> str:
        """
        Gets the name of the tool.

        :return: The name of the tool.
        :raises NotImplementedError: If the `name` is not defined.
        """
        if cls.description is not None:
            return cls.description
        raise NotImplementedError(
            f"'{cls.__name__}' class does not define a 'description'."
        )

    @classmethod
    def get_type(cls) -> ModuleType:
        """
        Gets the type of the module.

        :return: The type of the module.
        :raises NotImplementedError: If the `type` is not defined.
        """
        if cls._module_type is not None:
            return cls._module_type
        raise NotImplementedError(
            f"'{cls.__name__}' class does not define a 'module type'."
        )

    @classmethod
    def __args_schema(cls, model: BaseModel):
        """
        Get the JSON schema of the model.
        """
        schema = model.model_json_schema()
        if "title" in schema:
            del schema["title"]
        if "description" in schema:
            del schema["description"]
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": schema,
        }

    @classmethod
    def get_input_format(cls, llm_format: bool = False) -> str:
        """
        Get the JSON schema of the input format model.

        :return: The JSON schema of the input format as a string.
        :raises NotImplementedError: If the `input_format` is not defined.
        """
        if cls.output_format is not None:
            if llm_format:
                return json.dumps(cls.__args_schema(cls.input_format), indent=2)
            return json.dumps(cls.input_format.model_json_schema(), indent=2)
        raise NotImplementedError(
            f"'{cls.__name__}' class does not define an 'input_format'."
        )

    @classmethod
    def get_output_format(cls, llm_format: bool = False) -> str:
        """
        Get the JSON schema of the output format model.

        :return: The JSON schema of the output format as a string.
        :raises NotImplementedError: If the `output_format` is not defined.
        """
        if cls.output_format is not None:
            if llm_format:
                return json.dumps(cls.__args_schema(cls.output_format), indent=2)
            return json.dumps(cls.output_format.model_json_schema(), indent=2)
        raise NotImplementedError(
            f"'{cls.__name__}' class does not define an 'output_format'."
        )

    @classmethod
    def get_setup_format(cls, llm_format: bool = False) -> str:
        """
        Gets the JSON schema of the setup format model.

        :return: The JSON schema of the setup format as a string.
        :raises NotImplementedError: If the `setup_format` is not defined.
        """
        if cls.setup_format is not None:
            if llm_format:
                return json.dumps(cls.__args_schema(cls.setup_format), indent=2)
            return json.dumps(cls.setup_format.model_json_schema(), indent=2)
        raise NotImplementedError(
            f"'{cls.__name__}' class does not define an 'setup_format'."
        )

    @abstractmethod
    async def start(self, setup_id: str) -> None:
        """
        Starts the module.
        """
        raise NotImplementedError("Subclasses must implement 'start' abstract method")

    @abstractmethod
    async def execute(
        self,
        input_data: InputModelT,
        setup_id: str,
        callback: Callable[[OutputModelT], Awaitable[None]],
    ) -> None:
        """
        Executes the module.

        :param input_data: The input data for the module.
        :param setup_data: The setup data for the module.
        :param callback: The callback to call with the output data.
        """
        raise NotImplementedError("Subclasses must implement 'execute' abstract method")

    @abstractmethod
    async def stop(self) -> None:  # ? Other params like module_id ?
        """
        Stops the module.
        """
        raise NotImplementedError("Subclasses must implement 'stop' abstract method")

    async def send_output(self, output: OutputModelT, module_ids: List[str]) -> None:
        """
        Sends the output to the list of gRPC modules.

        :param output: The output data to send.
        :param module_ids: The list of module IDs to send the output to.
        """
        # Check if module_ids is None or empty, in which case we don't send the output
        if module_ids is None or len(module_ids) == 0:
            return

        try:
            if not isinstance(output, self.output_format):
                raise TypeError(
                    f"Output must be of type '{self.output_format.__name__}', not '{type(output).__name__}'."
                )

            # Validate and serialize the output using the output_format Pydantic model
            output_data = self.output_format.model_validate(
                output.model_dump()
            ).model_dump()

            # Convert in gRPC Struct proto format the output data in order to send it as input of a block
            struct_input = (  # pylint: disable=unused-variable # noqa
                json_format.ParseDict(
                    output_data, struct_pb2.Struct()  # pylint: disable=no-member
                )
            )

            # use module_ids to send the output to the right module
            for module_id in module_ids:
                module = await self.registry.find_module_by_id(module_id)
                module = None
                if module is None:
                    return None

                logger.info("Module found: \n\t%s", module)

                # Send the result to the list of gRPC modules
                async with grpc.aio.insecure_channel(  # ! TODO replace with secure_channel
                    f"{module.address}:{module.port}"
                ) as channel:  # pylint: disable=unused-variable # noqa
                    raise Exception(  # pylint: disable=broad-exception-raised # noqa
                        "Not implemented"
                    )
                    # stub = ModuleServiceStub(channel)
                    # request = StartModuleRequest(
                    #     input=struct_input,
                    #     setup_id="I don't know what to put here",  # ! TODO: What to put here?
                    #     module_ids=[],  # ! TODO: What to put here?
                    # )
                    # await stub.StartModule(request)  # ! TODO not streaming response
                    # logger.info(
                    #     "📞 Output sent to Tool module %s \n\t%s", module_id, module
                    # )
        except grpc.aio.AioRpcError as e:
            if not isinstance(module, ModuleModel):
                message = "😵 Error sending output to none existing module:\n\t"
            else:
                # Handle gRPC exceptions
                message = f"😵 Error sending output to {self.identity.type} module {module_id}:\n\t"
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                message += "- Server is unavailable"
            elif e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                message += "- Deadline exceeded"
            elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                message += f"- Invalid argument provided: \n\t - {e.details()}"
            else:
                message += f"An error occurred: {e.details()} (code: {e.code()})"
            logger.error(message)
        except Exception as e:
            logger.error("Exception during send_output: %s", e)
            raise RuntimeError(str(e)) from e

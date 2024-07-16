"""
TODO: sphinx docstring
"""

import json
import inspect
from abc import ABC, abstractmethod
from typing import Type, TypeVar, Generic, List, Callable

import grpc
from pydantic import BaseModel
from google.protobuf import json_format, struct_pb2

import kin_sdk.service.service as service
import proto.digitalkin.service.v1.service_pb2 as service_pb2
import proto.digitalkin.service.v1.service_pb2_grpc as service_pb2_grpc
from kin_sdk.grpc_services import ServiceServer, ServiceModel
from kin_sdk.common import ServiceType, logger

InputModelT = TypeVar("InputModelT", bound=BaseModel)
OutputModelT = TypeVar("OutputModelT", bound=BaseModel)
SetupModelT = TypeVar("SetupModelT", bound=BaseModel)


class BaseService(Generic[InputModelT, OutputModelT, SetupModelT], ServiceServer, ABC):
    """
    Abstract base class for defining a trigger.
    """

    name: str
    description: str
    input_format: Type[InputModelT]
    output_format: Type[OutputModelT]
    setup_format: Type[SetupModelT]

    def __init__(
        self,
        service_id: str,
        service_address: str,
        service_port: int,
        service_type: ServiceType,
        registry_address: str,
        max_workers: int = 10,
    ):
        """
        Initializes the BaseTrigger.

        :param service_id: The ID of the service.
        :param service_address: The address of the service.
        :param service_port: The port of the service.
        :param service_type: The type of the service.
        :param registry_address: The address of the registry.
        :param max_workers: The maximum number of worker threads.
        """
        self.max_workers = max_workers
        super().__init__(
            service_id=service_id,
            service_address=service_address,
            service_port=service_port,
            service_type=service_type,
            servicer_class=service.Service,
            servicer_kwargs=dict(
                service=self,
            ),
            registry_address=registry_address,
            max_workers=max_workers,
        )

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
    def start(self) -> None:  # ? other params like service_id ?
        """
        Starts the service.
        """
        raise NotImplementedError("Subclasses must implement 'start' abstract method")

    @abstractmethod
    def execute(
        self,
        input_data: InputModelT,
        setup_data: SetupModelT,  # ? SetupModelT  or setup_id ?
        callback: Callable[[OutputModelT], None],
    ) -> None:
        """
        Executes the trigger.

        :param input_data: The input data for the trigger.
        :param setup_data: The setup data for the trigger.
        :param callback: The callback to call with the output data.
        """
        raise NotImplementedError("Subclasses must implement 'execute' abstract method")

    @abstractmethod
    def stop(self) -> None:  # ? Other params like service_id ?
        """
        Stops the trigger.
        """
        raise NotImplementedError("Subclasses must implement 'stop' abstract method")

    def send_output(self, output: OutputModelT, service_ids: List[str]) -> None:
        """
        Sends the output to the list of gRPC services.

        :param output: The output data to send.
        :param service_ids: The list of service IDs to send the output to.
        """
        # Check if service_ids is None or empty, in which case we don't send the output
        if service_ids is None or len(service_ids) == 0:
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
            struct_input = json_format.ParseDict(output_data, struct_pb2.Struct())

            # use service_ids to send the output to the right service
            for service_id in service_ids:
                service: ServiceModel = self.search_service(service_id)
                logger.info(f"Service found: \n\t{service}")

                # Send the result to the list of gRPC services
                with grpc.insecure_channel(
                    f"{service.address}:{service.port}"
                ) as channel:
                    stub = service_pb2_grpc.ServiceStub(channel)
                    request = service_pb2.StartServiceRequest(
                        input=struct_input,
                        setup_id="I don't know what to put here",  # TODO: What to put here?
                        service_ids=[],  # TODO: What to put here?
                    )
                    stub.ExecuteTool(request)
                    logger.info(
                        f"📞 Output sent to Tool service {service_id} \n\t{service}"
                    )
        except grpc.RpcError as e:
            # Handle gRPC exceptions
            message = f"😵 Error sending output to {service.service_type} service {service_id}:\n\t"
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
            raise Exception(str(e))

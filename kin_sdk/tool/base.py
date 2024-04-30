"""
This module defines the abstract base class `BaseTool` and the `ResponseModel`.

`BaseTool` serves as a template for creating different types of tools, each representing
a functional unit within the system that performs a specific task. It enforces
the implementation of core methods and structures that all tools must adhere to.

`ResponseModel` is a Pydantic model that standardizes the response structure from a tool's
execution, providing a consistent interface for success or error communication.

Classes:
    BaseTool: An abstract generic class that defines the interface and common behavior for all tools.
    ResponseModel: A model used for formulating standard responses from tools.

The module also provides helper methods for accessing the schema information of the input
and output data models associated with a tool, and a protected `_run` method that handles
the execution flow and response generation for a tool.

Subclasses of `BaseTool` must define their own `role`, `description`, `input_format`,
`output_format`, and implement the `execute` method, which contains the tool's main logic.

Example:
    class MyTool(BaseTool[MyInputModel, MyOutputModel]):
        role = 'my_role'
        description = 'Description of MyTool'
        input_format = MyInputModel
        output_format = MyOutputModel

        def execute(self, input_data: MyInputModel) -> MyOutputModel:
            # Tool-specific logic here
            pass

Usage:
    # Instantiate a tool subclass and execute with valid input data
    my_tool = MyTool()
    result = my_tool.execute(valid_input_data)
"""

import json
import inspect
import threading
from enum import Enum
from abc import ABC, abstractmethod
from typing import Type, TypeVar, Generic, Dict, Any, Union

from opentelemetry import trace
from pydantic import BaseModel, ValidationError
from google.protobuf import json_format, struct_pb2

import grpc
import proto.digitalkin.service.v1.tool.tool_service_pb2 as tool_service_pb2
import proto.digitalkin.service.v1.tool.tool_service_pb2_grpc as tool_service_pb2_grpc

from kin_sdk.common import (
    validate_stream_grpc_request,
    logger,
    pydantic_validation_error,
)
from kin_sdk.grpc_services import ServiceServer

InputModelT = TypeVar("InputModelT", bound=BaseModel)
OutputModelT = TypeVar("OutputModelT", bound=BaseModel)


class ResponseType(str, Enum):
    ERROR = "error"
    SUCCESS = "success"


class ResponseModel(BaseModel):
    type: ResponseType
    content: str


class ToolService(tool_service_pb2_grpc.ToolServiceServicer):
    def __init__(self, tool: "BaseTool"):
        self.tool = tool
        self.tracer = trace.get_tracer(self.tool.__class__.__name__)

        self.rooms: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    @validate_stream_grpc_request()
    def ExecuteTool(
        self,
        request: Union[tool_service_pb2.ExecuteRequest, struct_pb2.Struct],
        context: grpc.ServicerContext,
    ):
        with self.tracer.start_span("execute_tool"):
            try:
                # Extract service name from metadata
                json_request = json_format.MessageToDict(
                    request, preserving_proto_field_name=True
                )
                partial_request = json_request.get("partial_request", False)
                if partial_request:
                    # Send the response
                    context.set_code(grpc.StatusCode.OK)
                    context.set_details("Success")
                    return tool_service_pb2.ExecuteResponse(
                        success=True,
                        output=json_format.ParseDict(
                            {"message": "partial_request has been received."},
                            struct_pb2.Struct(),
                        ),
                    )

                input = json_request.get("input", None)
                if input is None:
                    raise ValueError("Input data is missing.")

                # Parse and validate the input JSON using the input_format Pydantic model
                input_data = self.tool.input_format.model_validate(input)

                # Call the user-defined run method and get the output data
                output_data = self.tool.execute(input_data)

                # Validate and serialize the output using the output_format Pydantic model
                output_data = self.tool.output_format(
                    **output_data.model_dump()
                ).model_dump()

                # Reconvert in gRPC Struct proto format the output data
                struct_response = json_format.ParseDict(
                    output_data, struct_pb2.Struct()
                )

                # Send the response
                context.set_code(grpc.StatusCode.OK)
                context.set_details("Success")
                return tool_service_pb2.ExecuteResponse(
                    success=True, output=struct_response
                )
            except ValidationError as e:
                error_message = pydantic_validation_error(e, context)
                logger.error(error_message)  # Validation Error
                # Reconvert in gRPC Struct proto format the output data
                struct_response = json_format.ParseDict(
                    {"message": error_message},
                    struct_pb2.Struct(),
                )
                return tool_service_pb2.ExecuteResponse(
                    success=False, output=struct_response
                )
            except Exception as e:
                logger.error("Exception Error: %s", e)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))

                # Reconvert in gRPC Struct proto format the output data
                struct_response = json_format.ParseDict(
                    {"message": str(e)}, struct_pb2.Struct()
                )
                return tool_service_pb2.ExecuteResponse(
                    success=False, output=struct_response
                )

    def add_to_server(self, server: grpc.Server) -> None:
        tool_service_pb2_grpc.add_ToolServiceServicer_to_server(self, server)


class BaseTool(Generic[InputModelT, OutputModelT], ServiceServer, ABC):
    name: str
    description: str
    input_format: Type[InputModelT]
    output_format: Type[OutputModelT]

    def __init__(
        self,
        service_id: str,
        service_address: str,
        service_port: int,
        registry_address: str,
        max_workers: int = 10,
    ):
        self.registry_address = registry_address
        self.max_workers = max_workers
        super().__init__(
            service_id=service_id,
            service_address=service_address,
            service_port=service_port,
            service_type="tool",
            servicer_class=ToolService,
            servicer_kwargs=dict(tool=self),
            registry_address=registry_address,
            max_workers=max_workers,
        )

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not inspect.isabstract(cls):
            required_attrs = ["name", "description", "input_format", "output_format"]
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
        Get the description of the cell.

        :return: The description of the cell.
        :raises NotImplementedError: If the `description` is not defined.
        """
        if cls.description is not None:
            return cls.description
        raise NotImplementedError(
            f"'{cls.__name__}' class does not define a 'description'."
        )

    @classmethod
    def get_input_format(cls) -> str:
        """
        Get the JSON schema of the input format model.

        :return: The JSON schema of the input format as a string.
        :raises NotImplementedError: If the `input_format` is not defined.
        """
        if cls.input_format is not None:
            return json.dumps(cls.input_format.model_json_schema(), indent=2)
        raise NotImplementedError(
            f"'{cls.__name__}' class does not define an 'input_format'."
        )

    @classmethod
    def get_output_format(cls) -> str:
        """
        Get the JSON schema of the output format model.

        :return: The JSON schema of the output format as a string.
        :raises NotImplementedError: If the `output_format` is not defined.
        """
        if cls.output_format is not None:
            return json.dumps(cls.output_format.model_json_schema(), indent=2)
        raise NotImplementedError(
            f"'{cls.__name__}' class does not define an 'output_format'."
        )

    @abstractmethod
    def execute(self, input_data: InputModelT) -> OutputModelT:
        """
        Process the input data and produce output.
        This method must be implemented by all subclasses.
        """
        raise NotImplementedError("Subclasses must implement 'execute' abstract method")

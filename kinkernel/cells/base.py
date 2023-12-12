"""
This module defines the abstract base class `BaseCell` and the `ResponseModel`.

`BaseCell` serves as a template for creating different types of cells, each representing
an autonomous agent with a specific role and behavior within the system. It enforces
the implementation of core methods and structures that all cells must adhere to.

`ResponseModel` is a Pydantic model that standardizes the response structure from a cell's
execution, providing a consistent interface for success or error communication.

Classes:
    BaseCell: An abstract generic class that defines the interface and common behavior for all cells.
    ResponseModel: A model used for formulating standard responses from cells.

The module also provides helper methods for accessing the schema information of the input
and output data models associated with a cell, and a protected `_run` method that handles
the execution flow and response generation for a cell.

Subclasses of `BaseCell` must define their own `role`, `description`, `input_format`,
`output_format`, and implement the `execute` method, which contains the cell's main logic.

Example:
    class MyCell(BaseCell[MyInputModel, MyOutputModel]):
        role = 'my_role'
        description = 'Description of MyCell'
        input_format = MyInputModel
        output_format = MyOutputModel

        def execute(self, input_data: MyInputModel) -> MyOutputModel:
            # Cell-specific logic here
            pass

Usage:
    # Instantiate a cell subclass and execute with valid input data
    my_cell = MyCell()
    result = my_cell.execute(valid_input_data)
"""
import json
import inspect
import asyncio
from enum import Enum
from abc import ABC, abstractmethod
from typing import Type, TypeVar, Generic, Optional

from opentelemetry import trace
from pydantic import BaseModel, ValidationError

from kinkernel.config import ConfigModel


# Create a type variable that can be used for input and output models
InputModelT = TypeVar("InputModelT", bound=BaseModel)
OutputModelT = TypeVar("OutputModelT", bound=BaseModel)


class ResponseType(str, Enum):
    """
    An enumeration for response types.

    :param ERROR (str): Represents an error response.
    :param SUCCESS (str): Represents a successful response.
    """

    ERROR = "error"
    SUCCESS = "success"


class ResponseModel(BaseModel):
    """
    A Pydantic model that represents a standard response from a cell.

    :param type: The type of response, indicating success or error.
    :param content: The content of the response, which may be a descriptive message or serialized data in JSON format.
    """

    type: ResponseType
    content: str


class BaseCell(Generic[InputModelT, OutputModelT], ABC):
    """
    Abstract base class for a Cell, which is an autonomous agent in the system.

    This class should be subclassed with specific implementations that define
    the `role`, `description`, `input_format`, `output_format`, and the `execute` method.

    :param role: The role of the cell within the system.
    :param description: A brief description of the cell's purpose.
    :param input_format: A Pydantic model describing the expected input format.
    :param output_format: A Pydantic model describing the expected output format.
    :param config: An optional configuration model for the cell.
    """

    role: str
    description: str
    input_format: Type[InputModelT]
    output_format: Type[OutputModelT]
    config: Optional[ConfigModel] = None

    def __init__(self, *args, **kwargs):
        """
        Initialize a new instance of the BaseCell class.

        :param args: Variable length argument list that can be used by subclasses.
        :param kwargs: Arbitrary keyword arguments that can be used by subclasses.
        """
        self.args = args
        self.kwargs = kwargs
        # Tracer from OpenTelemetry, used for creating spans around the cell's execution.
        self.tracer = trace.get_tracer(self.__class__.__name__)
        # Asyncio Lock for thread-safe operations within the cell.
        self.async_mutex = asyncio.Lock()

    def __init_subclass__(cls, **kwargs):
        """
        Initialize subclass checks for the presence and types of required class variables.
        """
        super().__init_subclass__(**kwargs)
        # Only perform checks if the subclass is not abstract
        if not inspect.isabstract(cls):
            if not hasattr(cls, "role") or cls.role is None:
                raise TypeError(
                    f"Subclass '{cls.__name__}' must define a 'role' class variable."
                )
            if not hasattr(cls, "description") or cls.description is None:
                raise TypeError(
                    f"Subclass '{cls.__name__}' must define a 'description' class variable."
                )
            if (
                not hasattr(cls, "input_format")
                or cls.input_format is None
                or not issubclass(cls.input_format, BaseModel)
            ):
                raise TypeError(
                    f"Subclass '{cls.__name__}' must define an 'input_format' class variable with a Pydantic model."
                )
            if (
                not hasattr(cls, "output_format")
                or cls.output_format is None
                or not issubclass(cls.output_format, BaseModel)
            ):
                raise TypeError(
                    f"Subclass '{cls.__name__}' must define an 'output_format' class variable with a Pydantic model."
                )

    @classmethod
    def get_role(cls) -> str:
        """
        Get the role of the cell.

        :return: The role of the cell.
        :raises NotImplementedError: If the `role` is not defined.
        """
        if cls.role is not None:
            return cls.role
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
    async def _execute(self, input_data: InputModelT) -> OutputModelT:
        """
        Asynchronously execute the cell's logic on the given input data and produce output.

        This method must be implemented by subclasses.

        :param input_data: The validated input data as an instance of TInputModel.
        :return: The output data as an instance of OutputModelT.
        :raises NotImplementedError: If the method is not implemented in the subclass.
        """
        raise NotImplementedError("Subclasses must implement 'execute' abstract method")

    async def run(self, input_json: str) -> dict:
        """
        Asynchronously process the input JSON string and return the result as a JSON.

        This method acquires a mutex, validates the input JSON against the
        `input_format` Pydantic model, executes the cell's logic by calling the
        `_execute` method, and then validates and serializes the output using
        the `output_format` Pydantic model.

        :param input_json: A JSON string representing the input data to be processed.
        :return: A JSON representing the response: ResponseModel, which could be the output data
                 or an error message.
        :raises NotImplementedError: If the input_format or output_format is not defined.
        :raises ValidationError: If the input data does not pass validation according to
                                 the input_format Pydantic model.
        :raises Exception: If any other exception occurs during the processing of the input.
        """
        async with self.async_mutex:  # Use an async context manager to acquire the lock
            with self.tracer.start_span("run"):
                try:
                    if self.input_format is None or self.output_format is None:
                        raise NotImplementedError(
                            "Input and output formats must be defined."
                        )

                    # Parse and validate the input JSON using the input_format Pydantic model
                    input_data = self.input_format.model_validate_json(input_json)

                    # Call the user-defined run method and get the output data
                    output_data = await self._execute(input_data)

                    # Validate and serialize the output using the output_format Pydantic model
                    output_data = self.output_format(**output_data.model_dump())

                    # Prepare the success response
                    response = ResponseModel(
                        type=ResponseType.SUCCESS, content=output_data.model_dump_json()
                    )
                except ValidationError as e:
                    # Prepare the error response in case of validation errors
                    response = ResponseModel(type=ResponseType.ERROR, content=str(e))
                except Exception as e:  # pylint: disable=broad-exception-caught
                    # Prepare the error response in case of other exceptions
                    response = ResponseModel(type=ResponseType.ERROR, content=str(e))
        # Serialize the response to JSON
        output: dict = json.loads(response.model_dump_json())
        return output

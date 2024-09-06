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

from abc import ABC, abstractmethod
from typing import Awaitable, Callable, TypeVar

from pydantic import BaseModel

from kin_sdk.common.types import ModuleType
from kin_sdk.agent_module._module.base import BaseModule


InputModelT = TypeVar("InputModelT", bound=BaseModel)
OutputModelT = TypeVar("OutputModelT", bound=BaseModel)
SetupModelT = TypeVar("SetupModelT", bound=BaseModel)


class BaseTool(BaseModule[InputModelT, OutputModelT, SetupModelT], ABC):
    """TODO: Sphinx docstring"""

    _module_type: ModuleType = ModuleType.TOOL

    @abstractmethod
    async def start(self, setup_id: str) -> None:
        """
        Starts the tool.
        """
        raise NotImplementedError("Tool must implement 'start' abstract method")

    @abstractmethod
    async def execute(
        self,
        input_data: InputModelT,
        setup_id: str,
        callback: Callable[[OutputModelT], Awaitable[None]],
    ) -> None:
        """
        Executes the tool.

        :param input_data: The input data for the tool.
        :param setup_id: The ID of the setup for the tool.
        :param callback: The callback to call with the output data.
        """
        raise NotImplementedError("Tool must implement 'execute' abstract method")

    @abstractmethod
    async def stop(self) -> None:
        """
        Stops the tool.
        """
        raise NotImplementedError("Tool must implement 'stop' abstract method")

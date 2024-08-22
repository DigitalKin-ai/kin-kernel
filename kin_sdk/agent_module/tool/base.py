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
from typing import Callable, TypeVar

from pydantic import BaseModel

from kin_sdk.common.types import ModuleType
from kin_sdk.agent_module._module import BaseModule


InputModelT = TypeVar("InputModelT", bound=BaseModel)
OutputModelT = TypeVar("OutputModelT", bound=BaseModel)
SetupModelT = TypeVar("SetupModelT", bound=BaseModel)


class BaseTool(BaseModule[InputModelT, OutputModelT, SetupModelT], ABC):
    """TODO: Sphinx docstring"""

    def __init__(
        self,
        module_id: str,
        module_address: str,
        module_port: int,
        registry_address: str,
        max_workers: int = 10,
    ):
        """
        Initializes the BaseTool.

        :param module_id: The ID of the module.
        :param module_address: The address of the module.
        :param module_port: The port of the module.
        :param registry_address: The address of the registry.
        :param max_workers: The maximum number of worker threads.
        """
        super().__init__(
            module_id=module_id,
            module_address=module_address,
            module_port=module_port,
            module_type=ModuleType.TOOL,
            registry_address=registry_address,
            max_workers=max_workers,
        )

    @abstractmethod
    def start(self) -> None:
        """
        Starts the tool.
        """
        raise NotImplementedError("Tool must implement 'start' abstract method")

    @abstractmethod
    def execute(
        self,
        input_data: InputModelT,
        setup_id: str,
        callback: Callable[[OutputModelT], None],
    ) -> None:
        """
        Executes the tool.

        :param input_data: The input data for the tool.
        :param setup_id: The ID of the setup for the tool.
        :param callback: The callback to call with the output data.
        """
        raise NotImplementedError("Tool must implement 'execute' abstract method")

    @abstractmethod
    def stop(self) -> None:
        """
        Stops the tool.
        """
        raise NotImplementedError("Tool must implement 'stop' abstract method")

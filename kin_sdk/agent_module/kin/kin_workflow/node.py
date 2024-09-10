"""
Module for defining nodes in a graph with input and output data.

This module includes classes for InputData, OutputData, and Node, which represent
the components of a graph node and provide methods for executing operations and
updating data.
"""

import asyncio
import datetime
from typing import Any, Awaitable, Dict, List, Callable, Optional

from pydantic import BaseModel, Field

from kin_sdk.common.types import ModuleType


class InputData(BaseModel):
    """
    Model for input data of a node.

    Attributes:
        label (Optional[str]): Label of the input parameter.
        value (Optional[Any]): Value of the input parameter.
        updated_at (Optional[datetime.datetime]): Updated time of the input parameter.
        optional (bool): Indicates if the value is optional.
    """

    label: Optional[str] = Field(None, description="Label of the input parameter")
    value: Optional[Any] = Field(None, description="Value of the input parameter")
    updated_at: Optional[datetime.datetime] = Field(
        None, description="Updated time of the input parameter or None if not updated"
    )
    optional: bool = Field(False, description="Indicates if the value is optional")


class OutputData(BaseModel):
    """
    Model for output data of a node.

    Attributes:
        label (Optional[str]): Label of the output parameter.
        value (Optional[Any]): Value of the output parameter.
        updated_at (Optional[datetime.datetime]): Updated time of the output parameter.
        optional (bool): Indicates if the value is optional.
    """

    label: Optional[str] = Field(None, description="Label of the output parameter")
    value: Optional[Any] = Field(None, description="Value of the output parameter")
    updated_at: Optional[datetime.datetime] = Field(
        None, description="Updated time of the output parameter or None if not updated"
    )
    optional: bool = Field(False, description="Indicates if the value is optional")


class Node:
    """
    Represents a node in the graph.

    Attributes:
        node_id (str): The unique identifier of the node.
        node_type (str): The type of the node.
        inputs (List[InputData]): The inputs of the node.
        outputs (List[OutputData]): The outputs of the node.
        status (str): The status of the node execution.
        current_execution (int): The current execution count.
        last_execution (Optional[datetime.datetime]): The timestamp of the last execution.
        setup (Dict[str, Any]): The setup configuration for the node.
    """

    def __init__(
        self,
        node_id: str,
        node_type: str,
        module_type: ModuleType,
        module_id: str,
        inputs: List[Dict[str, Any]],
        outputs: List[Dict[str, Any]],
        setup: Dict[str, Any],
    ):
        self._node_id = node_id
        self._node_type = node_type
        self._module_type = module_type
        self._module_id = module_id
        self._inputs = [InputData(**input) for input in inputs]
        self._outputs = [OutputData(**output) for output in outputs]
        self._status = "pending"  # 'pending', 'running', 'completed', 'failed'
        self._current_execution = 0
        self._last_execution = None
        self._setup = setup

    @property
    def node_id(self) -> str:
        """Get the node ID."""
        return self._node_id

    @property
    def node_type(self) -> str:
        """Get the node type."""
        return self._node_type

    @property
    def module_type(self) -> ModuleType:
        """Get the module type."""
        return self._module_type

    @property
    def module_id(self) -> str:
        """Get the module ID."""
        return self._module_id

    @property
    def inputs(self) -> List[InputData]:
        """Get the inputs of the node."""
        return self._inputs

    @property
    def outputs(self) -> List[OutputData]:
        """Get the outputs of the node."""
        return self._outputs

    @property
    def status(self) -> str:
        """Get the status of the node."""
        return self._status

    @property
    def current_execution(self) -> int:
        """Get the current execution count."""
        return self._current_execution

    @property
    def last_execution(self) -> Optional[datetime.datetime]:
        """Get the timestamp of the last execution."""
        return self._last_execution

    @property
    def setup(self) -> Dict[str, Any]:
        """Get the setup configuration for the node."""
        return self._setup

    @property
    def values(self) -> Dict[str, Any]:
        """
        Get the values of the input data.

        Returns:
            Dict[str, Any]: A dictionary of input labels and their corresponding values.
        """
        inputs = {}
        for input_data in self._inputs:
            if input_data.label is not None:
                inputs[input_data.label] = input_data.value
        return inputs

    async def execute(
        self, module_callback: Callable[[Dict[str, Any]], Awaitable[None]]
    ) -> Dict[str, OutputData]:
        """
        Executes the node with the given input data.

        Args:
            module_callback (Callable): The callback function to execute the module.

        Returns:
            Dict[str, OutputData]: The output data generated by the node.
        """
        try:
            self._status = "running"
            # print(f"Executing node {self._module_type}:{self._node_id}")
            module_response = await module_callback(
                self._module_id, self.values, self._node_id
            )

            # Simulate some work being done
            await asyncio.sleep(0.5)  # ! TODO: remove this line
            print(f"\t - module_response: {module_response}")
            for label, value in module_response.items():
                self.update_output(label, value)

            output_data = {
                output.label: output
                for output in self._outputs
                if output.label is not None
            }

            self._last_execution = datetime.datetime.now()
            self._status = "completed"
            return output_data
        except Exception as e:  # pylint: disable=broad-except
            print(
                f"Unexpected error executing node {self._module_type}:{self._node_id}: {e}"
            )
            self._status = "failed"
            return {}

    async def get_setup(self, setup_id: str) -> Dict[str, Any]:
        """
        Get the setup data for the given setup id.

        Args:
            setup_id (str): The unique identifier of the setup.

        Returns:
            Dict[str, Any]: The setup data.
        """
        return {
            "setup_id": setup_id,
            "setup_data": f"setup_data_{setup_id}",
        }

    def update_input(self, label: str, value: Any) -> None:
        """
        Update the value of an input parameter.

        Args:
            label (str): The label of the input parameter to update.
            value (Any): The new value for the input parameter.
        """
        self._update_data(self.inputs, label, value)

    def update_output(self, label: str, value: Any) -> None:
        """
        Update the value of an output parameter.

        Args:
            label (str): The label of the output parameter to update.
            value (Any): The new value for the output parameter.
        """
        self._update_data(self.outputs, label, value)

    def _update_data(self, data_list: List[BaseModel], label: str, value: Any) -> None:
        """
        Update the value of a parameter in a given data list.

        Args:
            data_list (List[BaseModel]): The list of data models to update.
            label (str): The label of the parameter to update.
            value (Any): The new value for the parameter.
        """
        for data in data_list:
            if data.label == label:
                data.value = value
                data.updated_at = datetime.datetime.now()
                break

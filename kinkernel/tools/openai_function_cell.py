"""
This module provides a wrapper class OpenAiFunctionCell to connect DK BaseCell with OpenAI's Function Calls.
It allows for the invocation of these cells asynchronously and provides access to their arguments.
"""

import json

from typing import Union, Dict, Any, List

from kinkernel.cells import BaseCell


class OpenAiFunctionCell:
    """
    A class representing an OpenAI function calls that wraps around a DK BaseCell object, providing
    a convenient interface to access its properties and execute it asynchronously.

    Attributes:
        cell (BaseCell): The underlying BaseCell instance.
        name (str): The role name of the cell.
        description (str): The description of the cell.
    """

    def __init__(self, cell: BaseCell):
        """
        Initialize the OpenAiFunctionCell with a given BaseCell.

        Args:
            cell (BaseCell): The BaseCell instance to wrap.
        """
        self.cell = cell
        self.name = self.cell.get_role()
        self.description = self.cell.get_description()

    @property
    def args(self) -> dict:
        """
        Retrieve the input arguments schema for the cell.

        Returns:
            Dict[str, Any]: A dictionary representing the input arguments schema.

        Raises:
            ValueError: If the input schema is not found or cannot be parsed.
        """
        if self.cell.get_input_format() is None:
            raise ValueError(
                f"No input schema found in the cell: {self.cell.get_role()}"
            )

        try:
            input_schema: Dict[str, Any] = json.loads(self.cell.get_input_format())[
                "properties"
            ]
            return input_schema
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON input schema: {e}") from e

    async def ainvoke(
        self, input: Union[str, Dict[str, Any]]  # pylint: disable=W0622
    ) -> Any:
        """
        Asynchronously invoke the cell with the given input.

        Args:
            input (Union[str, Dict[str, Any]]): The input data to pass to the cell. Can be a JSON string or a dictionary.

        Returns:
            Any: The output content from the cell after execution.

        Raises:
            TypeError: If the input cannot be serialized to JSON.
            KeyError: If the expected output key 'content' is missing from the cell's response.
        """
        try:
            input_json = json.dumps(input)
        except TypeError as e:
            print("herhreherhreherherhrh")
            raise TypeError(f"Input could not be serialized to JSON: {e}") from e

        cell_output = await self.cell.run(input_json)
        if "content" not in cell_output:
            raise KeyError(
                f"The 'content' key is missing in the cell's output: {cell_output}"
            )
        return cell_output["content"]

    def __repr__(self) -> str:
        """
        Represent the OpenAiFunctionCell as a string with its name.

        Returns:
            str: The string representation of the OpenAiFunctionCell.
        """
        return f"{self.name}()"


def cell_to_openai_function(cells: List[BaseCell]) -> List[OpenAiFunctionCell]:
    """
    Convert a list of BaseCell instances to a list of OpenAiFunctionCell instances.

    Args:
        cells (List[BaseCell]): The list of BaseCell instances to convert.

    Returns:
        List[OpenAiFunctionCell]: A list of OpenAiFunctionCell instances.
    """
    return [OpenAiFunctionCell(cell) for cell in cells]

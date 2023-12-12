# pylint: disable-all
# test_cell.py
import pytest
from pydantic import BaseModel

from kinkernel.cells.base import BaseCell
from kinkernel import Cell


# Create dummy BaseModel subclasses for testing purposes
class InputModel(BaseModel):
    input_field: str


class OutputModel(BaseModel):
    output_field: int


# Define a concrete subclass of BaseCell for testing purposes
class ConcreteCell(Cell[InputModel, OutputModel]):
    role = "test"
    description = "A test cell"
    input_format = InputModel
    output_format = OutputModel

    async def _execute(self, input_data: InputModel) -> OutputModel:
        return OutputModel(output_field=len(input_data.input_field))


# Define the test class for ConcreteCell
class TestConcreteCell:
    def test_concrete_cell_instantiation(self):
        # Test the instantiation of ConcreteCell
        cell = ConcreteCell()
        assert isinstance(cell, Cell)
        assert isinstance(cell, BaseCell)
        assert isinstance(cell, ConcreteCell)
        assert cell.role == "test"
        assert cell.description == "A test cell"

    @pytest.mark.asyncio
    async def test_concrete_cell_execute(self):
        # Test the execute method of ConcreteCell
        cell = ConcreteCell()
        input_model = InputModel(input_field="test")
        output_model = await cell._execute(input_model)
        assert isinstance(output_model, OutputModel)
        assert output_model.output_field == 4  # length of "test"

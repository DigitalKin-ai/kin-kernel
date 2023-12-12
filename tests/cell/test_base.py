# pylint: disable-all
import json
import pytest

from pydantic import BaseModel

from kinkernel.cells import BaseCell


# Define Pydantic models for testing purposes
class TestInputModel(BaseModel):
    __test__ = False
    x: int
    y: int


class TestOutputModel(BaseModel):
    __test__ = False
    result: int


# Define a concrete subclass of BaseCell for testing purposes
class ConcreteCell(BaseCell[TestInputModel, TestOutputModel]):
    role = "test"
    description = "A test cell"
    input_format = TestInputModel
    output_format = TestOutputModel

    async def _execute(self, input_data: TestInputModel) -> TestOutputModel:
        return TestOutputModel(result=input_data.x + input_data.y)


# Define a concrete subclass that intentionally leaves the `execute` method unimplemented
class NoExecuteCell(BaseCell[BaseModel, BaseModel]):
    role = "unimplemented_execute"
    description = "A cell with an unimplemented execute method"
    input_format = BaseModel
    output_format = BaseModel


# Define a concrete subclass that intentionally leaves the `execute` method unimplemented
class UnimplementedExecuteCell(BaseCell[BaseModel, BaseModel]):
    role = "unimplemented_execute"
    description = "A cell with an unimplemented execute method"
    input_format = BaseModel
    output_format = BaseModel

    async def _execute(self, input_data: BaseModel) -> BaseModel:
        raise NotImplementedError


# Define a test for successful execution of the cell
@pytest.mark.asyncio
async def test_concrete_cell_success():
    cell = ConcreteCell()
    input_json = '{"x": 1, "y": 2}'
    result = await cell.run(input_json)

    # Define the expected result as a dictionary
    expected_result = {"type": "success", "content": '{"result":3}'}

    # Compare the actual result with the expected result
    assert result == expected_result


# Define a test for the __init__ method of BaseCell
def test_base_cell_init():
    cell = ConcreteCell(custom_arg="value")
    assert cell.args == ()
    assert cell.kwargs == {"custom_arg": "value"}


# Define a test for the run method where a general exception is raised
@pytest.mark.asyncio
async def test_concrete_cell_general_exception():
    cell = ConcreteCell()

    # Mock _execute to raise a general exception
    async def mock_execute(input_data):
        raise Exception("General error")

    cell._execute = mock_execute

    input_json = '{"x": 1, "y": 2}'
    result = await cell.run(input_json)

    assert result["type"] == "error"
    assert result["content"] == "General error"


# Define a test to cover the NotImplementedError in _execute method of BaseCell
@pytest.mark.asyncio
async def test_base_cell_execute_not_implemented_direct_call():
    cell = ConcreteCell()

    with pytest.raises(NotImplementedError):
        await BaseCell._execute(cell, TestInputModel(x=1, y=2))


# Define a test for input validation error
@pytest.mark.asyncio
async def test_concrete_cell_input_validation_error():
    cell = ConcreteCell()
    input_json = '{"x": "not_a_number", "y": 2}'
    result = await cell.run(input_json)

    assert result["type"] == "error"
    assert "validation error for TestInputModel" in result["content"]
    assert "Input should be a valid integer" in result["content"]
    assert "unable to parse string as an integer" in result["content"]


# Define a test for the abstract execute method error
@pytest.mark.asyncio
async def test_base_cell_execute_not_implemented():
    with pytest.raises(NotImplementedError):
        cell = UnimplementedExecuteCell()
        await cell._execute(None)


# Define a test for the abstract execute method error
def test_base_cell_execute_not_implemented2():
    with pytest.raises(TypeError):
        NoExecuteCell()


# Define tests for class method outputs
def test_get_role():
    assert ConcreteCell.get_role() == "test"
    assert ConcreteCell.get_role() != "other"


def test_get_description():
    assert ConcreteCell.get_description() == "A test cell"
    assert ConcreteCell.get_description() != "Other"


def test_get_input_format():
    expected_input_format = ConcreteCell.get_input_format()
    exemple_input = {
        "properties": {
            "x": {"title": "X", "type": "integer"},
            "y": {"title": "Y", "type": "integer"},
        },
        "required": ["x", "y"],
        "title": "TestInputModel",
        "type": "object",
    }
    assert exemple_input == json.loads(expected_input_format)


def test_get_output_format():
    exemple_output_format = ConcreteCell.get_output_format()
    exemple_output = {
        "properties": {"result": {"title": "Result", "type": "integer"}},
        "required": ["result"],
        "title": "TestOutputModel",
        "type": "object",
    }
    assert exemple_output == json.loads(exemple_output_format)


# Define tests for exceptions in __init_subclass__
def test_missing_role():
    with pytest.raises(TypeError):

        class CellWithoutRole(BaseCell[TestInputModel, TestOutputModel]):
            role = None
            description = "No role"
            input_format = TestInputModel
            output_format = TestOutputModel

            async def _execute(self, input_data: TestInputModel) -> TestOutputModel:
                return TestOutputModel(result=input_data.y)

        CellWithoutRole()


def test_missing_description():
    with pytest.raises(TypeError):

        class CellWithoutDescription(BaseCell[TestInputModel, TestOutputModel]):
            role = "No description"
            description = None
            input_format = TestInputModel
            output_format = TestOutputModel

            async def _execute(self, input_data: TestInputModel) -> TestOutputModel:
                return TestOutputModel(result=input_data.y)

        CellWithoutDescription()


def test_missing_input_format():
    with pytest.raises(TypeError):

        class CellWithoutInputFormat(BaseCell[TestOutputModel, TestOutputModel]):
            role = "No input format"
            description = "No input format"
            input_format = None
            output_format = TestOutputModel

            async def _execute(self, input_data: TestOutputModel) -> TestOutputModel:
                return TestOutputModel(result=2)

        CellWithoutInputFormat()


def test_missing_output_format():
    with pytest.raises(TypeError):

        class CellWithoutInputFormat(BaseCell[TestInputModel, TestInputModel]):
            role = "No input format"
            description = "No input format"
            input_format = TestInputModel
            output_format = None

            async def _execute(self, input_data: TestInputModel) -> TestInputModel:
                return TestInputModel(x=input_data.x, y=input_data.y)

        CellWithoutInputFormat()

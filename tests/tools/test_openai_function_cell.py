import pytest
import json

# Import the module and classes/functions to be tested
from kinkernel.tools.openai_function_cell import (
    OpenAiFunctionCell,
    cell_to_openai_function,
)


# Mock BaseCell to avoid actual API calls
class MockBaseCell:
    def get_role(self):
        return "test_role"

    def get_description(self):
        return "test_description"

    def get_input_format(self):
        return json.dumps(
            {"properties": {"arg1": {"type": "string"}, "arg2": {"type": "number"}}}
        )

    async def run(self, input_json):
        return {"content": f"Processed {input_json}"}


@pytest.fixture
def base_cell():
    return MockBaseCell()


@pytest.fixture
def open_ai_function_cell(base_cell):
    return OpenAiFunctionCell(base_cell)


def test_openai_function_cell_init(base_cell):
    cell = OpenAiFunctionCell(base_cell)
    assert cell.name == "test_role"
    assert cell.description == "test_description"


def test_openai_function_cell_args(open_ai_function_cell):
    expected_args = {"arg1": {"type": "string"}, "arg2": {"type": "number"}}
    assert open_ai_function_cell.args == expected_args


@pytest.mark.asyncio
async def test_openai_function_cell_ainvoke(open_ai_function_cell):
    input_data = {"arg1": "value1", "arg2": 42}
    result = await open_ai_function_cell.ainvoke(input_data)
    assert result == f"Processed {json.dumps(input_data)}"


def test_cell_to_openai_function(base_cell):
    cells = [base_cell, base_cell]
    openai_function_cells = cell_to_openai_function(cells)
    assert len(openai_function_cells) == 2
    for func_cell in openai_function_cells:
        assert isinstance(func_cell, OpenAiFunctionCell)


# #############################
# No input format
# #############################


# Mock BaseCell to avoid actual API calls
class MockBaseCellFail:
    def get_role(self):
        return "test_role"

    def get_description(self):
        return "test_description"

    def get_input_format(self):
        # Return None to simulate a missing input format
        return None

    async def run(self, input_json):
        # Simulate different responses based on input
        if input_json == json.dumps({"error": "simulate"}):
            return {}  # Missing 'content' key
        return {"content": f"Processed {input_json}"}


@pytest.fixture
def base_cell_fail():
    return MockBaseCellFail()


@pytest.fixture
def open_ai_function_cell_fail(base_cell_fail):
    return OpenAiFunctionCell(base_cell_fail)


def test_openai_function_cell_missing_args(open_ai_function_cell_fail):
    with pytest.raises(ValueError) as excinfo:
        _ = open_ai_function_cell_fail.args
    assert "No input schema found" in str(excinfo.value)


@pytest.mark.asyncio
async def test_openai_function_cell_ainvoke_error(open_ai_function_cell_fail):
    with pytest.raises(KeyError) as excinfo:
        await open_ai_function_cell_fail.ainvoke({"error": "simulate"})
    assert "The 'content' key is missing" in str(excinfo.value)


@pytest.mark.asyncio
async def test_openai_function_cell_ainvoke_serialization_error(
    open_ai_function_cell_fail,
):
    with pytest.raises(TypeError) as excinfo:
        # Pass an object that cannot be serialized to JSON
        await open_ai_function_cell_fail.ainvoke(lambda x: x)
    assert "Input could not be serialized to JSON:" in str(excinfo.value)


def test_repr(open_ai_function_cell_fail):
    assert repr(open_ai_function_cell_fail) == "test_role()"


# #############################
# Invalid input format
# #############################


# Extend the MockBaseCell to simulate a JSON decoding error
class MockBaseCellWithInvalidJSON(MockBaseCell):
    def get_input_format(self):
        # Return an invalid JSON string
        return "{invalid_json}"


@pytest.fixture
def base_cell_with_invalid_json():
    return MockBaseCellWithInvalidJSON()


@pytest.fixture
def open_ai_function_cell_with_invalid_json(base_cell_with_invalid_json):
    return OpenAiFunctionCell(base_cell_with_invalid_json)


def test_openai_function_cell_invalid_json_args(
    open_ai_function_cell_with_invalid_json,
):
    with pytest.raises(ValueError) as excinfo:
        _ = open_ai_function_cell_with_invalid_json.args
    assert "Invalid JSON input schema" in str(excinfo.value)

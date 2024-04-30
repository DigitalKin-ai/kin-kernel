from typing import Tuple
from pydantic import BaseModel, Field

from kin_sdk.tool.base import BaseTool


class AdditionInput(BaseModel):
    last_numbers: Tuple[int, int] = Field(
        ..., description="The last two numbers of fibonacci sequence"
    )


class AdditionOutput(BaseModel):
    next_number: int = Field(..., description="Next number in fibonacci sequence")


class AdditionTool(BaseTool[AdditionInput, AdditionOutput]):
    name = "Addition"
    description = "A simple addition tool that take to number and return the sum"
    input_format = AdditionInput
    output_format = AdditionOutput

    def execute(self, input_data: AdditionInput) -> AdditionOutput:
        """
        Execute the addition tool
        """
        return AdditionOutput(
            next_number=input_data.last_numbers[0] + input_data.last_numbers[1]
        )

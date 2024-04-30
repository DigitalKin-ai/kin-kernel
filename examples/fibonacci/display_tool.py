from typing import List
from pydantic import BaseModel, Field

from kin_sdk.tool.base import BaseTool


class DisplayInput(BaseModel):
    fibonacci: List[int] = Field(..., description="The fibonacci sequence")
    new_number: int = Field(..., description="The new number of fibonacci sequence")


class DisplayOutput(BaseModel):
    pass


class DisplayTool(BaseTool[DisplayInput, DisplayOutput]):
    name = "Display"
    description = "A simple tool to display the fibonacci sequence"
    input_format = DisplayInput
    output_format = DisplayOutput

    def execute(self, input_data: DisplayInput) -> DisplayOutput:
        """
        Execute the addition tool
        """
        print("Fibonacci sequence:", input_data.fibonacci)
        print("New number:", input_data.new_number)
        return DisplayOutput()

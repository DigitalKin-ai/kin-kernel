from typing import List, Optional, Tuple
from pydantic import BaseModel, Field

from kin_sdk.tool.base import BaseTool


class SequenceInput(BaseModel):
    initial_numbers: Tuple[int, int] = Field(
        ..., description="The first two numbers of fibonacci sequence"
    )
    new_numbers: Optional[int] = Field(
        ..., description="The next numbers of fibonacci sequence"
    )


class SequenceOutput(BaseModel):
    last_number: int = Field(..., description="The last number in fibonacci sequence")
    fibonacci: List[int] = Field(..., description="The fibonacci sequence")


class SequenceTool(BaseTool[SequenceInput, SequenceOutput]):
    name = "Sequence"
    description = "Buffer to save the fibonnaci sequence"
    input_format = SequenceInput
    output_format = SequenceOutput

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fibonacci = None

    def execute(self, input_data: SequenceInput) -> SequenceOutput:
        """
        Execute the addition tool
        """
        if not self.fibonacci:
            self.fibonacci = list(input_data.initial_numbers)
        if input_data.new_numbers:
            self.fibonacci.append(input_data.new_numbers)
        return SequenceOutput(
            last_number=input_data.new_numbers, fibonacci=self.fibonacci
        )

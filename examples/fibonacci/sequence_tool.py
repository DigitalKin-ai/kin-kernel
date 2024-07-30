from typing import Callable, List, Optional, Tuple
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
    fibonacci_list: List[int] = Field(..., description="The fibonacci sequence")


class SequenceSetup(BaseModel):
    pass


class SequenceTool(BaseTool[SequenceInput, SequenceOutput, SequenceSetup]):
    name = "Sequence"
    description = "Buffer to save the fibonnaci sequence"
    input_format = SequenceInput
    output_format = SequenceOutput
    setup_format = SequenceSetup

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fibonacci = None

    def start(self) -> None:
        """
        Start the service
        """
        print("Starting the service")

    def execute(
        self,
        input_data: SequenceInput,
        setup_id: str,
        callback: Callable[[SequenceSetup], None],
    ) -> SequenceOutput:
        """
        Execute the addition tool
        """
        if not self.fibonacci:
            self.fibonacci = list(input_data.initial_numbers)
        if input_data.new_numbers:
            self.fibonacci.append(input_data.new_numbers)

        callback(
            SequenceOutput(last_number=input_data.new_numbers, fibonacci=self.fibonacci)
        )

    def stop(self) -> None:
        """
        Stop the service
        """
        print("Stopping the service")


if __name__ == "__main__":
    # ! First start the service registry server from the examples.server_registry.py file
    test = {"input": {"last_numbers": [1, 2]}}
    # Create an instance of your custom tool
    sequence_tool = SequenceTool(
        service_id="services:sequence_tool",
        service_address="localhost",
        service_port=50053,
        registry_address="localhost:50051",
    )
    sequence_tool.serve()

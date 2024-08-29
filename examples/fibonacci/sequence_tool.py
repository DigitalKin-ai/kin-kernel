from typing import Callable, List, Optional, Tuple
from pydantic import BaseModel, Field

from kin_sdk.agent_module import BaseTool


class SequenceInput(BaseModel):
    initial_numbers: Tuple[int, int] = Field(
        ..., description="The first two numbers of fibonacci sequence"
    )
    next_number: Optional[int] = Field(
        ..., description="The next numbers of fibonacci sequence"
    )


class SequenceOutput(BaseModel):
    last_numbers: Tuple[int, int] = Field(
        ..., description="The last number in fibonacci sequence"
    )
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

    def start(self, setup_id: str) -> None:
        """
        Start the module
        """
        print("Starting the module")

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
        if input_data.next_number:
            self.fibonacci.append(input_data.next_number)

        callback(
            SequenceOutput(
                last_numbers=(self.fibonacci[-2], self.fibonacci[-1]),
                fibonacci_list=self.fibonacci,
            )
        )

    def stop(self) -> None:
        """
        Stop the module
        """
        print("Stopping the module")


if __name__ == "__main__":
    # ! First start the module registry server from the examples.server_registry.py file
    test = {"input": {"last_numbers": [1, 2]}}
    # Create an instance of your custom tool
    sequence_tool = SequenceTool(
        module_id="modules:sequence_tool",
        module_address="localhost",
        module_port=50053,
        registry_address="localhost:50051",
    )
    sequence_tool.serve()

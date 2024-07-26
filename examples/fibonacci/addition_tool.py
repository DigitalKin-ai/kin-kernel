from typing import Callable, Tuple
from pydantic import BaseModel, Field

from google.protobuf import json_format, struct_pb2
from kin_sdk.tool.base import BaseTool


class AdditionInput(BaseModel):
    last_numbers: Tuple[int, int] = Field(
        ..., description="The last two numbers of fibonacci sequence"
    )


class AdditionOutput(BaseModel):
    next_number: int = Field(..., description="Next number in fibonacci sequence")


class AdditionSetup(BaseModel):
    """empty setup"""

    pass


class AdditionTool(BaseTool[AdditionInput, AdditionOutput, AdditionSetup]):
    name = "Addition"
    description = "A simple addition tool that take to number and return the sum"
    input_format = AdditionInput
    output_format = AdditionOutput
    setup_format = AdditionSetup

    def start(self) -> None:
        """
        Start the service
        """
        print("Starting the service")

    def execute(
        self,
        input_data: AdditionInput,
        setup_id: str,
        callback: Callable[[AdditionOutput], None],
    ) -> None:
        """
        Execute the addition tool
        """
        print(f"Execute the service with setup_id: {setup_id}")
        callback(
            AdditionOutput(
                next_number=input_data.last_numbers[0] + input_data.last_numbers[1]
            )
        )

    def stop(self) -> None:
        """
        Stop the service
        """
        print("Stopping the service")


if __name__ == "__main__":
    # ! First start the service registry server from the examples.server_registry.py file
    test = {"input": {"last_numbers": [1, 2]}}
    print(json_format.ParseDict(test, struct_pb2.Struct()))
    # Create an instance of your custom tool
    addition_tool = AdditionTool(
        service_id="services:addition_tool",
        service_address="localhost",
        service_port=50053,
        registry_address="localhost:50051",
    )
    addition_tool.serve()

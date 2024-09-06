"""TODO: Add a description here"""

from typing import Awaitable, Callable, Tuple
from pydantic import BaseModel, Field

from kin_sdk.agent_module import BaseTool


class AdditionInput(BaseModel):
    """Input data for the addition tool"""

    last_numbers: Tuple[int, int] = Field(
        ..., description="The last two numbers of fibonacci sequence"
    )


class AdditionOutput(BaseModel):
    """Output data for the addition tool"""

    next_number: int = Field(..., description="Next number in fibonacci sequence")


class AdditionSetup(BaseModel):
    """empty setup"""


class AdditionTool(BaseTool[AdditionInput, AdditionOutput, AdditionSetup]):
    """A simple addition tool"""

    name = "Addition"
    description = "A simple addition tool that take to number and return the sum"
    input_format = AdditionInput
    output_format = AdditionOutput
    setup_format = AdditionSetup

    async def start(self, setup_id: str) -> None:
        """
        Start the module
        """
        print("Starting the module setup: ", setup_id)

    async def execute(
        self,
        input_data: AdditionInput,
        setup_id: str,
        callback: Callable[[AdditionOutput], Awaitable[None]],
    ) -> None:
        """
        Execute the addition tool
        """
        print(f"Execute the module with setup_id: {setup_id}")
        await callback(
            AdditionOutput(
                next_number=input_data.last_numbers[0] + input_data.last_numbers[1]
            )
        )

    async def stop(self) -> None:
        """
        Stop the module
        """
        print("Stopping the module")


# if __name__ == "__main__":
#     # ! First start the module registry server from the examples.server_registry.py file
#     # Create an instance of your custom tool
#     addition_tool = AdditionTool(
#         module_id="modules:addition_tool",
#         module_address="localhost",
#         module_port=50053,
#         registry_address="localhost:50051",
#     )
#     addition_tool.serve()

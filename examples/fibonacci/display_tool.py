from typing import Awaitable, Callable, List
from pydantic import BaseModel, Field

from kin_sdk.agent_module import BaseTool


class DisplayInput(BaseModel):
    """
    TODO: input format
    """

    fibonacci_list: List[int] = Field(..., description="The fibonacci sequence")
    next_number: int = Field(..., description="The new number of fibonacci sequence")


class DisplayOutput(BaseModel):
    """
    TODO: output format
    """


class DisplaySetup(BaseModel):
    """
    TODO: setup format
    """


class DisplayTool(BaseTool[DisplayInput, DisplayOutput, DisplaySetup]):
    """
    TODO: Add description
    """

    name = "Display"
    description = "A simple tool to display the fibonacci sequence"
    input_format = DisplayInput
    output_format = DisplayOutput
    setup_format = DisplaySetup

    async def start(self, setup_id: str) -> None:
        """
        Start the module
        """
        print("Starting the module setup: ", setup_id)

    async def execute(
        self,
        input_data: DisplayInput,
        setup_id: str,
        callback: Callable[[DisplayOutput], Awaitable[None]],
    ) -> None:
        """
        Execute the addition tool
        """
        print("Fibonacci sequence:", input_data.fibonacci_list)
        print("New number:", input_data.next_number)
        await callback(DisplayOutput())

    async def stop(self) -> None:
        """
        Stop the module
        """
        print("Stopping the module")


# if __name__ == "__main__":
#     # ! First start the module registry server from the examples.server_registry.py file
#     test = {"input": {"last_numbers": [1, 2]}}
#     # Create an instance of your custom tool
#     display_tool = DisplayTool(
#         module_id="modules:display_tool",
#         module_address="localhost",
#         module_port=50053,
#         registry_address="localhost:50051",
#     )
#     display_tool.serve()

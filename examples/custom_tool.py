"""TODO: Add a description here"""

import asyncio
from typing import Callable
from pydantic import BaseModel

from kin_sdk.agent_module import BaseTool
from kin_sdk.grpc_system import ModuleServer


class MultiplyInput(BaseModel):
    """Input data for the multiplier tool"""

    number: float
    factor: float = 2.0  # Default factor is 2


class MultiplyOutput(BaseModel):
    """Output data for the multiplier tool"""

    result: float


class MultiplySetup(BaseModel):
    """Output data for the multiplier tool"""


class CustomTool(BaseTool[MultiplyInput, MultiplyOutput, MultiplySetup]):
    """A simple multiplier tool"""

    name = "Multiplier"
    description = "A simple multiplier tool"
    input_format = MultiplyInput
    output_format = MultiplyOutput
    setup_format = MultiplySetup

    async def start(self, setup_id: str) -> None:
        """Start the module"""
        print("Starting the module")

    async def execute(
        self,
        input_data: MultiplyInput,
        setup_id: str,
        callback: Callable[[MultiplyOutput], None],
    ) -> None:
        """Multiply the input number by the factor"""
        # Implémentez la logique spécifique de l'outil ici
        exec_result = {"result": input_data.number * input_data.factor}
        print(MultiplyOutput(**exec_result))
        await callback(MultiplyOutput(**exec_result))

    async def stop(self) -> None:
        """Stop the module"""
        print("Stopping the module")


async def main():
    """
    TODO: Add a description here
    """
    # ! First start the module registry server from the examples.server_registry.py file
    # Create an instance of your custom tool
    tool_server = ModuleServer(
        module_class=CustomTool,
        module_id="multiplier1",
        module_address="localhost",
        module_port=50052,
        registry_address="localhost:50051",
        max_workers=10,
    )
    await tool_server.serve()


if __name__ == "__main__":
    asyncio.run(main())

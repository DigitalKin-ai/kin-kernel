"""TODO: Add a description here"""

from pydantic import BaseModel

from kin_sdk.agent_module import BaseTool


class MultiplyInput(BaseModel):
    """Input data for the multiplier tool"""

    number: float
    factor: float = 2.0  # Default factor is 2


class MultiplyOutput(BaseModel):
    """Output data for the multiplier tool"""

    result: float


class CustomTool(BaseTool[MultiplyInput, MultiplyOutput]):
    """A simple multiplier tool"""

    name = "Multiplier"
    description = "A simple multiplier tool"
    input_format = MultiplyInput
    output_format = MultiplyOutput

    def execute(self, input_data: MultiplyInput) -> MultiplyOutput:
        """Multiply the input number by the factor"""
        # Implémentez la logique spécifique de l'outil ici
        exec_result = {"result": input_data.number * input_data.factor}
        print(MultiplyOutput(**exec_result))
        return MultiplyOutput(**exec_result)


if __name__ == "__main__":
    # ! First start the module registry server from the examples.server_registry.py file
    # Create an instance of your custom tool
    custom_tool = CustomTool(
        module_id="multiplier1",
        module_address="localhost",
        module_port=50052,
        registry_address="localhost:50051",
    )
    custom_tool.serve()

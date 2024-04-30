from pydantic import BaseModel

from kin_sdk.tool.base import BaseTool


class MultiplyInput(BaseModel):
    number: float
    factor: float = 2.0  # Default factor is 2


class MultiplyOutput(BaseModel):
    result: float


class CustomTool(BaseTool[MultiplyInput, MultiplyOutput]):
    name = "Multiplier"
    description = "A simple multiplier tool"
    input_format = MultiplyInput
    output_format = MultiplyOutput

    def execute(self, input_data: MultiplyInput) -> MultiplyOutput:
        # Implémentez la logique spécifique de l'outil ici
        exec_result = {"result": input_data.number * input_data.factor}
        print(MultiplyOutput(**exec_result))
        return MultiplyOutput(**exec_result)


if __name__ == "__main__":
    # ! First start the service registry server from the examples.server_registry.py file
    # Create an instance of your custom tool
    custom_tool = CustomTool(
        service_id="multiplier1",
        service_address="localhost",
        service_port=50052,
        registry_address="localhost:50051",
    )
    custom_tool.serve()

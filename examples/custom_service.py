from typing import Callable
from pydantic import BaseModel

from kin_sdk.common.types import ModuleType
from kin_sdk.agent_module._module import BaseModule


class MultiplyInput(BaseModel):
    number: float
    factor: float = 2.0  # Default factor is 2


class MultiplyOutput(BaseModel):
    result: float


class MultiplySetup(BaseModel):
    result: float


class CustomModule(BaseModule):
    name = "Multiplier"
    description = "A simple multiplier tool"
    input_format = MultiplyInput
    output_format = MultiplyOutput
    setup_format = MultiplySetup

    def start(self) -> None:
        print("Starting the module")

    def stop(self) -> None:
        print("Stopping the module")

    def execute(
        self,
        input_data: MultiplyInput,
        setup_id: str,
        callback: Callable[[MultiplyOutput], None],
    ) -> None:
        # Implémentez la logique spécifique de l'outil ici
        exec_result = {"result": input_data.number * input_data.factor}
        callback(MultiplyOutput(**exec_result))

        # counter = 0

        # while counter < 10:
        #     # Implémentez la logique spécifique de l'outil ici
        #     callback(MultiplyOutput(**exec_result))
        #     counter += 1
        #     time.sleep(0.05)


if __name__ == "__main__":
    # ! First start the module registry server from the examples.server_registry.py file
    # Create an instance of your custom tool
    custom_module = CustomModule(
        module_id="multiplier1",
        module_address="localhost",
        module_type=ModuleType.TOOL,
        module_port=50052,
        registry_address="localhost:50051",
        max_workers=10,
    )
    custom_module.serve()

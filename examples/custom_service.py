import time
from typing import Callable
from pydantic import BaseModel

from kin_sdk.service.base import BaseService


class MultiplyInput(BaseModel):
    number: float
    factor: float = 2.0  # Default factor is 2


class MultiplyOutput(BaseModel):
    result: float


class MultiplySetup(BaseModel):
    result: float


class CustomService(BaseService):
    name = "Multiplier"
    description = "A simple multiplier tool"
    input_format = MultiplyInput
    output_format = MultiplyOutput
    setup_format = MultiplySetup

    def start(self) -> None:
        print("Starting the service")

    def stop(self) -> None:
        print("Stopping the service")

    def execute(
        self,
        input_data: MultiplyInput,
        setup_id: str,
        callback: Callable[[MultiplyOutput], None],
    ) -> None:
        # Implémentez la logique spécifique de l'outil ici
        exec_result = {"result": input_data.number * input_data.factor}
        callback(MultiplyOutput(**exec_result))

        counter = 0

        while counter < 10:
            # Implémentez la logique spécifique de l'outil ici
            callback(MultiplyOutput(**exec_result))
            counter += 1
            time.sleep(0.05)


if __name__ == "__main__":
    # ! First start the service registry server from the examples.server_registry.py file
    # Create an instance of your custom tool
    custom_service = CustomService(
        service_id="multiplier1",
        service_address="localhost",
        service_type="tool",
        service_port=50052,
        registry_address="localhost:50051",
        max_workers=20,
    )
    custom_service.serve()

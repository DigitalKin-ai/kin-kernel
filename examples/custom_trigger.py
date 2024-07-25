import time
import random
from typing import Callable
from pydantic import BaseModel

from kin_sdk.trigger.base import BaseTrigger


class CronMultiplyInput(BaseModel):
    pass


class CronMultiplyOutput(BaseModel):
    numbers: float
    factor: float = 2.0  # Default factor is 2


class CronMultiplySetup(BaseModel):
    result: float


class CustomTrigger(
    BaseTrigger[CronMultiplyInput, CronMultiplyOutput, CronMultiplySetup]
):
    name = "Cron Multiplier"
    description = "A simple cron that execute multiplier tool"
    input_format = CronMultiplyInput
    output_format = CronMultiplyOutput
    setup_format = CronMultiplySetup

    def execute(
        self,
        input_data: CronMultiplyInput,
        setup_id: str,
        callback: Callable[[CronMultiplyOutput], None],
    ) -> None:
        counter = 0
        start = random.randint(0, 100)

        print("input_data", input_data)

        while counter < 10:
            # Implémentez la logique spécifique de l'outil ici
            exec_result = {"numbers": 5, "factor": start + counter}
            callback(CronMultiplyOutput(**exec_result))
            counter += 1
            time.sleep(1)

    def start(self) -> None:
        print("Executing cron job", self.name)

    def stop(self) -> None:
        print("Stopping cron job", self.name)


if __name__ == "__main__":
    # ! First start the service registry server from the examples.server_registry.py file
    # Create an instance of your custom tool
    custom_trigger = CustomTrigger(
        service_id="cron multiplier",
        service_address="localhost",
        service_port=50053,
        registry_address="localhost:50051",
    )
    custom_trigger.serve()

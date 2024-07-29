import time
import random
from typing import Callable, Tuple
from pydantic import BaseModel, Field

from kin_sdk.trigger.base import BaseTrigger


class CronFibonacciInput(BaseModel):
    pass


class CronFibonacciOutput(BaseModel):
    initials_numbers: Tuple[int, int] = Field(
        ..., description="The first two numbers of fibonacci sequence"
    )


class CronFibonacciSetup(BaseModel):
    initials_numbers: Tuple[int, int] = Field(
        ..., description="The first two numbers of fibonacci sequence"
    )


class CronTrigger(
    BaseTrigger[CronFibonacciInput, CronFibonacciOutput, CronFibonacciSetup]
):
    name = "Cron Multiplier"
    description = "A simple cron that execute multiplier tool"
    input_format = CronFibonacciInput
    output_format = CronFibonacciOutput
    setup_format = CronFibonacciSetup

    def start(self) -> None:
        print("Executing cron job", self.name)

    def execute(
        self,
        input_data: CronFibonacciInput,
        setup_id: str,
        callback: Callable[[CronFibonacciOutput], None],
    ) -> None:
        counter = 0

        print("input_data", input_data)

        while counter < 10:
            # Implémentez la logique spécifique de l'outil ici
            exec_result = {"initials_numbers": [1, 1]}
            callback(CronFibonacciOutput(**exec_result))
            counter += 1
            time.sleep(1)
            print("here")

    def stop(self) -> None:
        print("Stopping cron job", self.name)


if __name__ == "__main__":
    # ! First start the service registry server from the examples.server_registry.py file
    test = {"input": {"last_numbers": [1, 2]}}
    # Create an instance of your custom tool
    cron_trigger = CronTrigger(
        service_id="services:fibonacci_triogger",
        service_address="localhost",
        service_port=50053,
        registry_address="localhost:50051",
    )
    cron_trigger.serve()

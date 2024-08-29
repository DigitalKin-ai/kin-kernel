# import time
# import random
from typing import Callable, Tuple
from pydantic import BaseModel, Field

from kin_sdk.agent_module import BaseTrigger


class CronFibonacciInput(BaseModel):
    """
    Input data for the cron job
    """


class CronFibonacciOutput(BaseModel):
    initial_numbers: Tuple[int, int] = Field(
        ..., description="The first two numbers of fibonacci sequence"
    )


class CronFibonacciSetup(BaseModel):
    initial_numbers: Tuple[int, int] = Field(
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

    def start(self, setup_id: str) -> None:
        print("Executing cron job", self.name, setup_id)

    def execute(
        self,
        input_data: CronFibonacciInput,
        setup_id: str,
        callback: Callable[[CronFibonacciOutput], None],
    ) -> None:

        print("input_data", input_data)
        exec_result = {"initial_numbers": [1, 1]}
        callback(CronFibonacciOutput(**exec_result))

        # counter = 0
        # while counter < 10:
        #     # Implémentez la logique spécifique de l'outil ici
        #     exec_result = {"initial_numbers": [1, 1]}
        #     callback(CronFibonacciOutput(**exec_result))
        #     counter += 1
        #     time.sleep(1)
        #     print("here")

    def stop(self) -> None:
        print("Stopping cron job", self.name)


if __name__ == "__main__":
    # ! First start the module registry server from the examples.server_registry.py file
    test = {"input": {"last_numbers": [1, 2]}}
    # Create an instance of your custom tool
    cron_trigger = CronTrigger(
        module_id="modules:fibonacci_triogger",
        module_address="localhost",
        module_port=50053,
        registry_address="localhost:50051",
    )
    cron_trigger.serve()

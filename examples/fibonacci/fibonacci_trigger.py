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

    def execute(
        self,
        input_data: CronFibonacciInput,
        setup_data: CronFibonacciSetup,
        callback: Callable[[CronFibonacciOutput], None],
    ) -> None:
        counter = 0
        start = random.randint(0, 100)

        print("input_data", input_data)

        while counter < 10:
            # Implémentez la logique spécifique de l'outil ici
            exec_result = {"numbers": setup_data.result, "factor": start + counter}
            callback(CronFibonacciOutput(**exec_result))
            counter += 1
            time.sleep(1)
            print("here")

    def start(self) -> None:
        print("Executing cron job", self.name)

    def stop(self) -> None:
        print("Stopping cron job", self.name)

"""
This module defines a gRPC-based Trigger Service with job management capabilities.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Callable

from pydantic import BaseModel

from kin_sdk.common.types import ModuleType
from kin_sdk.agent_module._module import BaseModule

InputModelT = TypeVar("InputModelT", bound=BaseModel)
OutputModelT = TypeVar("OutputModelT", bound=BaseModel)
SetupModelT = TypeVar("SetupModelT", bound=BaseModel)


class BaseTrigger(
    BaseModule[InputModelT, OutputModelT, SetupModelT], ABC
):  # , ModuleServer, ABC):
    """
    Abstract base class for defining a trigger.
    """

    _module_type: ModuleType = ModuleType.TRIGGER

    @abstractmethod
    async def start(self, setup_id: str) -> None:
        """
        Starts the trigger.
        """
        raise NotImplementedError("Trigger must implement 'start' abstract method")

    @abstractmethod
    async def execute(
        self,
        input_data: InputModelT,
        setup_id: str,
        callback: Callable[[OutputModelT], None],
    ) -> None:
        """
        Executes the trigger.

        :param input_data: The input data for the trigger.
        :param setup_id: The ID of the setup for the trigger.
        :param callback: The callback to call with the output data.
        """
        raise NotImplementedError("Trigger must implement 'execute' abstract method")

    @abstractmethod
    async def stop(self) -> None:
        """
        Stops the trigger.
        """
        raise NotImplementedError("Trigger must implement 'stop' abstract method")

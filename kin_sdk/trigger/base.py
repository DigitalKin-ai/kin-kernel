"""
This module defines a gRPC-based Trigger Service with job management capabilities.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Callable

from pydantic import BaseModel

from kin_sdk.common.types import ServiceType
from kin_sdk.service.base import BaseService

InputModelT = TypeVar("InputModelT", bound=BaseModel)
OutputModelT = TypeVar("OutputModelT", bound=BaseModel)
SetupModelT = TypeVar("SetupModelT", bound=BaseModel)


class BaseTrigger(
    BaseService[InputModelT, OutputModelT, SetupModelT], ABC
):  # , ServiceServer, ABC):
    """
    Abstract base class for defining a trigger.
    """

    def __init__(
        self,
        service_id: str,
        service_address: str,
        service_port: int,
        registry_address: str,
        max_workers: int = 10,
    ):
        """
        Initializes the BaseTrigger.

        :param service_id: The ID of the service.
        :param service_address: The address of the service.
        :param service_port: The port of the service.
        :param registry_address: The address of the registry.
        :param max_workers: The maximum number of worker threads.
        """
        super().__init__(
            service_id=service_id,
            service_address=service_address,
            service_port=service_port,
            service_type=ServiceType.TRIGGER,
            registry_address=registry_address,
            max_workers=max_workers,
        )

    @abstractmethod
    def start(self) -> None:
        """
        Starts the trigger.
        """
        raise NotImplementedError("Trigger must implement 'start' abstract method")

    @abstractmethod
    def execute(
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
    def stop(self) -> None:
        """
        Stops the trigger.
        """
        raise NotImplementedError("Trigger must implement 'stop' abstract method")

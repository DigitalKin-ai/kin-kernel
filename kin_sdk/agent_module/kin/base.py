"""
Todo: sphinx docstring
"""

from abc import ABC, abstractmethod
from typing import TypeVar, List, Callable

from pydantic import BaseModel

from kin_sdk.common.types import ModuleType
from kin_sdk.agent_module._module.base import BaseModule
from kin_sdk.agent_module.trigger.base import BaseTrigger
from kin_sdk.agent_module.tool.base import BaseTool

InputModelT = TypeVar("InputModelT", bound=BaseModel)
OutputModelT = TypeVar("OutputModelT", bound=BaseModel)
SetupModelT = TypeVar("SetupModelT", bound=BaseModel)


# ! TODO: changer l'architecture pour que nous ajoutions le BaseModule a serveur et qu'on run le serveur
# Ainsi le base module va dans le jobManager
class BaseKin(BaseModule[InputModelT, OutputModelT, SetupModelT], ABC):
    """TODO: Sphinx docstring"""

    triggers: List[BaseTrigger]
    tools: List[BaseTool]
    _module_type: ModuleType = ModuleType.KIN

    # ? do I need to override it in order to add the triggers and tools?
    # def __init_subclass__(cls, **kwargs):
    #     super().__init_subclass__(**kwargs)
    #     if not inspect.isabstract(cls):
    #         required_attrs = ["name", "description", "triggers", "tools"]
    #         for attr in required_attrs:
    #             if not hasattr(cls, attr) or getattr(cls, attr) is None:
    #                 raise TypeError(
    #                     f"Subclass '{cls.__name__}' must define a '{attr}' class variable."
    #                 )

    @abstractmethod
    async def start(self, setup_id: str) -> None:
        """
        Starts the kin.
        """
        raise NotImplementedError("Kin must implement 'start' abstract method")

    @abstractmethod
    async def execute(
        self,
        input_data: InputModelT,
        setup_id: str,
        callback: Callable[[OutputModelT], None],
    ) -> None:
        """
        Executes the kin.

        :param input_data: The input data for the kin.
        :param setup_id: The ID of the setup for the kin.
        :param callback: The callback to call with the output data.
        """
        raise NotImplementedError("Kin must implement 'execute' abstract method")

    @abstractmethod
    async def stop(self) -> None:
        """
        Stops the kin.
        """
        raise NotImplementedError("Kin must implement 'stop' abstract method")

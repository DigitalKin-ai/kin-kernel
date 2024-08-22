"""
TODO: sphinx docstring
"""

# from typing import Literal
from enum import Enum
from typing import Union


class ModuleType(Enum):
    """
    Enum for command types
    """

    UNKNOWN = "unknown"
    TRIGGER = "trigger"
    TOOL = "tool"
    KIN = "kin"
    VIEW = "view"

    @staticmethod
    def get(value: str, default: Union["ModuleType", None] = None) -> "ModuleType":
        """TODO: sphinx docstring"""
        return (
            ModuleType(value)
            if value in ModuleType._value2member_map_
            else default or ModuleType.UNKNOWN
        )


class RequestType(Enum):
    """
    Enum for command types
    """

    SEND = "SEND"
    EXIT = "EXIT"
    VALIDATE = "VALIDATE"
    DESTROY = "DESCTROY"

    @staticmethod
    def get(value: str, default: Union["RequestType", None] = None) -> "RequestType":
        """TODO: sphinx docstring"""
        return (
            RequestType(value)
            if value in RequestType._value2member_map_
            else default or RequestType.SEND
        )

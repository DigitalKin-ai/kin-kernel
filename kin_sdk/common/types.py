"""
TODO: sphinx docstring
"""

# from typing import Literal
from enum import Enum
from typing import Union


class ServiceType(Enum):
    """
    Enum for command types
    """

    UNKNOWN = "unknown"
    TRIGGER = "trigger"
    TOOL = "tool"
    KIN = "kin"
    VIEW = "view"

    @staticmethod
    def get(value: str, default: Union["ServiceType" | None] = None) -> "ServiceType":
        return (
            ServiceType(value)
            if value in ServiceType._value2member_map_
            else default or ServiceType.UNKNOWN
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
    def get(value: str, default: Union["RequestType" | None] = None) -> "RequestType":
        return (
            RequestType(value)
            if value in RequestType._value2member_map_
            else default or RequestType.SEND
        )

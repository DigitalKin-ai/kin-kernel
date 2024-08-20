"""
TODO: sphinx docstring
"""

# from typing import Literal
import warnings
from enum import Enum
from typing import Union


# ! Deprecated please remove
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
    def get(value: str, default: Union["ServiceType", None] = None) -> "ServiceType":
        return (
            ServiceType(value)
            if value in ServiceType._value2member_map_
            else default or ServiceType.UNKNOWN
        )


# Deprecate the old class
# TODO remove
class DeprecatedServiceType(ServiceType):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "ServiceType is deprecated, use ModuleType instead",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


# Alias the old class to the new one
ServiceType = DeprecatedServiceType


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
        return (
            RequestType(value)
            if value in RequestType._value2member_map_
            else default or RequestType.SEND
        )

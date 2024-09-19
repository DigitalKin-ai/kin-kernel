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

    REQUEST_TYPE_UNKNOWN = "REQUEST_TYPE_UNKNOWN"
    REQUEST_TYPE_CONNECTION = "REQUEST_TYPE_CONNECTION"
    REQUEST_TYPE_SEND = "REQUEST_TYPE_SEND"
    REQUEST_TYPE_EXIT = "REQUEST_TYPE_EXIT"
    REQUEST_TYPE_VALIDATE = "REQUEST_TYPE_VALIDATE"
    REQUEST_TYPE_DESTROY = "REQUEST_TYPE_DESTROY"

    @staticmethod
    def get(value: str, default: Union["RequestType", None] = None) -> "RequestType":
        """TODO: sphinx docstring"""
        return (
            RequestType(value)
            if value in RequestType._value2member_map_
            else default or RequestType.REQUEST_TYPE_SEND
        )


class ModuleRole(Enum):
    """
    Enum for command types
    """

    MODULE_ROLE_UNKNOWN = "MODULE_ROLE_UNKNOWN"
    MODULE_ROLE_OWNER = "MODULE_ROLE_OWNER"
    MODULE_ROLE_MEMBRE = "MODULE_ROLE_MEMBRE"

    @staticmethod
    def get(value: str, default: Union["ModuleRole", None] = None) -> "ModuleRole":
        """
        Get the ModuleRole enum from the given string value.

        :param value: The string value to convert to a ModuleRole enum
        :param default: The default value to return if the value is not found
        :return: The ModuleRole enum
        """
        return (
            ModuleRole(value)
            if value in ModuleRole._value2member_map_
            else default or ModuleRole.MODULE_ROLE_UNKNOWN
        )

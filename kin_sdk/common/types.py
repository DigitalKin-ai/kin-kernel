"""
TODO: sphinx docstring
"""

# from typing import Literal
from enum import Enum

# ServiceType = Literal["trigger", "tool", "kin"]


class ServiceType(Enum):
    """
    Enum for command types
    """

    UNKNOWN = "unknown"
    TRIGGER = "trigger"
    TOOL = "tool"
    KIN = "kin"


class RequestType(Enum):
    """
    Enum for command types
    """

    SEND = "SEND"
    EXIT = "EXIT"
    VALIDATE = "VALIDATE"
    DESTROY = "DESCTROY"

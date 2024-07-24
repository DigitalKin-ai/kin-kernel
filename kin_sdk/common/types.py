"""
TODO: sphinx docstring
"""

from typing import Literal
from enum import Enum

ServiceType = Literal["trigger", "tool", "kin"]


class RequestType(Enum):
    """
    Enum for command types
    """

    SEND = "send"
    EXIT = "exit"
    VALIDATE = "validate"
    DESTROY = "destroy"

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

    SEND = "SEND"
    EXIT = "EXIT"
    VALIDATE = "VALIDATE"
    DESTROY = "DESCTROY"

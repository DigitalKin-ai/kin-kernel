"""
This module contains the model for the module object.
"""

from pydantic import BaseModel

from kin_sdk.common.types import ModuleType


class ModuleModel(BaseModel):
    """TODO: sphinx docstring"""

    module_id: str
    module_type: ModuleType
    address: str
    port: int

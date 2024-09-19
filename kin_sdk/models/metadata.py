"""
TODO: sphinx docstring
"""

import uuid
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator
from pydantic_core import PydanticUndefinedType

from kin_sdk.common.types import ModuleRole


class Metadata(BaseModel):
    """
    Metadata model for gRPC module.

    :param module_id: The unique identifier of the module
    :param module_role: The role of the module (owner or member)
    :param room_id: The unique identifier of the room
    """

    module_id: str = Field(
        ..., description="The unique identifier of the module that send the request"
    )
    module_role: ModuleRole = Field(
        default=ModuleRole.MODULE_ROLE_MEMBRE,
        description="The role of the module that send the request",
    )
    room_id: Optional[uuid.UUID] = Field(
        None,
        description="The unique identifier of the room that the module is connected to",
    )

    @classmethod
    @model_validator(mode="before")
    def set_defaults_for_none(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """TODO: sphinx docstring"""
        fields = cls.model_fields
        for field_name, field_info in fields.items():
            value = values.get(field_name)
            default_value = (
                field_info.default
                if not isinstance(field_info.default, PydanticUndefinedType)
                else None
            )
            default_factory = (
                field_info.default_factory
                if not isinstance(field_info.default_factory, PydanticUndefinedType)
                else None
            )

            if value is None:
                if default_value is not None:
                    values[field_name] = default_value
                elif default_factory is not None:
                    values[field_name] = default_factory()

        return values

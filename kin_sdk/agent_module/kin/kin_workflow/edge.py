"""
TODO: Implement Edge class
"""

from typing import Dict, Union
from pydantic import BaseModel, Field


class SourceHandle(BaseModel):
    """TODO Sphinx docstring."""

    type: str = Field("", description="data type of the handled source")
    label: str = Field("", description="label of the handled source")


class TargetHandle(BaseModel):
    """TODO Sphinx docstring."""

    type: str = Field("", description="data type of the handled target")
    label: str = Field("", description="label of the handled target")


class Edge:
    """TODO Sphinx docstring."""

    def __init__(
        self,
        source: str,
        target: str,
        source_handle: Dict[str, str],
        target_handle: Dict[str, str],
    ):
        self.source = source
        self.target = target
        self.source_handle = SourceHandle(**source_handle)
        self.target_handle = TargetHandle(**target_handle)

    def __str__(self) -> str:
        return f"{self.source} -> {self.target} source_handle=({self.source_handle}) target_handle=({self.target_handle})"

    def __repr__(self) -> str:
        return str(self)

    def get_source_label(self) -> Union[str | None]:
        """TODO Sphinx docstring."""
        return self.source_handle.label or None

    def get_target_label(self) -> Union[str | None]:
        """TODO Sphinx docstring."""
        return self.target_handle.label or None

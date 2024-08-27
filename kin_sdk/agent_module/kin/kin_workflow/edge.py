"""
Module for defining edges in a graph with source and target handles.

This module includes classes for SourceHandle, TargetHandle, and Edge, which represent
the components of a graph edge and provide methods for accessing source and target labels.
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field


class SourceHandle(BaseModel):
    """
    Model for the source handle of an edge.

    Attributes:
        type (str): Data type of the handled source.
        label (str): Label of the handled source.
    """

    type: str = Field("", description="Data type of the handled source")
    label: str = Field("", description="Label of the handled source")


class TargetHandle(BaseModel):
    """
    Model for the target handle of an edge.

    Attributes:
        type (str): Data type of the handled target.
        label (str): Label of the handled target.
    """

    type: str = Field("", description="Data type of the handled target")
    label: str = Field("", description="Label of the handled target")


class Edge:
    """
    Represents an edge in the graph.

    Attributes:
        source (str): The unique identifier of the source node.
        target (str): The unique identifier of the target node.
        source_handle (SourceHandle): The handle for the source node.
        target_handle (TargetHandle): The handle for the target node.
    """

    def __init__(
        self,
        source: str,
        target: str,
        source_handle: Dict[str, str],
        target_handle: Dict[str, str],
    ):
        self._source = source
        self._target = target
        self._source_handle = SourceHandle(**source_handle)
        self._target_handle = TargetHandle(**target_handle)

    @property
    def source(self) -> str:
        """Get the source node ID."""
        return self._source

    @property
    def target(self) -> str:
        """Get the target node ID."""
        return self._target

    @property
    def source_handle(self) -> SourceHandle:
        """Get the source handle."""
        return self._source_handle

    @property
    def target_handle(self) -> TargetHandle:
        """Get the target handle."""
        return self._target_handle

    def __str__(self) -> str:
        return f"{self.source} -> {self.target} source_handle=({self.source_handle}) target_handle=({self.target_handle})"

    def __repr__(self) -> str:
        return str(self)

    def get_source_label(self) -> Optional[str]:
        """
        Get the label of the source handle.

        Returns:
            Optional[str]: The label of the source handle, or None if not set.
        """
        return self._source_handle.label or None

    def get_target_label(self) -> Optional[str]:
        """
        Get the label of the target handle.

        Returns:
            Optional[str]: The label of the target handle, or None if not set.
        """
        return self._target_handle.label or None

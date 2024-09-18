from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DataEdge(_message.Message):
    __slots__ = ("color", "running")
    COLOR_FIELD_NUMBER: _ClassVar[int]
    RUNNING_FIELD_NUMBER: _ClassVar[int]
    color: str
    running: bool
    def __init__(self, color: _Optional[str] = ..., running: bool = ...) -> None: ...

class Edge(_message.Message):
    __slots__ = ("id", "source", "source_handle", "target", "target_handle", "type", "data")
    ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_HANDLE_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    TARGET_HANDLE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    source: str
    source_handle: str
    target: str
    target_handle: str
    type: str
    data: DataEdge
    def __init__(self, id: _Optional[str] = ..., source: _Optional[str] = ..., source_handle: _Optional[str] = ..., target: _Optional[str] = ..., target_handle: _Optional[str] = ..., type: _Optional[str] = ..., data: _Optional[_Union[DataEdge, _Mapping]] = ...) -> None: ...

class AddEdgeWorkflowRequest(_message.Message):
    __slots__ = ("workflow_id", "edge")
    WORKFLOW_ID_FIELD_NUMBER: _ClassVar[int]
    EDGE_FIELD_NUMBER: _ClassVar[int]
    workflow_id: str
    edge: Edge
    def __init__(self, workflow_id: _Optional[str] = ..., edge: _Optional[_Union[Edge, _Mapping]] = ...) -> None: ...

class DeleteEdgeWorkflowRequest(_message.Message):
    __slots__ = ("workflow_id", "edge_id")
    WORKFLOW_ID_FIELD_NUMBER: _ClassVar[int]
    EDGE_ID_FIELD_NUMBER: _ClassVar[int]
    workflow_id: str
    edge_id: str
    def __init__(self, workflow_id: _Optional[str] = ..., edge_id: _Optional[str] = ...) -> None: ...

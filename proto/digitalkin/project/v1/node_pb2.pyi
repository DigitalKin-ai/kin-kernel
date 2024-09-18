from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Position(_message.Message):
    __slots__ = ("x", "y")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ...) -> None: ...

class Target(_message.Message):
    __slots__ = ("label", "type", "optional")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_FIELD_NUMBER: _ClassVar[int]
    label: str
    type: str
    optional: bool
    def __init__(self, label: _Optional[str] = ..., type: _Optional[str] = ..., optional: bool = ...) -> None: ...

class Source(_message.Message):
    __slots__ = ("label", "type")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    label: str
    type: str
    def __init__(self, label: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class DataNode(_message.Message):
    __slots__ = ("id", "name", "type", "color", "targets", "sources")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    TARGETS_FIELD_NUMBER: _ClassVar[int]
    SOURCES_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    type: str
    color: str
    targets: _containers.RepeatedCompositeFieldContainer[Target]
    sources: _containers.RepeatedCompositeFieldContainer[Source]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[str] = ..., color: _Optional[str] = ..., targets: _Optional[_Iterable[_Union[Target, _Mapping]]] = ..., sources: _Optional[_Iterable[_Union[Source, _Mapping]]] = ...) -> None: ...

class Measured(_message.Message):
    __slots__ = ("width", "height")
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    width: int
    height: int
    def __init__(self, width: _Optional[int] = ..., height: _Optional[int] = ...) -> None: ...

class Node(_message.Message):
    __slots__ = ("id", "type", "position", "data", "measured", "selected", "dragging")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    MEASURED_FIELD_NUMBER: _ClassVar[int]
    SELECTED_FIELD_NUMBER: _ClassVar[int]
    DRAGGING_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    position: Position
    data: DataNode
    measured: Measured
    selected: bool
    dragging: bool
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ..., position: _Optional[_Union[Position, _Mapping]] = ..., data: _Optional[_Union[DataNode, _Mapping]] = ..., measured: _Optional[_Union[Measured, _Mapping]] = ..., selected: bool = ..., dragging: bool = ...) -> None: ...

class ReadDataNodesListResponse(_message.Message):
    __slots__ = ("data_nodes",)
    DATA_NODES_FIELD_NUMBER: _ClassVar[int]
    data_nodes: _containers.RepeatedCompositeFieldContainer[DataNode]
    def __init__(self, data_nodes: _Optional[_Iterable[_Union[DataNode, _Mapping]]] = ...) -> None: ...

class AddNodeWorkflowRequest(_message.Message):
    __slots__ = ("workflow_id", "node")
    WORKFLOW_ID_FIELD_NUMBER: _ClassVar[int]
    NODE_FIELD_NUMBER: _ClassVar[int]
    workflow_id: str
    node: Node
    def __init__(self, workflow_id: _Optional[str] = ..., node: _Optional[_Union[Node, _Mapping]] = ...) -> None: ...

class UpdateNodePositionWorkflowRequest(_message.Message):
    __slots__ = ("workflow_id", "node_id", "position")
    WORKFLOW_ID_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    workflow_id: str
    node_id: str
    position: Position
    def __init__(self, workflow_id: _Optional[str] = ..., node_id: _Optional[str] = ..., position: _Optional[_Union[Position, _Mapping]] = ...) -> None: ...

class DeleteNodeWorkflowRequest(_message.Message):
    __slots__ = ("workflow_id", "node_id")
    WORKFLOW_ID_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    workflow_id: str
    node_id: str
    def __init__(self, workflow_id: _Optional[str] = ..., node_id: _Optional[str] = ...) -> None: ...

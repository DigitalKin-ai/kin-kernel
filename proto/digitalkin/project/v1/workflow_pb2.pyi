from digitalkin.project.v1 import edge_pb2 as _edge_pb2
from digitalkin.project.v1 import node_pb2 as _node_pb2
from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Workflow(_message.Message):
    __slots__ = ("id", "edges", "nodes")
    ID_FIELD_NUMBER: _ClassVar[int]
    EDGES_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    id: str
    edges: _containers.RepeatedCompositeFieldContainer[_edge_pb2.Edge]
    nodes: _containers.RepeatedCompositeFieldContainer[_node_pb2.Node]
    def __init__(self, id: _Optional[str] = ..., edges: _Optional[_Iterable[_Union[_edge_pb2.Edge, _Mapping]]] = ..., nodes: _Optional[_Iterable[_Union[_node_pb2.Node, _Mapping]]] = ...) -> None: ...

class CreateWorkflowRequest(_message.Message):
    __slots__ = ("kin_id", "workflow")
    KIN_ID_FIELD_NUMBER: _ClassVar[int]
    WORKFLOW_FIELD_NUMBER: _ClassVar[int]
    kin_id: str
    workflow: Workflow
    def __init__(self, kin_id: _Optional[str] = ..., workflow: _Optional[_Union[Workflow, _Mapping]] = ...) -> None: ...

class ReadWorkflowRequest(_message.Message):
    __slots__ = ("kin_id",)
    KIN_ID_FIELD_NUMBER: _ClassVar[int]
    kin_id: str
    def __init__(self, kin_id: _Optional[str] = ...) -> None: ...

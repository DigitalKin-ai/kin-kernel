from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Data(_message.Message):
    __slots__ = ("module_id", "node_id", "content")
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    module_id: str
    node_id: str
    content: _struct_pb2.Struct
    def __init__(self, module_id: _Optional[str] = ..., node_id: _Optional[str] = ..., content: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class Setup(_message.Message):
    __slots__ = ("id", "name", "kin_id", "data", "creation_date")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    KIN_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    CREATION_DATE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    kin_id: str
    data: _containers.RepeatedCompositeFieldContainer[Data]
    creation_date: int
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., kin_id: _Optional[str] = ..., data: _Optional[_Iterable[_Union[Data, _Mapping]]] = ..., creation_date: _Optional[int] = ...) -> None: ...

class ReadSetupRequest(_message.Message):
    __slots__ = ("setup_id",)
    SETUP_ID_FIELD_NUMBER: _ClassVar[int]
    setup_id: str
    def __init__(self, setup_id: _Optional[str] = ...) -> None: ...

class ReadSetupResponse(_message.Message):
    __slots__ = ("setup",)
    SETUP_FIELD_NUMBER: _ClassVar[int]
    setup: Setup
    def __init__(self, setup: _Optional[_Union[Setup, _Mapping]] = ...) -> None: ...

class GetNodeSetupRequest(_message.Message):
    __slots__ = ("setup_id", "node_id")
    SETUP_ID_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    setup_id: str
    node_id: str
    def __init__(self, setup_id: _Optional[str] = ..., node_id: _Optional[str] = ...) -> None: ...

class GetNodeSetupResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: Data
    def __init__(self, data: _Optional[_Union[Data, _Mapping]] = ...) -> None: ...

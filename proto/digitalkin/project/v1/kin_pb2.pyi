from digitalkin.common.v1 import common_pb2 as _common_pb2
from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Kin(_message.Message):
    __slots__ = ("id", "name", "origin_address", "threads", "workflow")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    THREADS_FIELD_NUMBER: _ClassVar[int]
    WORKFLOW_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    origin_address: str
    threads: _containers.RepeatedCompositeFieldContainer[_common_pb2.ThreadReply]
    workflow: _common_pb2.WorkflowReply
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., origin_address: _Optional[str] = ..., threads: _Optional[_Iterable[_Union[_common_pb2.ThreadReply, _Mapping]]] = ..., workflow: _Optional[_Union[_common_pb2.WorkflowReply, _Mapping]] = ...) -> None: ...

class ReadKinRequest(_message.Message):
    __slots__ = ("kin_id",)
    KIN_ID_FIELD_NUMBER: _ClassVar[int]
    kin_id: str
    def __init__(self, kin_id: _Optional[str] = ...) -> None: ...

class UpdateKinOriginAddressRequest(_message.Message):
    __slots__ = ("kin_id", "origin_address")
    KIN_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    kin_id: str
    origin_address: str
    def __init__(self, kin_id: _Optional[str] = ..., origin_address: _Optional[str] = ...) -> None: ...

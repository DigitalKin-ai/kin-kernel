from digitalkin.common.v1 import common_pb2 as _common_pb2
from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MessageRequest(_message.Message):
    __slots__ = ("thread_id", "organization_id", "message", "files")
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    thread_id: str
    organization_id: str
    message: str
    files: _containers.RepeatedCompositeFieldContainer[_common_pb2.File]
    def __init__(self, thread_id: _Optional[str] = ..., organization_id: _Optional[str] = ..., message: _Optional[str] = ..., files: _Optional[_Iterable[_Union[_common_pb2.File, _Mapping]]] = ...) -> None: ...

class MessageResponse(_message.Message):
    __slots__ = ("content",)
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    content: str
    def __init__(self, content: _Optional[str] = ...) -> None: ...

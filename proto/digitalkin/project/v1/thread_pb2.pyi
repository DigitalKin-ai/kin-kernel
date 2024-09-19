from digitalkin.common.v1 import common_pb2 as _common_pb2
from digitalkin.project.v1 import response_pb2 as _response_pb2
from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Thread(_message.Message):
    __slots__ = ("id", "thread_subject", "responses")
    ID_FIELD_NUMBER: _ClassVar[int]
    THREAD_SUBJECT_FIELD_NUMBER: _ClassVar[int]
    RESPONSES_FIELD_NUMBER: _ClassVar[int]
    id: str
    thread_subject: str
    responses: _containers.RepeatedCompositeFieldContainer[_response_pb2.Response]
    def __init__(self, id: _Optional[str] = ..., thread_subject: _Optional[str] = ..., responses: _Optional[_Iterable[_Union[_response_pb2.Response, _Mapping]]] = ...) -> None: ...

class CreateThreadRequest(_message.Message):
    __slots__ = ("kin_id", "setup_id")
    KIN_ID_FIELD_NUMBER: _ClassVar[int]
    SETUP_ID_FIELD_NUMBER: _ClassVar[int]
    kin_id: str
    setup_id: str
    def __init__(self, kin_id: _Optional[str] = ..., setup_id: _Optional[str] = ...) -> None: ...

class ReadThreadRequest(_message.Message):
    __slots__ = ("thread_id",)
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    thread_id: str
    def __init__(self, thread_id: _Optional[str] = ...) -> None: ...

class DeleteThreadRequest(_message.Message):
    __slots__ = ("thread_id",)
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    thread_id: str
    def __init__(self, thread_id: _Optional[str] = ...) -> None: ...

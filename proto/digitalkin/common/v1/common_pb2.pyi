from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Thing(_message.Message):
    __slots__ = ("id", "tb")
    ID_FIELD_NUMBER: _ClassVar[int]
    TB_FIELD_NUMBER: _ClassVar[int]
    id: str
    tb: str
    def __init__(self, id: _Optional[str] = ..., tb: _Optional[str] = ...) -> None: ...

class File(_message.Message):
    __slots__ = ("name", "type", "content")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    content: bytes
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ..., content: _Optional[bytes] = ...) -> None: ...

class UserReply(_message.Message):
    __slots__ = ("user_name", "first_name", "last_name", "email", "avatar", "activated")
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    AVATAR_FIELD_NUMBER: _ClassVar[int]
    ACTIVATED_FIELD_NUMBER: _ClassVar[int]
    user_name: str
    first_name: str
    last_name: str
    email: str
    avatar: str
    activated: bool
    def __init__(self, user_name: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., email: _Optional[str] = ..., avatar: _Optional[str] = ..., activated: bool = ...) -> None: ...

class KinReply(_message.Message):
    __slots__ = ("id", "name", "description", "activated")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ACTIVATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    activated: bool
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., activated: bool = ...) -> None: ...

class ThreadReply(_message.Message):
    __slots__ = ("id", "thread_subject", "activated")
    ID_FIELD_NUMBER: _ClassVar[int]
    THREAD_SUBJECT_FIELD_NUMBER: _ClassVar[int]
    ACTIVATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    thread_subject: str
    activated: bool
    def __init__(self, id: _Optional[str] = ..., thread_subject: _Optional[str] = ..., activated: bool = ...) -> None: ...

class WorkflowReply(_message.Message):
    __slots__ = ("id", "name", "status", "duration", "price")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    status: str
    duration: _timestamp_pb2.Timestamp
    price: int
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., status: _Optional[str] = ..., duration: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., price: _Optional[int] = ...) -> None: ...

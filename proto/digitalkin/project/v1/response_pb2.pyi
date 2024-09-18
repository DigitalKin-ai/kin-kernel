from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STATUS_UNKNOWN: _ClassVar[Status]
    STATUS_PENDING: _ClassVar[Status]
    STATUS_DONE: _ClassVar[Status]
    STATUS_ERROR: _ClassVar[Status]
    STATUS_WAITING: _ClassVar[Status]

class Role(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROLE_UNKNOWN: _ClassVar[Role]
    ROLE_USER: _ClassVar[Role]
    ROLE_ASSISTANT: _ClassVar[Role]
STATUS_UNKNOWN: Status
STATUS_PENDING: Status
STATUS_DONE: Status
STATUS_ERROR: Status
STATUS_WAITING: Status
ROLE_UNKNOWN: Role
ROLE_USER: Role
ROLE_ASSISTANT: Role

class Response(_message.Message):
    __slots__ = ("id", "role", "status", "content", "create_date", "origin_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    CREATE_DATE_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    role: Role
    status: Status
    content: str
    create_date: _timestamp_pb2.Timestamp
    origin_id: str
    def __init__(self, id: _Optional[str] = ..., role: _Optional[_Union[Role, str]] = ..., status: _Optional[_Union[Status, str]] = ..., content: _Optional[str] = ..., create_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., origin_id: _Optional[str] = ...) -> None: ...

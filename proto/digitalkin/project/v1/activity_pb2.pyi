from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Activity(_message.Message):
    __slots__ = ("id", "kin_id", "status", "kin_name", "workflow_name", "subject", "date", "duration", "price")
    ID_FIELD_NUMBER: _ClassVar[int]
    KIN_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    KIN_NAME_FIELD_NUMBER: _ClassVar[int]
    WORKFLOW_NAME_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    id: str
    kin_id: str
    status: str
    kin_name: str
    workflow_name: str
    subject: str
    date: _timestamp_pb2.Timestamp
    duration: _timestamp_pb2.Timestamp
    price: float
    def __init__(self, id: _Optional[str] = ..., kin_id: _Optional[str] = ..., status: _Optional[str] = ..., kin_name: _Optional[str] = ..., workflow_name: _Optional[str] = ..., subject: _Optional[str] = ..., date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., duration: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., price: _Optional[float] = ...) -> None: ...

class ReadActivitiesRequest(_message.Message):
    __slots__ = ("kin_id",)
    KIN_ID_FIELD_NUMBER: _ClassVar[int]
    kin_id: str
    def __init__(self, kin_id: _Optional[str] = ...) -> None: ...

class Activities(_message.Message):
    __slots__ = ("activities",)
    ACTIVITIES_FIELD_NUMBER: _ClassVar[int]
    activities: _containers.RepeatedCompositeFieldContainer[Activity]
    def __init__(self, activities: _Optional[_Iterable[_Union[Activity, _Mapping]]] = ...) -> None: ...

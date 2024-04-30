from google.protobuf import struct_pb2 as _struct_pb2
from proto.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

CANCELED: KinStatus
DESCRIPTOR: _descriptor.FileDescriptor
EXPIRED: KinStatus
FAILED: KinStatus
PROCESSING: KinStatus
STARTING: KinStatus
STOPPED: KinStatus
SUCCESS: KinStatus

class GetKinStatusRequest(_message.Message):
    __slots__ = ["kin_id"]
    KIN_ID_FIELD_NUMBER: _ClassVar[int]
    kin_id: str
    def __init__(self, kin_id: _Optional[str] = ...) -> None: ...

class KinResponse(_message.Message):
    __slots__ = ["kin_id", "message", "success"]
    KIN_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    kin_id: str
    message: str
    success: bool
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., kin_id: _Optional[str] = ...) -> None: ...

class KinStatusResponse(_message.Message):
    __slots__ = ["kin_id", "status", "success"]
    KIN_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    kin_id: str
    status: KinStatus
    success: bool
    def __init__(self, success: bool = ..., status: _Optional[_Union[KinStatus, str]] = ..., kin_id: _Optional[str] = ...) -> None: ...

class StartKinRequest(_message.Message):
    __slots__ = ["input", "kin_id", "setup", "trigger_id"]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    KIN_ID_FIELD_NUMBER: _ClassVar[int]
    SETUP_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_ID_FIELD_NUMBER: _ClassVar[int]
    input: _struct_pb2.Struct
    kin_id: str
    setup: _struct_pb2.Struct
    trigger_id: str
    def __init__(self, input: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., setup: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., kin_id: _Optional[str] = ..., trigger_id: _Optional[str] = ...) -> None: ...

class StopKinRequest(_message.Message):
    __slots__ = ["kin_id"]
    KIN_ID_FIELD_NUMBER: _ClassVar[int]
    kin_id: str
    def __init__(self, kin_id: _Optional[str] = ...) -> None: ...

class KinStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

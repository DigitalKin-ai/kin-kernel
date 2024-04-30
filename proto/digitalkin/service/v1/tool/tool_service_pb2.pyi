from google.protobuf import struct_pb2 as _struct_pb2
from proto.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExecuteRequest(_message.Message):
    __slots__ = ["input", "mission_id", "service_ids", "setup", "tool_id"]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    MISSION_ID_FIELD_NUMBER: _ClassVar[int]
    SERVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    SETUP_FIELD_NUMBER: _ClassVar[int]
    TOOL_ID_FIELD_NUMBER: _ClassVar[int]
    input: _struct_pb2.Struct
    mission_id: str
    service_ids: _containers.RepeatedScalarFieldContainer[str]
    setup: _struct_pb2.Struct
    tool_id: str
    def __init__(self, input: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., setup: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., service_ids: _Optional[_Iterable[str]] = ..., tool_id: _Optional[str] = ..., mission_id: _Optional[str] = ...) -> None: ...

class ExecuteResponse(_message.Message):
    __slots__ = ["output", "success"]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    output: _struct_pb2.Struct
    success: bool
    def __init__(self, success: bool = ..., output: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

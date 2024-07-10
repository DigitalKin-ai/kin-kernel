from google.protobuf import struct_pb2 as _struct_pb2
from proto.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

CANCELED: TriggerStatus
DESCRIPTOR: _descriptor.FileDescriptor
EXPIRED: TriggerStatus
FAILED: TriggerStatus
PROCESSING: TriggerStatus
STARTING: TriggerStatus
STOPPED: TriggerStatus
SUCCESS: TriggerStatus

class GetTriggerInputRequest(_message.Message):
    __slots__ = ["llm_format", "trigger_id"]
    LLM_FORMAT_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_ID_FIELD_NUMBER: _ClassVar[int]
    llm_format: bool
    trigger_id: str
    def __init__(self, trigger_id: _Optional[str] = ..., llm_format: bool = ...) -> None: ...

class GetTriggerOutputRequest(_message.Message):
    __slots__ = ["llm_format", "trigger_id"]
    LLM_FORMAT_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_ID_FIELD_NUMBER: _ClassVar[int]
    llm_format: bool
    trigger_id: str
    def __init__(self, trigger_id: _Optional[str] = ..., llm_format: bool = ...) -> None: ...

class GetTriggerStatusRequest(_message.Message):
    __slots__ = ["trigger_id"]
    TRIGGER_ID_FIELD_NUMBER: _ClassVar[int]
    trigger_id: str
    def __init__(self, trigger_id: _Optional[str] = ...) -> None: ...

class StartTriggerRequest(_message.Message):
    __slots__ = ["input", "service_ids", "setup"]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    SERVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    SETUP_FIELD_NUMBER: _ClassVar[int]
    input: _struct_pb2.Struct
    service_ids: _containers.RepeatedScalarFieldContainer[str]
    setup: _struct_pb2.Struct
    def __init__(self, input: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., setup: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., service_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class StopTriggerRequest(_message.Message):
    __slots__ = ["trigger_id"]
    TRIGGER_ID_FIELD_NUMBER: _ClassVar[int]
    trigger_id: str
    def __init__(self, trigger_id: _Optional[str] = ...) -> None: ...

class TriggerInputResponse(_message.Message):
    __slots__ = ["input_schema", "success"]
    INPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    input_schema: _struct_pb2.Struct
    success: bool
    def __init__(self, success: bool = ..., input_schema: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class TriggerOutputResponse(_message.Message):
    __slots__ = ["output_schema", "success"]
    OUTPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    output_schema: _struct_pb2.Struct
    success: bool
    def __init__(self, success: bool = ..., output_schema: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class TriggerResponse(_message.Message):
    __slots__ = ["message", "success", "trigger_id"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_ID_FIELD_NUMBER: _ClassVar[int]
    message: str
    success: bool
    trigger_id: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., trigger_id: _Optional[str] = ...) -> None: ...

class TriggerStatusResponse(_message.Message):
    __slots__ = ["status", "success", "trigger_id"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_ID_FIELD_NUMBER: _ClassVar[int]
    status: TriggerStatus
    success: bool
    trigger_id: str
    def __init__(self, success: bool = ..., status: _Optional[_Union[TriggerStatus, str]] = ..., trigger_id: _Optional[str] = ...) -> None: ...

class TriggerStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

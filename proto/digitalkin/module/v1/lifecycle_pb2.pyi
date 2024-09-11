from google.protobuf import struct_pb2 as _struct_pb2
from proto.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
REQUEST_TYPE_DESTROY: RequestType
REQUEST_TYPE_EXIT: RequestType
REQUEST_TYPE_SEND: RequestType
REQUEST_TYPE_UNKNOWN: RequestType
REQUEST_TYPE_VALIDATE: RequestType
START_RESPONSE_TYPE_CONNECTION: StartResponseType
START_RESPONSE_TYPE_ERROR: StartResponseType
START_RESPONSE_TYPE_INPUT: StartResponseType
START_RESPONSE_TYPE_OUTPUT: StartResponseType
START_RESPONSE_TYPE_UNKNOWN: StartResponseType

class ConnectionResponse(_message.Message):
    __slots__ = ["message", "room_id"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    message: str
    room_id: str
    def __init__(self, message: _Optional[str] = ..., room_id: _Optional[str] = ...) -> None: ...

class ErrorResponse(_message.Message):
    __slots__ = ["details", "message"]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    details: str
    message: str
    def __init__(self, message: _Optional[str] = ..., details: _Optional[str] = ...) -> None: ...

class InputDataResponse(_message.Message):
    __slots__ = ["input", "message"]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    input: _struct_pb2.Struct
    message: str
    def __init__(self, message: _Optional[str] = ..., input: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class OutputDataResponse(_message.Message):
    __slots__ = ["job_id", "message", "output"]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    message: str
    output: _struct_pb2.Struct
    def __init__(self, message: _Optional[str] = ..., output: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., job_id: _Optional[str] = ...) -> None: ...

class StartModuleRequest(_message.Message):
    __slots__ = ["input", "module_ids", "request_type", "setup_id"]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    MODULE_IDS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_TYPE_FIELD_NUMBER: _ClassVar[int]
    SETUP_ID_FIELD_NUMBER: _ClassVar[int]
    input: _struct_pb2.Struct
    module_ids: _containers.RepeatedScalarFieldContainer[str]
    request_type: RequestType
    setup_id: str
    def __init__(self, input: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., setup_id: _Optional[str] = ..., module_ids: _Optional[_Iterable[str]] = ..., request_type: _Optional[_Union[RequestType, str]] = ...) -> None: ...

class StartModuleResponse(_message.Message):
    __slots__ = ["connection", "error", "input_response", "module_id", "output_response", "response_type", "success"]
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    INPUT_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    connection: ConnectionResponse
    error: ErrorResponse
    input_response: InputDataResponse
    module_id: str
    output_response: OutputDataResponse
    response_type: StartResponseType
    success: bool
    def __init__(self, success: bool = ..., response_type: _Optional[_Union[StartResponseType, str]] = ..., connection: _Optional[_Union[ConnectionResponse, _Mapping]] = ..., input_response: _Optional[_Union[InputDataResponse, _Mapping]] = ..., output_response: _Optional[_Union[OutputDataResponse, _Mapping]] = ..., error: _Optional[_Union[ErrorResponse, _Mapping]] = ..., module_id: _Optional[str] = ...) -> None: ...

class StopModuleRequest(_message.Message):
    __slots__ = ["job_id"]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    def __init__(self, job_id: _Optional[str] = ...) -> None: ...

class StopModuleResponse(_message.Message):
    __slots__ = ["job_id", "message", "success"]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    message: str
    success: bool
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., job_id: _Optional[str] = ...) -> None: ...

class RequestType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class StartResponseType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

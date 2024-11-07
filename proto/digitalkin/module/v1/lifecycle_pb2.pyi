from buf.validate import validate_pb2 as _validate_pb2
from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RequestType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REQUEST_TYPE_UNKNOWN: _ClassVar[RequestType]
    REQUEST_TYPE_CONNECTION: _ClassVar[RequestType]
    REQUEST_TYPE_SEND: _ClassVar[RequestType]
    REQUEST_TYPE_EXIT: _ClassVar[RequestType]
    REQUEST_TYPE_VALIDATE: _ClassVar[RequestType]
    REQUEST_TYPE_DESTROY: _ClassVar[RequestType]

class StartResponseType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    START_RESPONSE_TYPE_UNKNOWN: _ClassVar[StartResponseType]
    START_RESPONSE_TYPE_CONNECTION: _ClassVar[StartResponseType]
    START_RESPONSE_TYPE_INPUT: _ClassVar[StartResponseType]
    START_RESPONSE_TYPE_OUTPUT: _ClassVar[StartResponseType]
    START_RESPONSE_TYPE_ERROR: _ClassVar[StartResponseType]

class ModuleRole(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MODULE_ROLE_UNKNOWN: _ClassVar[ModuleRole]
    MODULE_ROLE_OWNER: _ClassVar[ModuleRole]
    MODULE_ROLE_MEMBRE: _ClassVar[ModuleRole]
REQUEST_TYPE_UNKNOWN: RequestType
REQUEST_TYPE_CONNECTION: RequestType
REQUEST_TYPE_SEND: RequestType
REQUEST_TYPE_EXIT: RequestType
REQUEST_TYPE_VALIDATE: RequestType
REQUEST_TYPE_DESTROY: RequestType
START_RESPONSE_TYPE_UNKNOWN: StartResponseType
START_RESPONSE_TYPE_CONNECTION: StartResponseType
START_RESPONSE_TYPE_INPUT: StartResponseType
START_RESPONSE_TYPE_OUTPUT: StartResponseType
START_RESPONSE_TYPE_ERROR: StartResponseType
MODULE_ROLE_UNKNOWN: ModuleRole
MODULE_ROLE_OWNER: ModuleRole
MODULE_ROLE_MEMBRE: ModuleRole

class ConnectionRequest(_message.Message):
    __slots__ = ("room_id", "module_id", "module_role")
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    MODULE_ROLE_FIELD_NUMBER: _ClassVar[int]
    room_id: str
    module_id: str
    module_role: ModuleRole
    def __init__(self, room_id: _Optional[str] = ..., module_id: _Optional[str] = ..., module_role: _Optional[_Union[ModuleRole, str]] = ...) -> None: ...

class InputDataRequest(_message.Message):
    __slots__ = ("input", "setup_id", "instance_id", "module_ids")
    INPUT_FIELD_NUMBER: _ClassVar[int]
    SETUP_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    MODULE_IDS_FIELD_NUMBER: _ClassVar[int]
    input: _struct_pb2.Struct
    setup_id: str
    instance_id: str
    module_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, input: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., setup_id: _Optional[str] = ..., instance_id: _Optional[str] = ..., module_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class StartModuleRequest(_message.Message):
    __slots__ = ("request_type", "connection_request", "input_request")
    REQUEST_TYPE_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_REQUEST_FIELD_NUMBER: _ClassVar[int]
    INPUT_REQUEST_FIELD_NUMBER: _ClassVar[int]
    request_type: RequestType
    connection_request: ConnectionRequest
    input_request: InputDataRequest
    def __init__(self, request_type: _Optional[_Union[RequestType, str]] = ..., connection_request: _Optional[_Union[ConnectionRequest, _Mapping]] = ..., input_request: _Optional[_Union[InputDataRequest, _Mapping]] = ...) -> None: ...

class StopModuleRequest(_message.Message):
    __slots__ = ("job_id",)
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    def __init__(self, job_id: _Optional[str] = ...) -> None: ...

class ConnectionResponse(_message.Message):
    __slots__ = ("message", "room_id")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    message: str
    room_id: str
    def __init__(self, message: _Optional[str] = ..., room_id: _Optional[str] = ...) -> None: ...

class InputDataResponse(_message.Message):
    __slots__ = ("message", "input")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    message: str
    input: _struct_pb2.Struct
    def __init__(self, message: _Optional[str] = ..., input: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class OutputDataResponse(_message.Message):
    __slots__ = ("message", "output", "job_id")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    message: str
    output: _struct_pb2.Struct
    job_id: str
    def __init__(self, message: _Optional[str] = ..., output: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., job_id: _Optional[str] = ...) -> None: ...

class ErrorResponse(_message.Message):
    __slots__ = ("message", "details")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    message: str
    details: str
    def __init__(self, message: _Optional[str] = ..., details: _Optional[str] = ...) -> None: ...

class StartModuleResponse(_message.Message):
    __slots__ = ("success", "response_type", "connection", "input_response", "output_response", "error", "module_id")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    INPUT_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    success: bool
    response_type: StartResponseType
    connection: ConnectionResponse
    input_response: InputDataResponse
    output_response: OutputDataResponse
    error: ErrorResponse
    module_id: str
    def __init__(self, success: bool = ..., response_type: _Optional[_Union[StartResponseType, str]] = ..., connection: _Optional[_Union[ConnectionResponse, _Mapping]] = ..., input_response: _Optional[_Union[InputDataResponse, _Mapping]] = ..., output_response: _Optional[_Union[OutputDataResponse, _Mapping]] = ..., error: _Optional[_Union[ErrorResponse, _Mapping]] = ..., module_id: _Optional[str] = ...) -> None: ...

class StopModuleResponse(_message.Message):
    __slots__ = ("success", "message", "job_id")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    job_id: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., job_id: _Optional[str] = ...) -> None: ...

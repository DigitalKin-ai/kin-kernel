from google.protobuf import struct_pb2 as _struct_pb2
from proto.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

CANCELED: ServiceStatus
DESCRIPTOR: _descriptor.FileDescriptor
DESTROY: RequestType
EXIT: RequestType
EXPIRED: ServiceStatus
FAILED: ServiceStatus
PROCESSING: ServiceStatus
SEND: RequestType
STARTING: ServiceStatus
STOPPED: ServiceStatus
SUCCESS: ServiceStatus
VALIDATE: RequestType

class GetServiceInputRequest(_message.Message):
    __slots__ = ["llm_format", "service_id"]
    LLM_FORMAT_FIELD_NUMBER: _ClassVar[int]
    SERVICE_ID_FIELD_NUMBER: _ClassVar[int]
    llm_format: bool
    service_id: str
    def __init__(self, service_id: _Optional[str] = ..., llm_format: bool = ...) -> None: ...

class GetServiceOutputRequest(_message.Message):
    __slots__ = ["llm_format", "service_id"]
    LLM_FORMAT_FIELD_NUMBER: _ClassVar[int]
    SERVICE_ID_FIELD_NUMBER: _ClassVar[int]
    llm_format: bool
    service_id: str
    def __init__(self, service_id: _Optional[str] = ..., llm_format: bool = ...) -> None: ...

class GetServiceStatusRequest(_message.Message):
    __slots__ = ["job_id"]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    def __init__(self, job_id: _Optional[str] = ...) -> None: ...

class ServiceInputResponse(_message.Message):
    __slots__ = ["input_schema", "success"]
    INPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    input_schema: _struct_pb2.Struct
    success: bool
    def __init__(self, success: bool = ..., input_schema: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class ServiceOutputResponse(_message.Message):
    __slots__ = ["output_schema", "success"]
    OUTPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    output_schema: _struct_pb2.Struct
    success: bool
    def __init__(self, success: bool = ..., output_schema: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class ServiceResponse(_message.Message):
    __slots__ = ["message", "service_id", "success"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SERVICE_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    message: str
    service_id: str
    success: bool
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., service_id: _Optional[str] = ...) -> None: ...

class ServiceStatusResponse(_message.Message):
    __slots__ = ["job_id", "status", "success"]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    status: ServiceStatus
    success: bool
    def __init__(self, success: bool = ..., status: _Optional[_Union[ServiceStatus, str]] = ..., job_id: _Optional[str] = ...) -> None: ...

class StartServiceRequest(_message.Message):
    __slots__ = ["input", "request_type", "service_ids", "setup_id"]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    REQUEST_TYPE_FIELD_NUMBER: _ClassVar[int]
    SERVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    SETUP_ID_FIELD_NUMBER: _ClassVar[int]
    input: _struct_pb2.Struct
    request_type: RequestType
    service_ids: _containers.RepeatedScalarFieldContainer[str]
    setup_id: str
    def __init__(self, input: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., setup_id: _Optional[str] = ..., service_ids: _Optional[_Iterable[str]] = ..., request_type: _Optional[_Union[RequestType, str]] = ...) -> None: ...

class StopServiceRequest(_message.Message):
    __slots__ = ["service_id"]
    SERVICE_ID_FIELD_NUMBER: _ClassVar[int]
    service_id: str
    def __init__(self, service_id: _Optional[str] = ...) -> None: ...

class ServiceStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class RequestType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

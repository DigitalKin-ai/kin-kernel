from proto.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
MODULE_STATUS_CANCELED: ModuleStatus
MODULE_STATUS_EXPIRED: ModuleStatus
MODULE_STATUS_FAILED: ModuleStatus
MODULE_STATUS_PROCESSING: ModuleStatus
MODULE_STATUS_STARTING: ModuleStatus
MODULE_STATUS_STOPPED: ModuleStatus
MODULE_STATUS_SUCCESS: ModuleStatus
MODULE_STATUS_UNKNOWN: ModuleStatus

class GetModuleStatusRequest(_message.Message):
    __slots__ = ["job_id"]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    def __init__(self, job_id: _Optional[str] = ...) -> None: ...

class GetModuleStatusResponse(_message.Message):
    __slots__ = ["job_id", "status", "success"]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    status: ModuleStatus
    success: bool
    def __init__(self, success: bool = ..., status: _Optional[_Union[ModuleStatus, str]] = ..., job_id: _Optional[str] = ...) -> None: ...

class ModuleStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

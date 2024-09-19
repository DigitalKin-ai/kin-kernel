from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ModuleStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MODULE_STATUS_UNKNOWN: _ClassVar[ModuleStatus]
    MODULE_STATUS_STARTING: _ClassVar[ModuleStatus]
    MODULE_STATUS_PROCESSING: _ClassVar[ModuleStatus]
    MODULE_STATUS_CANCELED: _ClassVar[ModuleStatus]
    MODULE_STATUS_FAILED: _ClassVar[ModuleStatus]
    MODULE_STATUS_EXPIRED: _ClassVar[ModuleStatus]
    MODULE_STATUS_SUCCESS: _ClassVar[ModuleStatus]
    MODULE_STATUS_STOPPED: _ClassVar[ModuleStatus]
MODULE_STATUS_UNKNOWN: ModuleStatus
MODULE_STATUS_STARTING: ModuleStatus
MODULE_STATUS_PROCESSING: ModuleStatus
MODULE_STATUS_CANCELED: ModuleStatus
MODULE_STATUS_FAILED: ModuleStatus
MODULE_STATUS_EXPIRED: ModuleStatus
MODULE_STATUS_SUCCESS: ModuleStatus
MODULE_STATUS_STOPPED: ModuleStatus

class JobInfo(_message.Message):
    __slots__ = ("job_id", "job_status")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_STATUS_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    job_status: ModuleStatus
    def __init__(self, job_id: _Optional[str] = ..., job_status: _Optional[_Union[ModuleStatus, str]] = ...) -> None: ...

class GetModuleStatusRequest(_message.Message):
    __slots__ = ("job_id",)
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    def __init__(self, job_id: _Optional[str] = ...) -> None: ...

class GetModuleStatusResponse(_message.Message):
    __slots__ = ("success", "status", "job_id")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    success: bool
    status: ModuleStatus
    job_id: str
    def __init__(self, success: bool = ..., status: _Optional[_Union[ModuleStatus, str]] = ..., job_id: _Optional[str] = ...) -> None: ...

class GetModuleJobsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetModuleJobsResponse(_message.Message):
    __slots__ = ("success", "jobs")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    JOBS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    jobs: _containers.RepeatedCompositeFieldContainer[JobInfo]
    def __init__(self, success: bool = ..., jobs: _Optional[_Iterable[_Union[JobInfo, _Mapping]]] = ...) -> None: ...

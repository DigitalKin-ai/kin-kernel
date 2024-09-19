from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ModuleInfo(_message.Message):
    __slots__ = ("module_id", "module_status")
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    MODULE_STATUS_FIELD_NUMBER: _ClassVar[int]
    module_id: str
    module_status: bool
    def __init__(self, module_id: _Optional[str] = ..., module_status: bool = ...) -> None: ...

class GetAllModulesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAllModulesResponse(_message.Message):
    __slots__ = ("success", "modules")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MODULES_FIELD_NUMBER: _ClassVar[int]
    success: bool
    modules: _containers.RepeatedCompositeFieldContainer[ModuleInfo]
    def __init__(self, success: bool = ..., modules: _Optional[_Iterable[_Union[ModuleInfo, _Mapping]]] = ...) -> None: ...

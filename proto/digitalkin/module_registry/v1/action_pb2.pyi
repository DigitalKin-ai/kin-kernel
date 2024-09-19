from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class DiscoverRequest(_message.Message):
    __slots__ = ("module_id",)
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    module_id: str
    def __init__(self, module_id: _Optional[str] = ...) -> None: ...

class DiscoverResponse(_message.Message):
    __slots__ = ("module_type", "address", "port", "status")
    MODULE_TYPE_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    module_type: str
    address: str
    port: int
    status: bool
    def __init__(self, module_type: _Optional[str] = ..., address: _Optional[str] = ..., port: _Optional[int] = ..., status: bool = ...) -> None: ...

class UpdateStatusRequest(_message.Message):
    __slots__ = ("module_id", "status")
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    module_id: str
    status: bool
    def __init__(self, module_id: _Optional[str] = ..., status: bool = ...) -> None: ...

class UpdateStatusResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

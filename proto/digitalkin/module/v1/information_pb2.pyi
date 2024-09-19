from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetModuleInputRequest(_message.Message):
    __slots__ = ("module_id", "llm_format")
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    LLM_FORMAT_FIELD_NUMBER: _ClassVar[int]
    module_id: str
    llm_format: bool
    def __init__(self, module_id: _Optional[str] = ..., llm_format: bool = ...) -> None: ...

class GetModuleOutputRequest(_message.Message):
    __slots__ = ("module_id", "llm_format")
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    LLM_FORMAT_FIELD_NUMBER: _ClassVar[int]
    module_id: str
    llm_format: bool
    def __init__(self, module_id: _Optional[str] = ..., llm_format: bool = ...) -> None: ...

class GetModuleSetupRequest(_message.Message):
    __slots__ = ("module_id", "llm_format")
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    LLM_FORMAT_FIELD_NUMBER: _ClassVar[int]
    module_id: str
    llm_format: bool
    def __init__(self, module_id: _Optional[str] = ..., llm_format: bool = ...) -> None: ...

class GetModuleInputResponse(_message.Message):
    __slots__ = ("success", "input_schema")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    INPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    success: bool
    input_schema: _struct_pb2.Struct
    def __init__(self, success: bool = ..., input_schema: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class GetModuleOutputResponse(_message.Message):
    __slots__ = ("success", "output_schema")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    success: bool
    output_schema: _struct_pb2.Struct
    def __init__(self, success: bool = ..., output_schema: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class GetModuleSetupResponse(_message.Message):
    __slots__ = ("success", "setup_schema")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    SETUP_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    success: bool
    setup_schema: _struct_pb2.Struct
    def __init__(self, success: bool = ..., setup_schema: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

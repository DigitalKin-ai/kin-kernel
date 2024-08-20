from google.protobuf import struct_pb2 as _struct_pb2
from proto.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetModuleInputRequest(_message.Message):
    __slots__ = ["llm_format", "module_id"]
    LLM_FORMAT_FIELD_NUMBER: _ClassVar[int]
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    llm_format: bool
    module_id: str
    def __init__(self, module_id: _Optional[str] = ..., llm_format: bool = ...) -> None: ...

class GetModuleInputResponse(_message.Message):
    __slots__ = ["input_schema", "success"]
    INPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    input_schema: _struct_pb2.Struct
    success: bool
    def __init__(self, success: bool = ..., input_schema: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class GetModuleOutputRequest(_message.Message):
    __slots__ = ["llm_format", "module_id"]
    LLM_FORMAT_FIELD_NUMBER: _ClassVar[int]
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    llm_format: bool
    module_id: str
    def __init__(self, module_id: _Optional[str] = ..., llm_format: bool = ...) -> None: ...

class GetModuleOutputResponse(_message.Message):
    __slots__ = ["output_schema", "success"]
    OUTPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    output_schema: _struct_pb2.Struct
    success: bool
    def __init__(self, success: bool = ..., output_schema: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class GetModuleSetupRequest(_message.Message):
    __slots__ = ["llm_format", "module_id"]
    LLM_FORMAT_FIELD_NUMBER: _ClassVar[int]
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    llm_format: bool
    module_id: str
    def __init__(self, module_id: _Optional[str] = ..., llm_format: bool = ...) -> None: ...

class GetModuleSetupResponse(_message.Message):
    __slots__ = ["setup_schema", "success"]
    SETUP_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    setup_schema: _struct_pb2.Struct
    success: bool
    def __init__(self, success: bool = ..., setup_schema: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

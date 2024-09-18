from proto.digitalkin.setup.v1 import tool_pb2 as _tool_pb2
from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Model(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MODEL_UNKNOWN: _ClassVar[Model]
    MODEL_CLAUDE_3_5_SONNET: _ClassVar[Model]
    MODEL_CLAUDE_3_HAIKU: _ClassVar[Model]
    MODEL_CLAUDE_3_OPUS: _ClassVar[Model]
    MODEL_CLAUDE_3_SONNET: _ClassVar[Model]
    MODEL_GEMINI_1_5_FLASH: _ClassVar[Model]
    MODEL_GEMINI_1_5_PRO: _ClassVar[Model]
    MODEL_GPT_3_5_TURBO: _ClassVar[Model]
    MODEL_GPT_4: _ClassVar[Model]
    MODEL_GPT_4_TURBO: _ClassVar[Model]
    MODEL_GPT_4_O: _ClassVar[Model]
    MODEL_GPT_4_O_MINI: _ClassVar[Model]
MODEL_UNKNOWN: Model
MODEL_CLAUDE_3_5_SONNET: Model
MODEL_CLAUDE_3_HAIKU: Model
MODEL_CLAUDE_3_OPUS: Model
MODEL_CLAUDE_3_SONNET: Model
MODEL_GEMINI_1_5_FLASH: Model
MODEL_GEMINI_1_5_PRO: Model
MODEL_GPT_3_5_TURBO: Model
MODEL_GPT_4: Model
MODEL_GPT_4_TURBO: Model
MODEL_GPT_4_O: Model
MODEL_GPT_4_O_MINI: Model

class Assistant(_message.Message):
    __slots__ = ("id", "system", "model", "temperature", "tools", "max_tokens")
    ID_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    TOOLS_FIELD_NUMBER: _ClassVar[int]
    MAX_TOKENS_FIELD_NUMBER: _ClassVar[int]
    id: str
    system: str
    model: Model
    temperature: float
    tools: _containers.RepeatedCompositeFieldContainer[_tool_pb2.Tool]
    max_tokens: int
    def __init__(self, id: _Optional[str] = ..., system: _Optional[str] = ..., model: _Optional[_Union[Model, str]] = ..., temperature: _Optional[float] = ..., tools: _Optional[_Iterable[_Union[_tool_pb2.Tool, _Mapping]]] = ..., max_tokens: _Optional[int] = ...) -> None: ...

class ListAssistantsRequest(_message.Message):
    __slots__ = ("organization_id",)
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    organization_id: str
    def __init__(self, organization_id: _Optional[str] = ...) -> None: ...

class ListAssistantsResponse(_message.Message):
    __slots__ = ("assistants",)
    ASSISTANTS_FIELD_NUMBER: _ClassVar[int]
    assistants: _containers.RepeatedCompositeFieldContainer[Assistant]
    def __init__(self, assistants: _Optional[_Iterable[_Union[Assistant, _Mapping]]] = ...) -> None: ...

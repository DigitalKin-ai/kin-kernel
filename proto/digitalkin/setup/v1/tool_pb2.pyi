from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Property(_message.Message):
    __slots__ = ("type", "description", "enum_values")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ENUM_VALUES_FIELD_NUMBER: _ClassVar[int]
    type: str
    description: str
    enum_values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, type: _Optional[str] = ..., description: _Optional[str] = ..., enum_values: _Optional[_Iterable[str]] = ...) -> None: ...

class Parameters(_message.Message):
    __slots__ = ("type", "properties", "requireds")
    class PropertiesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Property
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Property, _Mapping]] = ...) -> None: ...
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    REQUIREDS_FIELD_NUMBER: _ClassVar[int]
    type: str
    properties: _containers.MessageMap[str, Property]
    requireds: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, type: _Optional[str] = ..., properties: _Optional[_Mapping[str, Property]] = ..., requireds: _Optional[_Iterable[str]] = ...) -> None: ...

class Tool(_message.Message):
    __slots__ = ("id", "name", "description", "parameters")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    parameters: Parameters
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., parameters: _Optional[_Union[Parameters, _Mapping]] = ...) -> None: ...

class ListToolsResponse(_message.Message):
    __slots__ = ("tools",)
    TOOLS_FIELD_NUMBER: _ClassVar[int]
    tools: _containers.RepeatedCompositeFieldContainer[Tool]
    def __init__(self, tools: _Optional[_Iterable[_Union[Tool, _Mapping]]] = ...) -> None: ...

class CreateToolRequest(_message.Message):
    __slots__ = ("name", "description", "parameters")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    parameters: Parameters
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., parameters: _Optional[_Union[Parameters, _Mapping]] = ...) -> None: ...

class UpdateToolRequest(_message.Message):
    __slots__ = ("id", "name", "description", "parameters")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    parameters: Parameters
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., parameters: _Optional[_Union[Parameters, _Mapping]] = ...) -> None: ...

class DeleteToolRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

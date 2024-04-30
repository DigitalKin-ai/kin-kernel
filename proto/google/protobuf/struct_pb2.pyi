from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf.internal import well_known_types as _well_known_types
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
NULL_VALUE: NullValue

class ListValue(_message.Message, _well_known_types.ListValue):
    __slots__ = ["values"]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedCompositeFieldContainer[Value]
    def __init__(self, values: _Optional[_Iterable[_Union[Value, _Mapping]]] = ...) -> None: ...

class Struct(_message.Message, _well_known_types.Struct):
    __slots__ = ["fields"]
    class FieldsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Value, _Mapping]] = ...) -> None: ...
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    fields: _containers.MessageMap[str, Value]
    def __init__(self, fields: _Optional[_Mapping[str, Value]] = ...) -> None: ...

class Value(_message.Message):
    __slots__ = ["bool_value", "list_value", "null_value", "number_value", "string_value", "struct_value"]
    BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
    LIST_VALUE_FIELD_NUMBER: _ClassVar[int]
    NULL_VALUE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_VALUE_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    STRUCT_VALUE_FIELD_NUMBER: _ClassVar[int]
    bool_value: bool
    list_value: ListValue
    null_value: NullValue
    number_value: float
    string_value: str
    struct_value: Struct
    def __init__(self, null_value: _Optional[_Union[NullValue, str]] = ..., number_value: _Optional[float] = ..., string_value: _Optional[str] = ..., bool_value: bool = ..., struct_value: _Optional[_Union[Struct, _Mapping]] = ..., list_value: _Optional[_Union[ListValue, _Mapping]] = ...) -> None: ...

class NullValue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

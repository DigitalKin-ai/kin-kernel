from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ChatMessage(_message.Message):
    __slots__ = ["message", "room", "user_name"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ROOM_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    message: str
    room: str
    user_name: str
    def __init__(self, user_name: _Optional[str] = ..., message: _Optional[str] = ..., room: _Optional[str] = ...) -> None: ...

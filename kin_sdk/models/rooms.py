"""
TODO: sphinx docstring
"""

import time
from uuid import UUID
from collections import defaultdict
from typing import Callable, DefaultDict, Union

from kin_sdk.common.merge_dicts import merge_dicts
from kin_sdk.common.types import RequestType
from kin_sdk.exception import (
    RoomLockedException,
    InvalidModuleRoleException,
    ModuleInRoomNotFoundException,
)

EXPIRATION_TIME = 10


class Room:
    """TODO: sphinx docstring"""

    def __init__(self, room_id: UUID, expiration_time: int = EXPIRATION_TIME):
        self.__id = room_id
        self.__owners = set()
        self.__members = set()
        self.__request = {}
        self.__subscribers: DefaultDict[str, Callable[[str], None]] = defaultdict(
            Callable
        )
        self.__expires_at = None
        self.__expiration_time = expiration_time
        self.__lock = False  # if true it is impossible to join this room

    # Getters
    @property
    def id(self) -> UUID:
        """
        Get the room id
        """
        return self.__id

    @property
    def owners(self) -> set:
        """
        Get the owners in the room
        """
        return self.__owners

    @property
    def members(self) -> set:
        """
        Get the members in the room
        """
        return self.__members

    @property
    def request(self) -> dict:
        """
        Get the request in the room
        """
        return self.__request

    @property
    def expires_at(self) -> Union[int, None]:
        """
        Get the expiration time of the room
        """
        return self.__expires_at

    def get_modules(self, module_role: str) -> set:
        """
        Get the modules in the room
        """
        if module_role == "owner":
            return self.owners
        elif module_role == "member":
            return self.members
        else:
            raise InvalidModuleRoleException("Invalid module role")

    def get_number_of_modules(self) -> int:
        """
        Get the number of modules in the room
        """
        return len(self.owners) + len(self.members)

    # Setters
    def add_owner(self, module_id: str) -> None:
        """
        Add an owner to the room and so reset the expiration time also raise an exception if the room is locked
        """
        if self.__lock:
            raise RoomLockedException("Room is locked")

        self.__owners.add(module_id)
        self.__subscribers[module_id] = None
        self.__expires_at = None

    def remove_owner(self, module_id: str) -> None:
        """
        Remove an owner from the room and set the expiration time if there is no more modules in the room
        """
        self.__owners.remove(module_id)
        self.unsubscribe(module_id)
        if self.get_number_of_modules() <= 0:
            # if there is no more modules in the room, set the expiration time in two minutes timestamp
            self.__expires_at = int(time.time()) + self.__expiration_time
            self.__lock = True

    def is_expired(self) -> bool:
        """
        Check if the room is expired
        """
        if self.__expires_at is not None:
            return int(time.time()) > self.__expires_at
        return False

    def add_member(self, module_id: str) -> None:
        """
        Add a member to the room and so reset the expiration time also raise an exception if the room is locked
        """
        if self.__lock:
            raise RoomLockedException("Room is locked")

        self.__members.add(module_id)
        self.__subscribers[module_id] = None
        self.__expires_at = None

    def remove_member(self, module_id: str) -> None:
        """
        Remove a member from the room and set the expiration time if there is no more modules in the room
        """
        self.__members.remove(module_id)
        self.unsubscribe(module_id)
        if self.get_number_of_modules() <= 0:
            # if there is no more modules in the room, set the expiration time in two minutes timestamp
            self.__expires_at = int(time.time()) + self.__expiration_time
            self.__lock = True

    def set_expiration(self, expires_at: int) -> None:
        """
        Set the expiration time of the room
        """
        self.__expires_at = expires_at

    def remove_expiration(self) -> None:
        """
        Remove the expiration time of the room
        """
        self.__expires_at = None

    def add_module(self, module_id: str, module_role: str) -> None:
        """
        Add a module to the room
        """
        if module_role == "owner":
            self.add_owner(module_id)
        elif module_role == "member":
            self.add_member(module_id)
        else:
            raise InvalidModuleRoleException("Invalid module role")

    def remove_module(self, module_id: str, module_role: str) -> None:
        """
        Remove a module from the room
        """
        if module_role == "owner":
            self.remove_owner(module_id)
        elif module_role == "member":
            self.remove_member(module_id)
        else:
            raise InvalidModuleRoleException("Invalid module role")

    # Methods
    def subscribe(self, module_id: str, callback: Callable[[str], None]) -> None:
        """
        Subscribe to a module
        """
        try:
            self.__subscribers[module_id] = callback
        except KeyError as exc:
            raise ModuleInRoomNotFoundException("module not found") from exc

    def unsubscribe(self, module_id: str) -> None:
        """
        Unsubscribe to a module
        """
        if module_id not in self.__subscribers:
            raise ModuleInRoomNotFoundException("Module not found")

        self.__subscribers.pop(module_id)

    def publish(self, module_id: str, request: dict, request_type: RequestType) -> None:
        """
        Publish to all subscribers
        """
        self.__request = merge_dicts(self.__request, request)
        for _id, callback in self.__subscribers.items():
            callback(module_id, self.__request, request_type)


class Rooms:
    """TODO: sphinx docstring"""

    def __init__(self):
        self.__rooms: DefaultDict[UUID, Room] = defaultdict(Room)

    @property
    def rooms(self) -> DefaultDict[UUID, Room]:
        """TODO: sphinx docstring"""
        return self.__rooms

    def create_room(self, room_id: UUID) -> None:
        """
        Create a room
        """
        # check if room does not exist
        if room_id in self.__rooms:
            raise KeyError("Room already exists")

        self.__rooms[room_id] = Room(room_id)

    def get_room(self, room_id: UUID) -> Room:
        """
        Get a room
        """
        return self.__rooms.get(room_id, None)

    def delete_room(self, room_id: UUID) -> None:
        """
        Delete a room
        """
        # check if room exists
        if room_id not in self.__rooms:
            raise KeyError("Room not found")

        self.__rooms.pop(room_id)

    def add_module_to_room(
        self, room_id: UUID, module_id: str, module_role: str
    ) -> None:
        """
        Add a module to a room
        """
        try:
            self.__rooms.get(room_id, None).add_module(module_id, module_role)
        except KeyError as exc:
            raise KeyError("Room not found") from exc

    def remove_module_from_room(
        self, room_id: UUID, module_id: str, module_role: str
    ) -> None:
        """
        Remove a module from a room
        """
        try:
            self.__rooms.get(room_id, None).remove_module(module_id, module_role)
        except KeyError as exc:
            raise KeyError("Room not found") from exc

    def subscribe_to_room(
        self, room_id: UUID, module_id: str, callback: Callable[[str], None]
    ) -> None:
        """
        Subscribe to a room
        """
        try:
            self.__rooms.get(room_id, None).subscribe(module_id, callback)
        except KeyError as exc:
            raise KeyError("Room not found") from exc

    def unsubscribe_to_room(self, room_id: UUID, module_id: str) -> None:
        """
        Unsubscribe to a room
        """
        try:
            self.__rooms.get(room_id, None).unsubscribe(module_id)
        except KeyError as exc:
            raise KeyError("Room not found") from exc

    def publish_to_room(
        self, room_id: UUID, module_id: str, request: dict, request_type: RequestType
    ) -> None:
        """
        Publish to a room
        """
        try:
            self.__rooms.get(room_id, None).publish(module_id, request, request_type)
        except KeyError as exc:
            raise KeyError("Room not found") from exc

    def get_modules_in_room(self, room_id: UUID, module_role: str) -> set:
        """
        Get the modules in a room
        """
        try:
            return self.__rooms.get(room_id, None).get_modules(module_role)
        except KeyError as exc:
            raise KeyError("Room not found") from exc

    def remove_expired_rooms(
        self,
    ) -> None:  # ! TODO : do not forget to call this method
        """
        Remove expired rooms
        """
        expired_room_ids = [
            room_id for room_id, room in self.__rooms.items() if room.is_expired()
        ]
        for room_id in expired_room_ids:
            self.__rooms.pop(room_id)

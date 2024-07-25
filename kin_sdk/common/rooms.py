"""
TODO: sphinx docstring
"""

import time
from uuid import UUID
from collections import defaultdict
from typing import Callable, DefaultDict, Union

from kin_sdk.common.merge_dicts import merge_dicts
from kin_sdk.common.types import RequestType

EXPIRATION_TIME = 10


class Room:
    def __init__(self, id: UUID, expiration_time: int = EXPIRATION_TIME):
        self.__id = id
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

    def get_services(self, service_role: str) -> set:
        """
        Get the services in the room
        """
        if service_role == "owner":
            return self.owners
        elif service_role == "member":
            return self.members
        else:
            raise Exception("Invalid service role")

    def get_number_of_services(self) -> int:
        """
        Get the number of services in the room
        """
        return len(self.owners) + len(self.members)

    # Setters
    def add_owner(self, service_id: str) -> None:
        """
        Add an owner to the room and so reset the expiration time also raise an exception if the room is locked
        """
        if self.__lock:
            raise Exception("Room is locked")

        self.__owners.add(service_id)
        self.__subscribers[service_id] = None
        self.__expires_at = None

    def remove_owner(self, service_id: str) -> None:
        """
        Remove an owner from the room and set the expiration time if there is no more services in the room
        """
        self.__owners.remove(service_id)
        self.unsubscribe(service_id)
        if self.get_number_of_services() <= 0:
            # if there is no more services in the room, set the expiration time in two minutes timestamp
            self.__expires_at = int(time.time()) + self.__expiration_time
            self.__lock = True

    def is_expired(self) -> bool:
        """
        Check if the room is expired
        """
        if self.__expires_at is not None:
            return int(time.time()) > self.__expires_at
        return False

    def add_member(self, service_id: str) -> None:
        """
        Add a member to the room and so reset the expiration time also raise an exception if the room is locked
        """
        if self.__lock:
            raise Exception("Room is locked")

        self.__members.add(service_id)
        self.__subscribers[service_id] = None
        self.__expires_at = None

    def remove_member(self, service_id: str) -> None:
        """
        Remove a member from the room and set the expiration time if there is no more services in the room
        """
        self.__members.remove(service_id)
        self.unsubscribe(service_id)
        if self.get_number_of_services() <= 0:
            # if there is no more services in the room, set the expiration time in two minutes timestamp
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

    def add_service(self, service_id: str, service_role: str) -> None:
        """
        Add a service to the room
        """
        if service_role == "owner":
            self.add_owner(service_id)
        elif service_role == "member":
            self.add_member(service_id)
        else:
            raise Exception("Invalid service role")

    def remove_service(self, service_id: str, service_role: str) -> None:
        """
        Remove a service from the room
        """
        if service_role == "owner":
            self.remove_owner(service_id)
        elif service_role == "member":
            self.remove_member(service_id)
        else:
            raise Exception("Invalid service role")

    # Methods
    def subscribe(self, service_id: str, callback: Callable[[str], None]) -> None:
        """
        Subscribe to a service
        """
        try:
            self.__subscribers[service_id] = callback
        except KeyError:
            raise Exception("Service not found")

    def unsubscribe(self, service_id: str) -> None:
        """
        Unsubscribe to a service
        """
        if service_id not in self.__subscribers:
            raise Exception("Service not found")

        self.__subscribers.pop(service_id)

    def publish(
        self, service_id: str, request: dict, request_type: RequestType
    ) -> None:
        """
        Publish to all subscribers
        """
        self.__request = merge_dicts(self.__request, request)
        for id, callback in self.__subscribers.items():
            callback(service_id, self.__request, request_type)


class Rooms:
    def __init__(self):
        self.__rooms: DefaultDict[UUID, Room] = defaultdict(Room)

    @property
    def rooms(self) -> DefaultDict[UUID, Room]:
        return self.__rooms

    def create_room(self, room_id: UUID) -> None:
        """
        Create a room
        """
        # check if room does not exist
        if room_id in self.__rooms:
            raise Exception("Room already exists")

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
            raise Exception("Room not found")

        self.__rooms.pop(room_id)

    def add_service_to_room(
        self, room_id: UUID, service_id: str, service_role: str
    ) -> None:
        """
        Add a service to a room
        """
        try:
            self.__rooms.get(room_id, None).add_service(service_id, service_role)
        except KeyError:
            raise Exception("Room not found")

    def remove_service_from_room(
        self, room_id: UUID, service_id: str, service_role: str
    ) -> None:
        """
        Remove a service from a room
        """
        try:
            self.__rooms.get(room_id, None).remove_service(service_id, service_role)
        except KeyError:
            raise Exception("Room not found")

    def subscribe_to_room(
        self, room_id: UUID, service_id: str, callback: Callable[[str], None]
    ) -> None:
        """
        Subscribe to a room
        """
        try:
            self.__rooms.get(room_id, None).subscribe(service_id, callback)
        except KeyError:
            raise Exception("Room not found")

    def unsubscribe_to_room(self, room_id: UUID, service_id: str) -> None:
        """
        Unsubscribe to a room
        """
        try:
            self.__rooms.get(room_id, None).unsubscribe(service_id)
        except KeyError:
            raise Exception("Room not found")

    def publish_to_room(
        self, room_id: UUID, service_id: str, request: dict, request_type: RequestType
    ) -> None:
        """
        Publish to a room
        """
        try:
            self.__rooms.get(room_id, None).publish(service_id, request, request_type)
        except KeyError:
            raise Exception("Room not found")

    def get_services_in_room(self, room_id: UUID, service_role: str) -> set:
        """
        Get the services in a room
        """
        try:
            return self.__rooms.get(room_id, None).get_services(service_role)
        except KeyError:
            raise Exception("Room not found")

    def remove_expired_rooms(self) -> None:  # TODO : do not forget to call this method
        """
        Remove expired rooms
        """
        expired_room_ids = [
            room_id for room_id, room in self.__rooms.items() if room.is_expired()
        ]
        for room_id in expired_room_ids:
            self.__rooms.pop(room_id)

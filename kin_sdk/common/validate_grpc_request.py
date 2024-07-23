import time
import grpc
import uuid

from threading import Thread

# from datetime import datetime
from functools import wraps
from typing import Dict, Any, Iterator, Callable, Literal, Optional
from queue import Queue

from pydantic import BaseModel, Field, model_validator
from google.protobuf import json_format, struct_pb2
from protoc_gen_validate.validator import validate, ValidationFailed
from pydantic_core import PydanticUndefinedType


from kin_sdk.common.logger import logger
from kin_sdk.common.rooms import Rooms
from kin_sdk.common.validated_request import ValidatedRequest


def merge_dicts(accumulated_dict: Dict[str, Any], new_dict: Dict[str, Any]) -> None:
    """Recursively merge new_dict into accumulated_dict."""
    for key, value in new_dict.items():
        if key in accumulated_dict:
            if isinstance(value, dict) and isinstance(accumulated_dict[key], dict):
                merge_dicts(accumulated_dict[key], value)
            elif isinstance(value, list) and isinstance(accumulated_dict[key], list):
                # Merge lists without duplicating elements
                for item in value:
                    if item not in accumulated_dict[key]:
                        accumulated_dict[key].append(item)
            else:
                accumulated_dict[key] = value
        else:
            accumulated_dict[key] = value


def validate_grpc_request(func):
    """
    A decorator to validate gRPC requests using protoc_gen_validate.

    This decorator intercepts the execution of a gRPC service method to
    perform validation on the incoming request. If the validation fails,
    it sets the appropriate gRPC status code and details. If the validation
    passes, it proceeds with the actual service method.

    Parameters:
        func (Callable): The gRPC service method to be decorated.

    Returns:
        Callable: A wrapper function that incorporates validation logic.
    """

    @wraps(func)
    def wrapper(self, request, context):
        """
        Wrapper function to execute validation and handle exceptions.

        Parameters:
            self: The instance of the gRPC service class.
            request: The request message for the gRPC method.
            context: The gRPC context.

        Returns:
            Varies: The return type depends on the gRPC method being called.

        Raises:
            grpc.RpcError: An appropriate gRPC error is raised and handled if validation fails.
        """
        try:
            # Validate the request using protoc_gen_validate
            validate(request)
            # If validation is successful, proceed to the actual function
            return func(self, request, context)
        except ValidationFailed as e:
            # Handle validation errors
            logger.error("Validation Error: %s", e)
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
        except Exception as e:
            # Handle other exceptions that may occur
            logger.error("Validate Exception Error: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

    return wrapper


def validate_stream_grpc_request():
    """
    A decorator to validate streaming gRPC requests using protoc_gen_validate.

    This decorator intercepts the execution of a gRPC service method to
    perform validation on the incoming request. If the validation fails,
    it sets the appropriate gRPC status code and details. If the validation
    passes, it proceeds with the actual service method.

    Parameters:
        func (Callable): The gRPC service method to be decorated.

    Returns:
        Callable: A wrapper function that incorporates validation logic.
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, request_iterator: Iterator, context: grpc.ServicerContext):
            """
            Todo: sphinx docstring
            """
            try:
                # Extract service name from metadata
                metadata = dict(context.invocation_metadata())
                service_name = metadata.get("name", "default_service")

                # Initialize room if not exists
                with self.lock:
                    if service_name not in self.rooms:
                        self.rooms[service_name] = {
                            "clients": 0,
                            "data": None,
                            "type": None,
                            "last_update": time.time(),
                        }

                self.rooms[service_name]["clients"] += 1
                # Process incoming requests
                for request in request_iterator:
                    with self.lock:
                        self.rooms[service_name]["type"] = type(request)
                        data_dict = (
                            json_format.MessageToDict(
                                self.rooms[service_name]["data"],
                                preserving_proto_field_name=True,
                            )
                            if self.rooms[service_name]["data"]
                            else {}
                        )
                        merge_dicts(
                            data_dict,
                            json_format.MessageToDict(
                                request,
                                preserving_proto_field_name=True,
                            ),
                        )
                        self.rooms[service_name]["data"] = json_format.ParseDict(
                            data_dict, type(request)()
                        )
                        self.rooms[service_name]["last_update"] = time.time()

                # Decrease the number of clients when the stream ends
                with self.lock:
                    self.rooms[service_name]["clients"] -= 1
                    if self.rooms[service_name]["clients"] <= 0:
                        self.condition.notify_all()

                if self.rooms[service_name]["clients"] <= 0:
                    # Execute the merged request
                    with self.lock:
                        merged_request = self.rooms[service_name]["data"]
                        del self.rooms[service_name]
                        validate(merged_request)

                    return func(self, merged_request, context)

                return func(
                    self,
                    json_format.ParseDict(
                        {"partial_request": True},
                        struct_pb2.Struct(),
                    ),
                    context,
                )

            except ValidationFailed as e:
                # Handle validation errors
                logger.error("Validation Error: %s", e)
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
            except Exception as e:
                # Handle other exceptions that may occur
                logger.error("Validate Exception Error: %s", e)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))

        return wrapper

    return decorator


class Metadata(BaseModel):
    service_id: str = Field(..., description="The unique identifier of the service")
    service_role: Literal["owner", "member"] = Field(
        default="member", description="The role of the service"
    )
    room_id: Optional[uuid.UUID] = Field(
        ..., description="The unique identifier of the room"
    )

    @model_validator(mode="before")
    def set_defaults_for_none(cls, values):
        fields = cls.model_fields
        for field_name, field_info in fields.items():
            value = values.get(field_name)
            default_value = (
                field_info.default
                if not isinstance(field_info.default, PydanticUndefinedType)
                else None
            )
            default_factory = (
                field_info.default_factory
                if not isinstance(field_info.default_factory, PydanticUndefinedType)
                else None
            )

            if value is None:
                if default_value is not None:
                    values[field_name] = default_value
                elif default_factory is not None:
                    values[field_name] = default_factory()

        return values


def get_metadata(context: grpc.ServicerContext):
    """
    Extract metadata from the gRPC context.

    Parameters:
        context (grpc.ServicerContext): The gRPC context object.

    Returns:
        Dict: A dictionary containing the metadata key-value pairs.
    """
    try:
        # Extract service name from metadata
        metadata = dict(context.invocation_metadata())
        service_id = metadata.get("service_id", None)
        service_role = metadata.get("service_role", None)
        room_id = metadata.get("room_id", None)

        if not service_id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Service ID metadata is required.")
            raise ValueError("Service ID metadata is required.")

        return Metadata(
            service_id=service_id, service_role=service_role, room_id=room_id
        )
    except grpc.RpcError as e:
        logger.error("Error getting metadata: %s", e)
        raise e


def validate_stream_request():
    """
    TODO: sphinx docstring
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, request_iterator, context: grpc.ServicerContext):
            """
            Todo: sphinx docstring
            """
            if not hasattr(self, "rooms"):
                raise AttributeError(
                    f"{self.__class__.__name__} instance must have a 'rooms' attribute."
                )

            if not isinstance(self.rooms, Rooms):
                raise TypeError(
                    f"The 'rooms' attribute must be of type Rooms, got {type(self.rooms).__name__}."
                )

            try:
                # Extract metadata
                metadata = get_metadata(context)
                message_queue = Queue()

                # Create room if not exists
                if not metadata.room_id:
                    metadata.room_id = uuid.uuid4()
                    with self.lock:
                        self.rooms.create_room(metadata.room_id)

                # Check if room exists
                if not self.rooms.get_room(metadata.room_id):
                    return func(
                        self,
                        ValidatedRequest(
                            request_iterator, False, "Room does not exist."
                        ),
                        context,
                    )

                # Add service to room
                with self.lock:
                    self.rooms.add_service_to_room(
                        room_id=metadata.room_id,
                        service_id=metadata.service_id,
                        service_role=metadata.service_role,
                    )

                def callback(request: Dict[str, Any]) -> None:
                    print("callback", request)

                def handle_incoming_messages() -> None:
                    has_subscription = False
                    try:
                        for request in request_iterator:
                            # Process incoming messages convert it to dict
                            request_dict = (
                                json_format.MessageToDict(
                                    request, preserving_proto_field_name=True
                                )
                                if request
                                else {}
                            )

                            if not has_subscription:
                                print("Subscribing to room ", metadata.room_id)
                                self.rooms.subscribe_to_room(
                                    metadata.room_id, metadata.service_id, callback
                                )
                                has_subscription = True

                            # Publish request message to room
                            with self.lock:
                                print(f"Publish message: {request_dict}")
                                self.rooms.publish_to_room(
                                    metadata.room_id, metadata.service_id, request_dict
                                )

                    except grpc.RpcError as e:
                        print(f"Client disconnected with error: {e}")
                    finally:
                        message_queue.put(None)  # Sentinel to stop the message_sender

                # Start the incoming message handler in a separate thread
                incoming_thread = Thread(target=handle_incoming_messages)
                incoming_thread.start()

                def message_sender() -> None:
                    print("message_sender")
                    while True:
                        message = message_queue.get()
                        if message is None:
                            print("User disconnected")
                            break
                        print(message)

                message_sender()
                # counter = 0
                # while counter < 10:
                #     try:
                #         counter += 1
                #         print(f"counter: {counter}")
                #         print(self.rooms.get_room(metadata.room_id))
                #         print(self.rooms.get_room(metadata.room_id).expires_at)
                #         print(
                #             self.rooms.get_room(metadata.room_id).expires_at
                #             - time.time()
                #         )

                #         expires_at_datetime = datetime.fromtimestamp(
                #             self.rooms.get_room(metadata.room_id).expires_at
                #         )
                #         formatted_time = expires_at_datetime.strftime(
                #             "%d %B %Y %H:%M:%S"
                #         )
                #         print(formatted_time)
                #         print(
                #             f"is expired: {self.rooms.get_room(metadata.room_id).is_expired()}"
                #         )
                #         self.rooms.remove_expired_rooms()
                #         time.sleep(10)
                #     except Exception as e:
                #         print(f"Error: {e}")
                #         break

                return func(
                    self,
                    json_format.ParseDict(
                        {"partial_request": True},
                        struct_pb2.Struct(),
                    ),
                    context,
                )
                assert "a" == "b", "stop"

                # // 1. request_iterator loop to add request input in the room and send it to other services
                # 2. receive message from the room with the new inputs values
                # 3. if owner is present and send instruction,then try to validate(merged_request) and then return func and disconnect all other members, and delete the room
                # 4. if all member disconnect and no services are left in the room, init a 2 minutes timer to delete the room

            #     # Initialize room if not exists
            #     with self.lock:
            #         if service_name not in self.rooms:
            #             self.rooms[service_name] = {
            #                 "clients": 0,
            #                 "data": None,
            #                 "type": None,
            #                 "last_update": time.time(),
            #             }

            #     self.rooms[service_name]["clients"] += 1
            #     # Process incoming requests
            #     for request in request_iterator:
            #         with self.lock:
            #             self.rooms[service_name]["type"] = type(request)
            #             data_dict = (
            #                 json_format.MessageToDict(
            #                     self.rooms[service_name]["data"],
            #                     preserving_proto_field_name=True,
            #                 )
            #                 if self.rooms[service_name]["data"]
            #                 else {}
            #             )
            #             merge_dicts(
            #                 data_dict,
            #                 json_format.MessageToDict(
            #                     request,
            #                     preserving_proto_field_name=True,
            #                 ),
            #             )
            #             self.rooms[service_name]["data"] = json_format.ParseDict(
            #                 data_dict, type(request)()
            #             )
            #             self.rooms[service_name]["last_update"] = time.time()

            #     # Decrease the number of clients when the stream ends
            #     with self.lock:
            #         self.rooms[service_name]["clients"] -= 1
            #         if self.rooms[service_name]["clients"] <= 0:
            #             self.condition.notify_all()

            #     if self.rooms[service_name]["clients"] <= 0:
            #         # Execute the merged request
            #         with self.lock:
            #             merged_request = self.rooms[service_name]["data"]
            #             del self.rooms[service_name]
            #             validate(merged_request)

            #         return func(self, merged_request, context)

            #     return func(
            #         self,
            #         json_format.ParseDict(
            #             {"partial_request": True},
            #             struct_pb2.Struct(),
            #         ),
            #         context,
            #     )

            except ValidationFailed as e:
                # Handle validation errors
                logger.error("Validation Error: %s", e)
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
            except Exception as e:
                # Handle other exceptions that may occur
                logger.error("Validate Exception Error: %s", e)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))

        return wrapper

    return decorator

import time
import grpc
import uuid
from threading import Thread, Lock

# from datetime import datetime
from functools import wraps
from typing import Dict, Any, Iterator, Callable, Literal, Optional
from queue import Queue

from pydantic import BaseModel, Field, model_validator
from google.protobuf import json_format, struct_pb2
from protoc_gen_validate.validator import validate, ValidationFailed
from pydantic_core import PydanticUndefinedType

import proto.digitalkin.service.v1.service_pb2 as service_pb2

from kin_sdk.common.logger import logger
from kin_sdk.common.types import RequestType
from kin_sdk.common.rooms import Rooms


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

        if (service_role is None or service_role == "member") and not room_id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(
                "Service role metadata should be `owner` if there is no `room_id` or should be `member` with a `room_id`."
            )
            raise ValueError(
                "Service role metadata should be `owner` if there is no `room_id` or should be `member` with a `room_id`."
            )

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
            # check required attributes to the attached method
            if not hasattr(self, "rooms"):
                raise AttributeError(
                    f"{self.__class__.__name__} instance must have a 'rooms' attribute."
                )
            if not isinstance(self.rooms, Rooms):
                raise TypeError(
                    f"The 'rooms' attribute must be of type Rooms, got {type(self.rooms).__name__}."
                )
            if not hasattr(self, "lock"):
                raise AttributeError(
                    f"{self.__class__.__name__} instance must have a 'lock' attribute."
                )
            if not isinstance(self.lock, type(Lock())):
                raise TypeError(
                    f"The 'lock' attribute must be of type Lock, got {type(self.lock).__name__}."
                )
            if not hasattr(self, "service"):
                raise AttributeError(
                    f"{self.__class__.__name__} instance must have a 'service' attribute."
                )
            # be cautious of circular imports
            from kin_sdk.service.base import BaseService

            if not isinstance(self.service, BaseService):
                raise TypeError(
                    f"The 'service' attribute must be of type BaseService, got {type(self.service).__name__}."
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

                # Check if room exists before adding service and raising an error if it doesn't
                if not self.rooms.get_room(metadata.room_id):
                    raise ValueError(f"Room {metadata.room_id} does not exist.")

                # Add service to room
                with self.lock:
                    self.rooms.add_service_to_room(
                        room_id=metadata.room_id,
                        service_id=metadata.service_id,
                        service_role=metadata.service_role,
                    )

                def callback(
                    service_id: str, request: Dict[str, Any], request_type: RequestType
                ) -> None:
                    """
                    Callback function to handle incoming messages from the room.
                    put the message in the message_queue to be sent to the client
                    """
                    message_queue.put((service_id, request, request_type))

                # Subscribe to the room to receive messages from other services in the room
                print("Subscribing to room ", metadata.room_id)
                self.rooms.subscribe_to_room(
                    metadata.room_id, metadata.service_id, callback
                )
                # Return a success message to the client indicating that the service is connected to the room
                yield service_pb2.ServiceResponse(
                    success=True,
                    message=f"connected to the room {metadata.room_id}",
                    service_id=self.service.service_id,
                )

                def handle_incoming_messages() -> None:
                    """
                    Handle incoming messages from the client and publish them to the room.
                    """
                    try:
                        # iterate over the incoming messages from the client stream
                        for request in request_iterator:
                            # Process incoming messages convert it to dict
                            request_dict = (
                                json_format.MessageToDict(
                                    request, preserving_proto_field_name=True
                                )
                                if request
                                else {}
                            )

                            # Publish request message to room
                            with self.lock:
                                # Extract request_type from the request_dict we do not want to let it inside the request
                                # also we want to set the default value to SEND and we want to make sure that the request_type is a RequestType
                                # if the service is the owner of the room we want to take into account the request_type else we want to ignore it and set it to SEND
                                request_type = (
                                    RequestType[
                                        request_dict.pop("request_type", "SEND")
                                    ]
                                    if metadata.service_role == "owner"
                                    else RequestType.SEND
                                )

                                # Publish the request to the room
                                self.rooms.publish_to_room(
                                    metadata.room_id,
                                    metadata.service_id,
                                    request_dict,
                                    request_type,
                                )

                    except grpc.RpcError as e:
                        # we do not want to raise an error if the client disconnects it is a normal behavior
                        print(f"Client disconnected with error: {e}")
                    finally:
                        message_queue.put(
                            (metadata.service_id, None, RequestType.EXIT)
                        )  # Sentinel to stop the message_sender

                # Start the incoming message handler in a separate thread
                incoming_thread = Thread(target=handle_incoming_messages)
                incoming_thread.start()

                # usefull to know if we want to try to validate the request
                is_validate: bool = False

                def message_sender() -> Iterator[service_pb2.ServiceResponse]:
                    print("message_sender")
                    while True:
                        sender_id, request, request_type = message_queue.get()
                        print(
                            f"Received a request from {sender_id}: request: {request_type} \n {request}"
                        )

                        # exit condition, this will terminate the stream
                        if request is None or request_type == RequestType.EXIT:
                            print(f"Service {metadata.service_id} disconnected")
                            break

                        print(
                            f"\t- metadata.service_role: {metadata.service_role}\n\t- metadata.service_id: {metadata.service_id}\n\t- sender_id: {sender_id}"
                        )

                        if (
                            metadata.service_role == "owner"
                            and metadata.service_id == sender_id
                            and request_type == RequestType.VALIDATE
                        ):
                            print("Validate request")
                            yield (None, True)
                            break

                        # yield the message to the client
                        yield (
                            service_pb2.ServiceResponse(
                                success=True,
                                message=str(request),
                                service_id=self.service.service_id,
                            ),
                            False,
                        )
                    print("end")
                    return None

                # Return the message sender generator
                for item, need_validate in message_sender():
                    is_validate = need_validate
                    print(f"is_validate s: {is_validate}")
                    if item is None:
                        break
                    yield item
                print(f"is_validate: {is_validate}")
                print(len(self.rooms.get_room(metadata.room_id).owners))
                print(metadata.service_role)

                if (
                    metadata.service_role == "owner"
                    and len(self.rooms.get_room(metadata.room_id).owners) <= 1
                ):
                    # if the stream ends and the owner is the only one left in the room
                    # eject all members
                    self.rooms.publish_to_room(
                        metadata.room_id, metadata.service_id, {}, RequestType.EXIT
                    )
                    # req = self.rooms.get_room(metadata.room_id).request.copy()
                    # request = json_format.ParseDict(
                    #     req,
                    #     service_pb2.StartServiceRequest(),
                    # )
                    # validate(request)
                    print(
                        self.rooms.get_room(metadata.room_id).get_number_of_services()
                    )

                with self.lock:
                    self.rooms.remove_service_from_room(
                        room_id=metadata.room_id,
                        service_id=metadata.service_id,
                        service_role=metadata.service_role,
                    )
                    print("close")
                print(
                    metadata.service_role,
                    self.rooms.get_room(metadata.room_id).get_number_of_services(),
                )

                if is_validate:
                    req = self.rooms.get_room(metadata.room_id).request.copy()
                    request = json_format.ParseDict(
                        req,
                        service_pb2.StartServiceRequest(),
                    )
                    validate(request)
                    print("validate")
                    print(
                        "services numbers",
                        self.rooms.get_room(metadata.room_id).get_number_of_services(),
                    )

                    for message in func(self, request, context):
                        if message is None:
                            break
                        yield message
                print("over", metadata.service_role)
                return None

                # // 1. request_iterator loop to add request input in the room and send it to other services
                # // 2. receive message from the room with the new inputs values
                # // 3. if owner is present and send instruction,then try to validate(merged_request) and then return func and disconnect all other members, and delete the room
                # // 4. if all member disconnect and no services are left in the room, init a 2 minutes timer to delete the room

            except ValidationFailed as e:
                # Handle validation errors
                logger.error("Validation Error: %s ", str(e))
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.ABORTED:
                    print("Le serveur a éjecté le client :", e.details())
                    context.set_code(grpc.StatusCode.ABORTED)
                    context.set_details("teststest", str(e))
                else:
                    print("Erreur lors de la communication avec le serveur :", e)
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details(str(e))
            except Exception as e:
                # Handle other exceptions that may occur
                print("Validate Exception Error: %s", e)
                logger.error("Validate Exception Error: %s", e)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))

        return wrapper

    return decorator

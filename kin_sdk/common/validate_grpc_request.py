"""TODO: Add a description here."""

import asyncio
import json
import time
import uuid
from threading import Lock, Thread
from functools import wraps

# from datetime import datetime
from typing import Dict, Any, Iterator, Callable, Literal, Optional
from queue import Queue

import grpc
from pydantic import BaseModel, Field, model_validator, ValidationError
from google.protobuf import json_format, struct_pb2
from protoc_gen_validate.validator import validate, ValidationFailed
from pydantic_core import PydanticUndefinedType

from proto.digitalkin.module.v1.lifecycle_pb2 import (
    StartModuleRequest,
    StartModuleResponse,
    ConnectionResponse,
    ErrorResponse,
    InputDataResponse,
)

from kin_sdk.exception import ValidateGrpcRequestException
from kin_sdk.common.pydantic_validation_error import pydantic_validation_error
from kin_sdk.common.logger import logger
from kin_sdk.common.types import RequestType
from kin_sdk.common.rooms import Rooms


# def merge_dicts(accumulated_dict: Dict[str, Any], new_dict: Dict[str, Any]) -> None:
#     """Recursively merge new_dict into accumulated_dict."""
#     for key, value in new_dict.items():
#         if key in accumulated_dict:
#             if isinstance(value, dict) and isinstance(accumulated_dict[key], dict):
#                 merge_dicts(accumulated_dict[key], value)
#             elif isinstance(value, list) and isinstance(accumulated_dict[key], list):
#                 # Merge lists without duplicating elements
#                 for item in value:
#                     if item not in accumulated_dict[key]:
#                         accumulated_dict[key].append(item)
#             else:
#                 accumulated_dict[key] = value
#         else:
#             accumulated_dict[key] = value


def validate_grpc_request(func):
    """
    A decorator to validate gRPC requests using protoc_gen_validate.

    This decorator intercepts the execution of a gRPC module method to
    perform validation on the incoming request. If the validation fails,
    it sets the appropriate gRPC status code and details. If the validation
    passes, it proceeds with the actual module method.

    Parameters:
        func (Callable): The gRPC module method to be decorated.

    Returns:
        Callable: A wrapper function that incorporates validation logic.
    """

    @wraps(func)
    async def async_wrapper(self, request, context):
        """
        Wrapper function to execute validation and handle exceptions for async methods.

        Parameters:
            self: The instance of the gRPC module class.
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
            return await func(self, request, context)
        except ValidationFailed as e:
            # Handle validation errors
            logger.error("Validation Error: %s", e)
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
        except ValidateGrpcRequestException as e:
            # Handle other exceptions that may occur
            logger.error("Validate Exception Error: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

    @wraps(func)
    def sync_wrapper(self, request, context):
        """
        Wrapper function to execute validation and handle exceptions for sync methods.

        Parameters:
            self: The instance of the gRPC module class.
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
        except ValidateGrpcRequestException as e:
            # Handle other exceptions that may occur
            logger.error("Validate Exception Error: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

    # Check if the function is a coroutine function
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


# def validate_stream_grpc_request():
#     """
#     A decorator to validate streaming gRPC requests using protoc_gen_validate.

#     This decorator intercepts the execution of a gRPC module method to
#     perform validation on the incoming request. If the validation fails,
#     it sets the appropriate gRPC status code and details. If the validation
#     passes, it proceeds with the actual module method.

#     Parameters:
#         func (Callable): The gRPC module method to be decorated.

#     Returns:
#         Callable: A wrapper function that incorporates validation logic.
#     """

#     def decorator(func: Callable):
#         @wraps(func)
#         def wrapper(self, request_iterator: Iterator, context: grpc.ServicerContext):
#             """
#             Todo: sphinx docstring
#             """
#             try:
#                 # Extract module name from metadata
#                 metadata = dict(context.invocation_metadata())
#                 module_name = metadata.get("name", "default_module")

#                 # Initialize room if not exists
#                 with self.lock:
#                     if module_name not in self.rooms:
#                         self.rooms[module_name] = {
#                             "clients": 0,
#                             "data": None,
#                             "type": None,
#                             "last_update": time.time(),
#                         }

#                 self.rooms[module_name]["clients"] += 1
#                 # Process incoming requests
#                 for request in request_iterator:
#                     with self.lock:
#                         self.rooms[module_name]["type"] = type(request)
#                         data_dict = (
#                             json_format.MessageToDict(
#                                 self.rooms[module_name]["data"],
#                                 preserving_proto_field_name=True,
#                             )
#                             if self.rooms[module_name]["data"]
#                             else {}
#                         )
#                         merge_dicts(
#                             data_dict,
#                             json_format.MessageToDict(
#                                 request,
#                                 preserving_proto_field_name=True,
#                             ),
#                         )
#                         self.rooms[module_name]["data"] = json_format.ParseDict(
#                             data_dict, type(request)()
#                         )
#                         self.rooms[module_name]["last_update"] = time.time()

#                 # Decrease the number of clients when the stream ends
#                 with self.lock:
#                     self.rooms[module_name]["clients"] -= 1
#                     if self.rooms[module_name]["clients"] <= 0:
#                         self.condition.notify_all()

#                 if self.rooms[module_name]["clients"] <= 0:
#                     # Execute the merged request
#                     with self.lock:
#                         merged_request = self.rooms[module_name]["data"]
#                         del self.rooms[module_name]
#                         validate(merged_request)

#                     return func(self, merged_request, context)

#                 return func(
#                     self,
#                     json_format.ParseDict(
#                         {"partial_request": True},
#                         struct_pb2.Struct(),  # pylint: disable=no-member
#                     ),
#                     context,
#                 )

#             except ValidationFailed as e:
#                 # Handle validation errors
#                 logger.error("Validation Error: %s", e)
#                 context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
#                 context.set_details(str(e))
#             except ValidateGrpcRequestException as e:
#                 # Handle other exceptions that may occur
#                 logger.error("Validate Exception Error: %s", e)
#                 context.set_code(grpc.StatusCode.INTERNAL)
#                 context.set_details(str(e))

#         return wrapper

#     return decorator


MAX_WORKERS = 10  # Adjust this value based on your system's capabilities


class Metadata(BaseModel):
    """
    Metadata model for gRPC module.

    :param module_id: The unique identifier of the module
    :param module_role: The role of the module (owner or member)
    :param room_id: The unique identifier of the room
    """

    module_id: str = Field(..., description="The unique identifier of the module")
    module_role: Literal["owner", "member"] = Field(
        default="member", description="The role of the module"
    )
    room_id: Optional[uuid.UUID] = Field(
        None, description="The unique identifier of the room"
    )

    @model_validator(mode="before")
    def set_defaults_for_none(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Set default values for None fields."""
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


def get_metadata(context: grpc.ServicerContext) -> Metadata:
    """
    Extract metadata from the gRPC context.

    :param context: The gRPC context object
    :return: A Metadata object containing the extracted metadata
    :raises ValueError: If required metadata is missing or invalid
    """
    try:
        metadata = dict(context.invocation_metadata())
        module_id = metadata.get("module_id", None)
        module_role = metadata.get("module_role", None)
        room_id = metadata.get("room_id", None)

        if not module_id:
            raise ValueError("Module ID metadata is required.")

        if (module_role is None or module_role == "member") and not room_id:
            raise ValueError(
                "Module role metadata should be `owner` if there is no `room_id` or should be `member` with a `room_id`."
            )

        return Metadata(
            module_id=module_id,
            module_role=module_role,
            room_id=uuid.UUID(room_id) if room_id else None,
        )

    except grpc.RpcError as e:
        logger.error("Error getting metadata: %s", e)
        raise e
    except ValueError as e:
        context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
        context.set_details(str(e))
        raise e


def pydantic_validation(request: Dict[str, Any], model: BaseModel) -> None:
    """TODO: sphinx docstring"""
    input_data = request.get("input", None)

    if input_data is None:
        raise ValueError("Input data is missing.")

    # Parse and validate the input JSON using the input_format Pydantic model
    model.model_validate(input_data)


def validate_stream_request():
    """
    Decorator to handle the communication between the client and the server.

    This decorator manages incoming messages from the streaming client, sends them to the room,
    and handles incoming messages from the room to send them to the client. The main goal is to
    merge requests from all clients inside the room, automatically merging each received message
    with previous messages. The final request will be the result of all messages received from the clients.
    Only owners can ask to validate the final request.
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, request_iterator, context: grpc.ServicerContext):
            """
            Wrapper function for the decorated method.

            :param self: The instance of the class containing the decorated method
            :param request_iterator: Iterator for incoming client requests
            :param context: gRPC module context
            :yield: StartModuleResponse messages
            :raises AttributeError: If required attributes are missing
            :raises TypeError: If attributes are of incorrect type
            """
            # Check required attributes
            if not all(hasattr(self, attr) for attr in ["rooms", "lock", "module"]):
                raise AttributeError(
                    f"{self.__class__.__name__} instance must have 'rooms', 'lock', and 'module' attributes."
                )

            if not isinstance(self.rooms, Rooms):
                raise TypeError(
                    f"The 'rooms' attribute must be of type Rooms, got {type(self.rooms).__name__}."
                )

            if not isinstance(self.lock, type(Lock())):
                raise TypeError(
                    f"The 'lock' attribute must be of type Lock, got {type(self.lock).__name__}."
                )

            # be cautious of circular imports
            from kin_sdk.agent_module._module.base import BaseModule

            if not isinstance(self.module, BaseModule):
                raise TypeError(
                    f"The 'module' attribute must be of type BaseModule, got {type(self.module).__name__}."
                )

            try:
                metadata = get_metadata(context)
                message_queue: Queue = Queue()

                # Create room if not exists
                if not metadata.room_id:
                    metadata.room_id = uuid.uuid4()
                    with self.lock:
                        self.rooms.create_room(metadata.room_id)

                # Check if room exists before adding module and raising an error if it doesn't
                if not self.rooms.get_room(metadata.room_id):
                    raise ValueError(f"Room {metadata.room_id} does not exist.")

                # Add module to room
                with self.lock:
                    self.rooms.add_module_to_room(
                        room_id=metadata.room_id,
                        module_id=metadata.module_id,
                        module_role=metadata.module_role,
                    )

                def callback(
                    module_id: str, request: Dict[str, Any], request_type: RequestType
                ) -> None:
                    """Callback function to handle incoming messages from the room."""
                    message_queue.put((module_id, request, request_type))

                # Subscribe to the room to receive messages from other modules in the room
                logger.debug("Subscribing to room %s", metadata.room_id)
                self.rooms.subscribe_to_room(
                    metadata.room_id, metadata.module_id, callback
                )

                # Send success message to client
                yield StartModuleResponse(
                    success=True,
                    response_type="START_RESPONSE_TYPE_CONNECTION",
                    connection=ConnectionResponse(
                        message=f"Connected to room {metadata.room_id}",
                        room_id=str(metadata.room_id),
                    ),
                    module_id=self.module.module_id,
                )

                def handle_incoming_messages() -> None:
                    """Handle incoming messages from the client and publish them to the room."""
                    try:
                        for request in request_iterator:
                            request_dict = (
                                json_format.MessageToDict(
                                    request, preserving_proto_field_name=True
                                )
                                if request
                                else {}
                            )

                            with self.lock:
                                request_type = (
                                    RequestType[
                                        request_dict.pop(
                                            "request_type", "REQUEST_TYPE_SEND"
                                        )
                                    ]
                                    if metadata.module_role == "owner"
                                    else RequestType.REQUEST_TYPE_SEND
                                )

                                self.rooms.publish_to_room(
                                    metadata.room_id,
                                    metadata.module_id,
                                    request_dict,
                                    request_type,
                                )

                            if (
                                request_type == RequestType.REQUEST_TYPE_VALIDATE
                                and metadata.module_role == "owner"
                            ):
                                break
                    except grpc.RpcError as e:
                        logger.info("Client disconnected: %s", e)
                    except ValidateGrpcRequestException as e:
                        logger.error("Error handling incoming messages: %s", e)
                    finally:
                        message_queue.put(
                            (metadata.module_id, None, RequestType.REQUEST_TYPE_EXIT)
                        )

                # Start the incoming message handler in a separate thread
                # this is useful to do not block the main thread that is waiting for the room incoming messages
                incoming_thread = Thread(target=handle_incoming_messages)
                incoming_thread.start()

                # usefull to know if we want to try to validate the request
                is_validate: bool = False

                def message_sender() -> Iterator[StartModuleResponse]:
                    """
                    Handle message that coming from the room and send it to the client
                    """
                    while True:
                        sender_id, request, request_type = message_queue.get()
                        logger.debug(
                            "Received request from %s: %s \n %s",
                            sender_id,
                            request_type,
                            request,
                        )

                        if (
                            request is None
                            or request_type == RequestType.REQUEST_TYPE_EXIT
                        ):
                            logger.info("Module %s disconnected", metadata.module_id)
                            break

                        # if the module is the owner of the room and the request is a validate request
                        # we want to try to validate the request and if it is valid we want to return the func and disconnect all other members
                        if (
                            metadata.module_role == "owner"
                            and metadata.module_id == sender_id
                            and request_type == RequestType.REQUEST_TYPE_VALIDATE
                        ):
                            logger.debug(
                                "Module: %s want to validate the request",
                                metadata.module_id,
                            )
                            yield (None, True)
                            break

                        input_data = json_format.Parse(
                            text=json.dumps(request.get("input", {})),
                            message=struct_pb2.Struct(),  # pylint: disable=no-member
                            ignore_unknown_fields=True,
                        )
                        # yield the message to the client
                        yield (
                            StartModuleResponse(
                                success=True,
                                response_type="START_RESPONSE_TYPE_INPUT",
                                input_response=InputDataResponse(
                                    message="New input data has been added in the room",
                                    input=input_data,
                                ),
                                module_id=self.module.module_id,
                            ),
                            False,
                        )
                    logger.debug(
                        "Message sender finished for module %s", metadata.module_id
                    )

                # Return the message sender generator to the client
                for item, need_validate in message_sender():
                    # update the is_validate variable
                    is_validate = need_validate
                    # if the item is None we want to break the loop
                    if item is None:
                        break
                    # yield the item to the client
                    yield item
                # if the module is the owner of the room and it is the last one in the room
                # we will eject all the members and delete the room
                if (
                    metadata.module_role == "owner"
                    and len(self.rooms.get_room(metadata.room_id).owners) <= 1
                ):
                    # if the stream ends and the owner is the only one left in the room
                    # eject all members
                    self.rooms.publish_to_room(
                        metadata.room_id,
                        metadata.module_id,
                        {},
                        RequestType.REQUEST_TYPE_EXIT,
                    )

                # Leave the room
                with self.lock:
                    self.rooms.remove_module_from_room(
                        room_id=metadata.room_id,
                        module_id=metadata.module_id,
                        module_role=metadata.module_role,
                    )

                # if the module is the owner of the room and the request is a validate request
                # we want to try to validate the request and if it is valid we want to return the func
                if metadata.module_role == "owner" and is_validate:
                    # get a copy of the final request from the room
                    req = self.rooms.get_room(metadata.room_id).request.copy()
                    # parse the request to the correct type
                    request = json_format.ParseDict(
                        req,
                        StartModuleRequest(),
                    )
                    # Try to validate the request it will raise an error if the request is not valid
                    validate(request)
                    pydantic_validation(req, self.module.input_format)
                    # call func and yield the result to the client
                    for message in func(self, request, context):
                        if message is None:
                            break
                        yield message

                # Après incoming_future.result(), on arrête le module et ferme la connexion gRPC
                logger.info("Stopping module for %s", metadata.module_id)
                context.set_code(grpc.StatusCode.OK)
                context.set_details("Module completed successfully")
                return  # This will stop the generator and close the gRPC connection
            except ValidationError as e:
                error_message = pydantic_validation_error(e, context)
                logger.error(error_message)  # Validation Error
                # Reconvert in gRPC Struct proto format the output data
            except ValidationFailed as e:
                # Handle validation errors
                logger.error("Validation Error: %s ", str(e))
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                yield StartModuleResponse(
                    success=False,
                    response_type="START_RESPONSE_TYPE_ERROR",
                    error=ErrorResponse(
                        message="An error occurred while starting the module",
                        details=str(e),
                    ),
                )
                return
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.ABORTED:
                    logger.info("Server ejected the client: %s", e.details())
                    context.set_code(grpc.StatusCode.ABORTED)
                    context.set_details(str(e))
                else:
                    logger.error("Error during server communication: %s", e)
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details(str(e))
                yield StartModuleResponse(
                    success=False,
                    response_type="START_RESPONSE_TYPE_ERROR",
                    error=ErrorResponse(
                        message="An error occurred while starting the module",
                        details=str(e),
                    ),
                )
            except ValidateGrpcRequestException as e:
                logger.exception("Unexpected error: %s", e)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))
                yield StartModuleResponse(
                    success=False,
                    response_type="START_RESPONSE_TYPE_ERROR",
                    error=ErrorResponse(
                        message="An error occurred while starting the module",
                        details=str(e),
                    ),
                )
            finally:
                # Ensure that the module is always stopped and the connection is closed
                logger.info("Finalizing module for %s", metadata.module_id)
                # You might want to add any cleanup code here

            # Stop the generator and close the gRPC connection if it hasn't been closed already
            return

        return wrapper

    return decorator

"""TODO: Add a description here"""

from __future__ import annotations
import asyncio
import json
import uuid
from functools import wraps
from threading import Lock

# from datetime import datetime
from typing import (
    AsyncIterator,
    Dict,
    Any,
    Callable,
    Union,
    TYPE_CHECKING,
)

import grpc
from pydantic import ValidationError
from google.protobuf import json_format, struct_pb2
from protoc_gen_validate.validator import validate, ValidationFailed

from proto.digitalkin.module.v1.lifecycle_pb2 import (
    StartModuleRequest,
    StartModuleResponse,
    ConnectionResponse,
    ErrorResponse,
    InputDataResponse,
)
from kin_sdk.models.metadata import Metadata
from kin_sdk.validation.grpc_helpers import (
    check_required_attributes,
    get_metadata,
    pydantic_validation,
)
from kin_sdk.validation.pydantic_validation_error import pydantic_validation_error
from kin_sdk.common.logger import logger
from kin_sdk.common.types import RequestType

if TYPE_CHECKING:
    from kin_sdk.models.rooms import Rooms


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
        except Exception as e:  # pylint: disable=broad-except
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
        except Exception as e:  # pylint: disable=broad-except
            # Handle other exceptions that may occur
            logger.error("Validate Exception Error: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

    # Check if the function is a coroutine function
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


async def handle_incoming_messages(
    rooms: Rooms,
    lock: Lock,
    metadata: Metadata,
    request_iterator: AsyncIterator[StartModuleRequest],
    message_queue: asyncio.Queue,
) -> None:
    """Handle incoming messages from the client and publish them to the room."""
    try:
        async for request in request_iterator:
            request_dict = (
                json_format.MessageToDict(request, preserving_proto_field_name=True)
                if request
                else {}
            )

            with lock:
                request_type = (
                    RequestType[request_dict.pop("request_type", "REQUEST_TYPE_SEND")]
                    if metadata.module_role == "owner"
                    else RequestType.REQUEST_TYPE_SEND
                )

                await rooms.publish_to_room(
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
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Error handling incoming messages: %s", e)
    finally:
        await message_queue.put(
            (metadata.module_id, None, RequestType.REQUEST_TYPE_EXIT)
        )


def validate_stream_request(func: Callable):
    """
    Decorator to handle the communication between the client and the server.

    This decorator manages incoming messages from the streaming client, sends them to the room,
    and handles incoming messages from the room to send them to the client. The main goal is to
    merge requests from all clients inside the room, automatically merging each received message
    with previous messages. The final request will be the result of all messages received from the clients.
    Only owners can ask to validate the final request.
    """

    @wraps(func)
    async def async_wrapper(
        self,
        request_iterator: AsyncIterator[StartModuleRequest],
        context: Union[grpc.aio.ServicerContext, grpc.ServicerContext],
    ):
        """
        Internal wrapper function to handle both synchronous and asynchronous functions.

        :param self: The instance of the class containing the decorated method
        :param request_iterator: Iterator for incoming client requests
        :param context: gRPC module context
        :yield: StartModuleResponse messages
        :raises AttributeError: If required attributes are missing
        :raises TypeError: If attributes are of incorrect type
        """

        try:
            # Check required attributes
            check_required_attributes(self)
            # Extract metadata from the gRPC context
            metadata = get_metadata(context)
            message_queue: asyncio.Queue = asyncio.Queue()

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

            async def callback(
                module_id: str, request: Dict[str, Any], request_type: RequestType
            ) -> None:
                """Callback function to handle incoming messages from the room."""
                await message_queue.put((module_id, request, request_type))

            # Subscribe to the room to receive messages from other modules in the room
            logger.debug("Subscribing to room %s", metadata.room_id)
            self.rooms.subscribe_to_room(metadata.room_id, metadata.module_id, callback)

            # Send success message to client
            yield StartModuleResponse(
                success=True,
                response_type="START_RESPONSE_TYPE_CONNECTION",
                connection=ConnectionResponse(
                    message=f"Connected to room {metadata.room_id}",
                    room_id=str(metadata.room_id),
                ),
                module_id=self.agent_management.identity.id,
            )

            # Create a task for handle_incoming_messages to run it in the background
            message_handler_task = asyncio.create_task(
                handle_incoming_messages(
                    self.rooms, self.lock, metadata, request_iterator, message_queue
                )
            )

            # usefull to know if we want to try to validate the request
            is_validate: bool = False

            async def message_sender() -> AsyncIterator[StartModuleResponse]:
                """
                Handle message that coming from the room and send it to the client
                """
                while True:
                    sender_id, request, request_type = await message_queue.get()
                    logger.debug(
                        "Received request from %s: %s \n %s",
                        sender_id,
                        request_type,
                        request,
                    )

                    if request is None or request_type == RequestType.REQUEST_TYPE_EXIT:
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
                            module_id=self.agent_management.identity.id,
                        ),
                        False,
                    )
                logger.debug(
                    "Message sender finished for module %s", metadata.module_id
                )

            # Return the message sender generator to the client
            async for item, need_validate in message_sender():
                # update the is_validate variable
                is_validate = need_validate
                # if the item is None we want to break the loop
                if item is None:
                    break
                # yield the item to the client
                yield item
            # Wait for the message handler task to complete
            await message_handler_task
            # if the module is the owner of the room and it is the last one in the room
            # we will eject all the members and delete the room
            if (
                metadata.module_role == "owner"
                and len(self.rooms.get_room(metadata.room_id).owners) <= 1
            ):
                # if the stream ends and the owner is the only one left in the room
                # eject all members
                await self.rooms.publish_to_room(
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
                pydantic_validation(req, self.module_class.input_format)
                # call func and yield the result to the client

                async for message in func(self, request, context):
                    if message is None:
                        break
                    yield message

                # for message in func(self, request, context):
                #     if message is None:
                #         break
                #     yield message

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
        except grpc.aio.AioRpcError as e:
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
        except Exception as e:  # pylint: disable=broad-except
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

    return async_wrapper

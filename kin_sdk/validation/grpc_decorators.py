"""TODO: Add a description here"""

import asyncio
import json
import uuid
from functools import wraps

# from datetime import datetime
from typing import (
    AsyncIterator,
    Dict,
    Any,
    Callable,
)

import grpc
from pydantic import ValidationError
from google.protobuf import json_format, struct_pb2
from protovalidate import validate, ValidationError as ValidationFailed

from digitalkin.module.v1.lifecycle_pb2 import (
    RequestType as RequestTypePB,
    StartModuleRequest,
    StartModuleResponse,
    ConnectionResponse,
    InputDataResponse,
    StartResponseType,
)
from kin_sdk.models.metadata import Metadata
from kin_sdk.validation.grpc_helpers import (
    check_required_attributes,
    format_violations,
    get_metadata,
    handle_start_error,
    pydantic_validation,
)
from kin_sdk.validation.pydantic_validation_error import pydantic_validation_error
from kin_sdk.common.logger import logger
from kin_sdk.common.types import ModuleRole, RequestType


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
            context.set_details(f"{str(e)}\n{format_violations(e.violations)}")
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
            context.set_details(f"{str(e)}\n{format_violations(e.violations)}")
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
    self,
    metadata: Metadata,
    request_iterator: AsyncIterator[StartModuleRequest],
    message_queue: asyncio.Queue,
) -> None:
    """
    Handle incoming messages from the client and publish them to the room.

    :param self: The instance of the class containing the rooms and lock
    :param metadata: Metadata object containing information about the module and room
    :param request_iterator: AsyncIterator for incoming client requests
    :param message_queue: Queue to store incoming messages
    """
    try:
        async for request in request_iterator:
            request_dict = (
                json_format.MessageToDict(request, preserving_proto_field_name=True)
                if request
                else {}
            )

            async with self.lock:
                request_type = (
                    RequestType[request_dict.pop("request_type", "REQUEST_TYPE_SEND")]
                    if metadata.module_role == ModuleRole.MODULE_ROLE_OWNER
                    else RequestType.REQUEST_TYPE_SEND
                )

                await self.rooms.publish_to_room(
                    metadata.room_id,
                    metadata.module_id,
                    {
                        **request_dict,
                        "request_type": RequestTypePB.Value(request_type.value),
                    },
                    request_type,
                )

            if (
                request_type == RequestType.REQUEST_TYPE_VALIDATE
                and metadata.module_role == ModuleRole.MODULE_ROLE_OWNER
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


async def setup_room(
    self,
    request_iterator: AsyncIterator[StartModuleRequest],
    context: grpc.aio.ServicerContext,
) -> Metadata:
    """
    Set up the room for the module.

    :param self: The instance of the class containing the decorated method
    :param request_iterator: Iterator for incoming client requests
    :param context: gRPC module context
    :return: Metadata object
    """
    request = await anext(request_iterator)
    metadata = get_metadata(request, context)

    # Create room if not exists
    if not metadata.room_id:
        metadata.room_id = uuid.uuid4()
        async with self.lock:
            self.rooms.create_room(metadata.room_id)
    # Check if room exists before adding module and raising an error if it doesn't
    if not self.rooms.get_room(metadata.room_id):
        raise ValueError(f"Room {metadata.room_id} does not exist.")

    # Add module to room
    async with self.lock:
        self.rooms.add_module_to_room(
            room_id=metadata.room_id,
            module_id=metadata.module_id,
            module_role=metadata.module_role,
        )

    return metadata


async def subscribe_to_room(
    self, metadata: Metadata, message_queue: asyncio.Queue
) -> None:
    """
    Subscribe to the room to receive messages from other modules.

    :param self: The instance of the class containing the decorated method
    :param metadata: Metadata object
    :param message_queue: Queue to store incoming messages
    """

    async def callback(
        module_id: str, request: Dict[str, Any], request_type: RequestType
    ) -> None:
        """
        Callback function to handle incoming messages from the room.

        :param module_id: The ID of the module sending the message
        :param request: The message content
        :param request_type: The type of message
        """
        await message_queue.put((module_id, request, request_type))

    logger.debug("Subscribing to room %s", metadata.room_id)
    self.rooms.subscribe_to_room(metadata.room_id, metadata.module_id, callback)


async def send_connection_response(self, metadata: Metadata) -> StartModuleResponse:
    """
    Send a connection response to the client.

    :param self: The instance of the class containing the decorated method
    :param metadata: Metadata object
    :return: StartModuleResponse object
    """
    return StartModuleResponse(
        success=True,
        response_type=StartResponseType.START_RESPONSE_TYPE_CONNECTION,
        connection=ConnectionResponse(
            message=f"Connected to room {metadata.room_id}",
            room_id=str(metadata.room_id),
        ),
        module_id=self.agent_management.identity.id,
    )


async def process_messages(
    self, metadata: Metadata, message_queue: asyncio.Queue
) -> AsyncIterator[StartModuleResponse]:
    """
    Process messages from the room and send them to the client.

    :param self: The instance of the class containing the decorated method
    :param metadata: Metadata object
    :param message_queue: Queue to store incoming messages
    :yield: StartModuleResponse objects
    """
    while True:
        sender_id, request, request_type = await message_queue.get()
        logger.debug(
            "Received request from %s: %s \n %s",
            sender_id,
            request_type,
            request,
        )
        # Note that only owner can publish other type than send in a room
        if request is None or request_type == RequestType.REQUEST_TYPE_EXIT:
            logger.info("Module %s disconnected", metadata.module_id)
            break

        # if the module is the owner of the room and the request is a validate request
        # we want to try to validate the request and if it is valid we want to return the func and disconnect all other members
        if (
            metadata.module_role == ModuleRole.MODULE_ROLE_OWNER
            and metadata.module_id == sender_id
            and request_type == RequestType.REQUEST_TYPE_VALIDATE
        ):
            logger.debug(
                "Module: %s want to validate the request",
                metadata.module_id,
            )
            yield None
            break

        input_data = json_format.Parse(
            text=json.dumps(request.get("input_request", {}).get("input", {})),
            message=struct_pb2.Struct(),  # pylint: disable=no-member
            ignore_unknown_fields=True,
        )
        # yield the message to the client
        yield StartModuleResponse(
            success=True,
            response_type="START_RESPONSE_TYPE_INPUT",
            input_response=InputDataResponse(
                message="New input data has been added in the room",
                input=input_data,
            ),
            module_id=self.agent_management.identity.id,
        )
    logger.debug("Message sender finished for module %s", metadata.module_id)


async def should_validate_request(self, metadata: Metadata) -> bool:
    """
    Check if the request should be validated.

    :param self: The instance of the class containing the decorated method
    :param metadata: Metadata object
    :return: Boolean indicating if the request should be validated
    """
    if (
        metadata.module_role == ModuleRole.MODULE_ROLE_OWNER
        and len(self.rooms.get_room(metadata.room_id).owners) <= 1
    ):
        # lock the room
        self.rooms.get_room(metadata.room_id).lock_the_room()
        return True
    return False


async def validate_and_process_request(
    self, metadata: Metadata, func: Callable, context: grpc.aio.ServicerContext
) -> AsyncIterator[StartModuleResponse]:
    """
    Validate the request and process it if valid.

    :param self: The instance of the class containing the decorated method
    :param metadata: Metadata object
    :param func: The original function to be called if the request is valid
    :param context: gRPC module context
    :yield: StartModuleResponse objects
    """
    # if the module is the owner of the room and the request is a validate request
    # we want to try to validate the request and if it is valid we want to return the func
    if metadata.module_role == ModuleRole.MODULE_ROLE_OWNER:
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


async def cleanup(self, metadata: Metadata) -> None:
    """
    Perform cleanup operations.

    :param self: The instance of the class containing the decorated method
    :param metadata: Metadata object
    """
    if metadata.module_role == ModuleRole.MODULE_ROLE_OWNER:
        await self.rooms.publish_to_room(
            metadata.room_id,
            metadata.module_id,
            {},
            RequestType.REQUEST_TYPE_EXIT,
        )

    async with self.lock:
        self.rooms.remove_module_from_room(
            room_id=metadata.room_id,
            module_id=metadata.module_id,
            module_role=metadata.module_role,
        )


async def handle_validation_error(
    e: ValidationError, context: grpc.aio.ServicerContext
) -> StartModuleResponse:
    """
    Handle Pydantic validation errors.

    :param e: ValidationError object
    :param context: gRPC module context
    :return: StartModuleResponse object
    """
    error_message = pydantic_validation_error(e, context)
    logger.error(error_message)
    return StartModuleResponse(
        success=False,
        response_type=StartResponseType.START_RESPONSE_TYPE_ERROR,
        error={"message": error_message},
    )


async def handle_validation_failed(
    e: ValidationFailed, context: grpc.aio.ServicerContext
) -> StartModuleResponse:
    """
    Handle validation failed errors.

    :param e: ValidationFailed object
    :param context: gRPC module context
    :return: StartModuleResponse object
    """
    logger.error("Validation Error: %s ", str(e))
    return handle_start_error(
        context,
        grpc.StatusCode.INVALID_ARGUMENT,
        "A validation error occurred while starting the module",
        f"{str(e)}\n{format_violations(e.violations)}",
    )


async def handle_grpc_error(
    e: grpc.aio.AioRpcError, context: grpc.aio.ServicerContext
) -> StartModuleResponse:
    """
    Handle gRPC errors.

    :param e: AioRpcError object
    :param context: gRPC module context
    :return: StartModuleResponse object
    """
    if e.code() == grpc.StatusCode.ABORTED:
        logger.info("Server ejected the client: %s", e.details())
        return handle_start_error(
            context,
            grpc.StatusCode.ABORTED,
            "An error occurred while starting the module",
            str(e),
        )
    else:
        logger.error("Error during server communication: %s", e)
        return handle_start_error(
            context,
            grpc.StatusCode.INTERNAL,
            "An error occurred while starting the module",
            str(e),
        )


async def handle_unexpected_error(
    e: Exception, context: grpc.aio.ServicerContext
) -> StartModuleResponse:
    """
    Handle unexpected errors.

    :param e: Exception object
    :param context: gRPC module context
    :return: StartModuleResponse object
    """
    logger.exception("Unexpected error: %s", e)
    return handle_start_error(
        context,
        grpc.StatusCode.INTERNAL,
        "An error occurred while starting the module",
        str(e),
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
        context: grpc.aio.ServicerContext,
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
            metadata = await setup_room(self, request_iterator, context)
            # Create a queue to handle incoming messages from the room
            message_queue: asyncio.Queue = asyncio.Queue()

            await subscribe_to_room(self, metadata, message_queue)
            yield await send_connection_response(self, metadata)

            # Create a task for handle_incoming_messages to run it in the background
            message_handler_task = asyncio.create_task(
                handle_incoming_messages(
                    self, metadata, request_iterator, message_queue
                )
            )

            # Return the message sender generator to the client
            async for response in process_messages(self, metadata, message_queue):
                if response is None:
                    break
                yield response

            # Wait for the message handler task to complete
            await message_handler_task

            if await should_validate_request(self, metadata):
                async for response in validate_and_process_request(
                    self, metadata, func, context
                ):
                    yield response

            logger.info("Stopping module for %s", metadata.module_id)
            context.set_code(grpc.StatusCode.OK)
            context.set_details("Module completed successfully")
            # return  # This will stop the generator and close the gRPC connection
        except ValidationError as e:
            yield await handle_validation_error(e, context)
        except ValidationFailed as e:
            yield await handle_validation_failed(e, context)
        except grpc.aio.AioRpcError as e:
            yield await handle_grpc_error(e, context)
        except Exception as e:  # pylint: disable=broad-except
            yield await handle_unexpected_error(e, context)
        finally:
            # check if metadata is declared and not None
            if "metadata" in locals() and metadata is not None:
                await cleanup(self, metadata)
        # Stop the generator and close the gRPC connection if it hasn't been closed already
        return

    return async_wrapper

"""
TODO: sphinx docstring
"""

import uuid
from typing import Dict, Any
from threading import Lock

import grpc
from pydantic import BaseModel

from proto.digitalkin.module.v1.lifecycle_pb2 import (
    StartModuleResponse,
    ErrorResponse,
)
from kin_sdk.common.logger import logger
from kin_sdk.models.metadata import Metadata


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
    """
    TODO: sphinx docstring
    """
    input_data = request.get("input", None)

    if input_data is None:
        raise ValueError("Input data is missing.")

    model.model_validate(input_data)


def check_required_attributes(instance: Any) -> None:
    """
    Check that the instance has the required attributes and that they are of the correct type.

    :param instance: The instance to check.
    :raises AttributeError: If a required attribute is missing.
    :raises TypeError: If an attribute is of the wrong type.
    """
    required_attrs = ["rooms", "lock", "module_class", "agent_management"]

    # Check for the presence of required attributes
    for attr in required_attrs:
        if not hasattr(instance, attr):
            raise AttributeError(
                f"{instance.__class__.__name__} instance must have '{attr}' attribute."
            )

    from kin_sdk.models.rooms import Rooms

    # Type checking
    if not isinstance(instance.rooms, Rooms):
        raise TypeError(
            f"The 'rooms' attribute must be of type Rooms, got {type(instance.rooms).__name__}."
        )

    if not isinstance(instance.lock, type(Lock())):
        raise TypeError(
            f"The 'lock' attribute must be of type Lock, got {type(instance.lock).__name__}."
        )

    from kin_sdk.agent_management.base import AgentManagement

    if not isinstance(instance.agent_management, AgentManagement):
        raise TypeError(
            f"The 'agent_management' attribute must be of type AgentManagement, got {type(instance.agent_management).__name__}."
        )

    from kin_sdk.agent_module._module.base import BaseModule

    if not issubclass(instance.module_class, BaseModule):
        raise TypeError(
            f"The 'module_class' attribute must be a subclass of BaseModule, got {instance.module_class.__name__}."
        )


def handle_start_error(context, code, message, details):
    """
    Handle an error response when starting a module.

    :param context: The gRPC context object.
    :param code: The gRPC status code.
    :param message: The error message.
    :param details: The error details.
    :return: A StartModuleResponse object.

    ===
    Example:
    ===
    ```
    handle_start_error(context, grpc.StatusCode.INVALID_ARGUMENT, "Invalid argument", "The input data is invalid.")
    ```
    """
    context.set_code(code)
    context.set_details(details)
    return StartModuleResponse(
        success=False,
        response_type="START_RESPONSE_TYPE_ERROR",
        error=ErrorResponse(
            message=message,
            details=details,
        ),
    )

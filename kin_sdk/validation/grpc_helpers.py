"""
TODO: sphinx docstring
"""

import uuid
from typing import Dict, Any
from asyncio import Lock

import grpc
from pydantic import BaseModel
from protovalidate import Violations

from proto.digitalkin.module.v1.lifecycle_pb2 import (
    MODULE_ROLE_MEMBRE,
    MODULE_ROLE_UNKNOWN,
    REQUEST_TYPE_CONNECTION,
    StartModuleRequest,
    StartModuleResponse,
    ErrorResponse,
    ModuleRole as ModuleRolePB,
)
from kin_sdk.common.types import ModuleRole
from kin_sdk.common.logger import logger
from kin_sdk.models.metadata import Metadata


def get_metadata(
    request: StartModuleRequest, context: grpc.aio.ServicerContext
) -> Metadata:
    """
    Extract metadata from the gRPC request.

    :param request: The gRPC request object
    :param context: The gRPC context object
    :return: A Metadata object containing the extracted metadata
    :raises ValueError: If required metadata is missing or invalid
    """
    try:
        request_type = request.request_type
        if request_type != REQUEST_TYPE_CONNECTION:
            raise ValueError(
                "Request type should be `REQUEST_TYPE_CONNECTION` for the first connection to a room."
            )

        connection_request = (
            request.connection_request
            if request.HasField("connection_request")
            else None
        )
        if connection_request is None or not connection_request:
            raise ValueError("Connection request is missing.")

        module_id = (
            connection_request.module_id if connection_request.module_id else None
        )
        int_module_role = connection_request.module_role
        room_id = connection_request.room_id if connection_request.room_id else None

        if not module_id:
            raise ValueError("Module ID is missing.")

        if int_module_role is None or int_module_role is MODULE_ROLE_UNKNOWN:
            raise ValueError("Module role is missing.")

        if int_module_role == MODULE_ROLE_MEMBRE and not room_id:
            raise ValueError(
                "Module role should be `MODULE_ROLE_OWNER` if there is no `room_id` or should be `MODULE_ROLE_MEMBRE` with a `room_id`."
            )

        module_role = (
            ModuleRolePB.Name(int_module_role) if int_module_role is not None else None
        )
        return Metadata(
            module_id=module_id,
            module_role=ModuleRole.get(str(module_role)),
            room_id=uuid.UUID(room_id) if room_id and room_id is not None else None,
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
    input_data = request.get("input_request", {}).get("input", None)

    if input_data is None:
        raise ValueError(
            "The parameter 'input' is missing, it should be in the 'input_request' field."
        )

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


def format_violations(violations_message: Violations):
    """
    Format the violations message.

    :param violations_message: The Violations message object.
    :return: A formatted string containing the violations.
    """
    violations = violations_message.violations

    formatted_output = []

    for v in violations:  # Ignorer le premier élément vide
        field_path = v.field_path
        constraint_id = v.constraint_id
        message = v.message

        # Formater chaque violation
        formatted_violation = f"{field_path}" f"[{constraint_id}]: " f"{message}"
        formatted_output.append(formatted_violation)

    # Joindre toutes les violations formatées avec une ligne de séparation
    return "\n".join(formatted_output)


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

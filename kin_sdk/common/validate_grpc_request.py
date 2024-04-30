import time
import grpc
from functools import wraps
from typing import Dict, Any, Iterator, Callable

from google.protobuf import json_format, struct_pb2
from protoc_gen_validate.validator import validate, ValidationFailed


from kin_sdk.common import logger


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

"""
TODO: sphinx docstring
"""

import grpc
from pydantic import ValidationError
from google.protobuf import struct_pb2


def pydantic_validation_error(
    e: ValidationError, context: grpc.ServicerContext = None
) -> struct_pb2.Struct:  # pylint: disable=no-member
    """
    TODO: sphinx docstring
    """
    error_message = "😵 Validation Error: "

    for error in e.errors():
        loc = " -> ".join(map(str, error["loc"]))
        msg = error["msg"]
        error_type = error["type"]
        error_message += f"\nField: {loc}, Error: {msg}, Type: {error_type}"
    if context:
        context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
        context.set_details(error_message)

    return error_message

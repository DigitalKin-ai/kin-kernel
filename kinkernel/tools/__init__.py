"""
This package provides tools for wrapping and interacting with OpenAI's Functions.

The `OpenAiFunctionCell` class offers a high-level interface to execute BaseCell objects
asynchronously and to access their properties and input arguments schema in order to use them with OpenAI
functions.

The `cell_to_openai_function` function is a utility that converts a list of BaseCell objects
into a list of `OpenAiFunctionCell` instances for easier manipulation.

Classes:
    OpenAiFunctionCell: Wraps a BaseCell to provide a convenient interface for execution and property access.

Functions:
    cell_to_openai_function(cells): Converts a list of BaseCell objects into a list of OpenAiFunctionCell instances.
"""
from kinkernel.tools.openai_function_cell import (
    OpenAiFunctionCell,
    cell_to_openai_function,
)
from kinkernel.tools.json_schema_cleaner import replace_refs_with_defs

__all__ = ["OpenAiFunctionCell", "cell_to_openai_function", "replace_refs_with_defs"]

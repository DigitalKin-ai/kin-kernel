"""
This package provides the core components required to define and configure cells within the system.

A cell is an autonomous agent characterized by its role, input and output formats, and the
ability to execute specific tasks based on provided input data.

The package includes the following key components:
- `Cell`: A concrete class representing a cell, which can be further subclassed for specific behaviors.
- `EnvVar`: A model representing an environment variable as a key-value pair.
- `ConfigModel`: A model for defining configuration parameters for a cell, including environment variables.

By creating a centralized package for these components, the system ensures consistency
and ease of use when defining new types of cells and their configurations.

The `__all__` list in this module specifies the public components that are available for import
when the package is imported using the `from package import *` syntax.

Examples:
    >>> from kinkernel import Cell
    >>> from kinkernel import EnvVar, ConfigModel

    # Define a custom cell by subclassing `Cell`
    # Define custom configuration models using `ConfigModel` and `EnvVar`

"""
import sys
from kinkernel.cells import Cell
from kinkernel.config import EnvVar, ConfigModel

# Checking version
if sys.version_info < (3, 10, 11):
    raise RuntimeError("This project requires Python 3.10.11 or higher.")


__all__ = ["Cell", "EnvVar", "ConfigModel"]

"""
This module defines configuration models for the system, particularly focusing on environment variables.

The `EnvVar` class encapsulates the concept of an environment variable as a key-value pair, while
the `ConfigModel` class provides a structured way to define and store configuration details for a cell,
including a list of environment variables.

Classes:
    EnvVar: Represents a single environment variable.
    ConfigModel: Holds the entire configuration for a cell, which may include multiple environment variables.

Usage:
    # Define a single environment variable
    env_var = EnvVar(key='DATABASE_URL', value='postgres://user:password@localhost/db')

    # Define a configuration model with one or more environment variables
    config = ConfigModel(env_vars=[env_var])

You can extend `ConfigModel` to include additional configuration parameters specific to your application's needs.
"""

from typing import List, Optional
from pydantic import BaseModel


class EnvVar(BaseModel):
    """
    Represents an environment variable as a key-value pair.

    Attributes:
        key (str): The name of the environment variable.
        value (str): The value associated with the environment variable.
    """

    key: str
    value: str


class ConfigModel(BaseModel):
    """
    Defines the configuration for a cell with an optional list of environment variables.

    The model can be extended to include additional configuration parameters as needed.

    Attributes:
        env_vars (Optional[List[EnvVar]]): A list of `EnvVar` instances representing
            environment variables. Defaults to an empty list if not provided.
    """

    env_vars: Optional[List[EnvVar]] = []

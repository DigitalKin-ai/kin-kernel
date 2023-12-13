"""
This module serves as the entry point for the `kinkernel.config` package. It re-exports
the `EnvVar` and `ConfigModel` classes from the `kinkernel.config.base` module.

The `EnvVar` class is used to represent environment variables as key-value pairs,
while the `ConfigModel` class allows for defining and managing a set of configuration
parameters for a cell, which can include environment variables and potentially other
settings.

Example:
    from kinkernel.config import EnvVar, ConfigModel

    # Create an environment variable instance
    database_url = EnvVar(key='DATABASE_URL', value='postgres://user:password@localhost/db')

    # Create a configuration model with the environment variable
    config = ConfigModel(env_vars=[database_url])

See Also:
    `kinkernel.config.base`: The module where `EnvVar` and `ConfigModel` are defined.

Available Classes:
    - `EnvVar`: Represents a single environment variable.
    - `ConfigModel`: Holds the configuration for a cell, which may include multiple environment variables.

"""
from kinkernel.config.base import EnvVar, ConfigModel


__all__ = ["EnvVar", "ConfigModel"]

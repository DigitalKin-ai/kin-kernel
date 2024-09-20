"""
TODO: sphinx docstring
"""

from kin_sdk.agent_management._database import ModuleDatabase, ParamsModuleDatabase
from kin_sdk.agent_management._identity import ModuleIdentity, ParamsModuleIdentity
from kin_sdk.agent_management._registry import ModuleRegistry, ParamsModuleRegistry


class AgentManagement:
    """
    The AgentManagement class is the main class of the agent management module.
    """

    def __init__(
        self,
        params_identity: ParamsModuleIdentity,
        params_registry: ParamsModuleRegistry,
        params_database: ParamsModuleDatabase,
    ):
        """
        Initializes the AgentManagement object.
        """
        self._identity = ModuleIdentity.from_params(params_identity)
        self._registry = ModuleRegistry.from_params(params_registry)
        self._database = ModuleDatabase.from_params(params_database)
        self._storage = None

    @property
    def identity(self) -> ModuleIdentity:
        """
        Returns the identity of the agent.
        """
        return self._identity

    @property
    def registry(self) -> ModuleRegistry:
        """
        Returns the registry of the agent.
        """
        return self._registry

    @property
    def database(self) -> ModuleDatabase:
        """
        Returns the database of the agent.
        """
        return self._database

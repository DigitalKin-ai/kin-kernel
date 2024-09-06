"""
TODO: sphinx docstring
"""

from kin_sdk.agent_management.identity import ModuleIdentity, ParamsModuleIdentity


class AgentManagement:
    """
    The AgentManagement class is the main class of the agent management module.
    """

    def __init__(self, params_identity: ParamsModuleIdentity):
        """
        Initializes the AgentManagement object.
        """
        self._identity = ModuleIdentity.from_params(params_identity)
        self._registry = None
        self._storage = None

    @property
    def identity(self) -> ModuleIdentity:
        """
        Returns the identity of the agent.
        """
        return self._identity

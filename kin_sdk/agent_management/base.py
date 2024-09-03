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
        self.identity = ModuleIdentity.from_params(params_identity)

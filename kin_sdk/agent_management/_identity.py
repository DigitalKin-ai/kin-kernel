"""
TODO: sphinx documentation
"""

from dataclasses import dataclass
from kin_sdk.common.types import ModuleType


@dataclass
class ParamsModuleIdentity:
    """
    The ParamsModuleIdentity class represents the parameters required to create a ModuleIdentity object.
    """

    module_id: str
    module_type: ModuleType
    module_address: str
    module_port: int


class ModuleIdentity:
    """
    The ModuleIdentity class represents the identity of a module in the system.
    """

    def __init__(
        self,
        module_id: str,
        module_type: ModuleType,
        module_address: str,
        module_port: int,
    ):
        """
        Initializes the ModuleIdentity object with the given details.

        :param module_id: The unique identifier of the module.
        :type module_id: str
        :param module_type: The type of the module.
        :type module_type: ModuleType
        :param module_address: The address of the module.
        :type module_address: str
        :param module_port: The port number of the module.
        :type module_port: int
        """
        self._module_id: str = module_id
        self._module_type: ModuleType = module_type
        self._module_address: str = module_address
        self._module_port: int = module_port

    @classmethod
    def from_params(cls, params: ParamsModuleIdentity) -> "ModuleIdentity":
        """
        Creates a ModuleIdentity object from the given parameters.
        """
        return cls(**params.__dict__)

    @property
    def id(self) -> str:
        """
        Returns the module ID.

        :return: The module ID.
        :rtype: str
        """
        return self._module_id

    @property
    def type(self) -> ModuleType:
        """
        Returns the module type.

        :return: The module type.
        :rtype: ModuleType
        """
        return self._module_type

    @property
    def address(self) -> str:
        """
        Returns the module address.

        :return: The module address.
        :rtype: str
        """
        return self._module_address

    @property
    def port(self) -> int:
        """
        Returns the module port.

        :return: The module port.
        :rtype: int
        """
        return self._module_port

    def __str__(self) -> str:
        """
        Returns a string representation of the ModuleIdentity object.

        :return: The string representation of the ModuleIdentity object.
        :rtype: str
        """
        return f"ModuleIdentity(id={self.id}, type={str(self.type)}, address={self.address}, port={self.port})"

    def __repr__(self) -> str:
        """
        Returns a string representation of the ModuleIdentity object.

        :return: The string representation of the ModuleIdentity object.
        :rtype: str
        """
        return self.__str__()

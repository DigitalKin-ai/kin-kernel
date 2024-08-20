"""
This module contains the model for the service object.
"""

import warnings
from pydantic import BaseModel

from kin_sdk.common.types import ServiceType, ModuleType


# !deprecated please remove
class ServiceModel(BaseModel):
    service_id: str
    service_type: ServiceType
    address: str
    port: int


# Deprecate the old class
# TODO remove
class DeprecatedServiceModel(ServiceModel):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "ServiceType is deprecated, use ModuleType instead",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


# Alias the old class to the new one
ServiceModel = DeprecatedServiceModel


class ModuleModel(BaseModel):
    module_id: str
    module_type: ModuleType
    address: str
    port: int

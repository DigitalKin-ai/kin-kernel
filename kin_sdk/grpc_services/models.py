"""
This module contains the model for the service object.
"""

from pydantic import BaseModel

from kin_sdk.common.types import ServiceType


class ServiceModel(BaseModel):
    service_id: str
    service_type: ServiceType
    address: str
    port: int

"""
This module contains the model for the service object.
"""

from pydantic import BaseModel


class ServiceModel(BaseModel):
    service_id: str
    service_type: str
    address: str
    port: int

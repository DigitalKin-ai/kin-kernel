from typing import Type, Literal, Optional

import grpc
from google.protobuf import json_format

import proto.digitalkin.service.v1.registry.service_registry_pb2_grpc as service_registry_pb2_grpc
import proto.digitalkin.service.v1.registry.service_registry_pb2 as service_registry_pb2
import proto.digitalkin.service.v1.trigger.trigger_service_pb2_grpc as trigger_service_pb2_grpc
import proto.digitalkin.service.v1.trigger.trigger_service_pb2 as trigger_service_pb2

from kin_sdk.grpc_services.models import ServiceModel
from kin_sdk.grpc_services.grpc_server_base import GRPCServerBase
from kin_sdk.common import logger, ServiceType


class ServiceServer(GRPCServerBase):
    """
    Base class for all specific service servers (Kin, Tool, Trigger).
    This class provides common functionalities for service registration.
    """

    def __init__(
        self,
        service_id: str,
        service_address: str,
        service_port: int,
        service_type: ServiceType,
        registry_address: str,
        servicer_class: Type,
        servicer_args: tuple = (),
        servicer_kwargs: dict = {},
        max_workers: int = 10,
    ):
        super().__init__(
            servicer_class=servicer_class,  # type: ignore
            port=service_port,
            servicer_args=servicer_args,
            servicer_kwargs=servicer_kwargs,
            max_workers=max_workers,
        )

        self.service_id = service_id
        self.service_address = service_address
        self.service_port = service_port
        self.service_type = service_type
        self.registry_address = registry_address

    def register_service(self):
        """
        Registers the service with the Service Registry.

        Args:
            service_id (str): Unique identifier for the service.
            service_type (str): Type of the service (e.g., 'trigger', 'tool', 'kin').

        Returns:
            bool: True if registration is successful, False otherwise.
        """
        with grpc.insecure_channel(self.registry_address) as channel:
            stub = service_registry_pb2_grpc.ServiceRegistryStub(channel)
            request = service_registry_pb2.RegisterRequest(
                service_id=self.service_id,
                service_type=self.service_type,
                address=self.service_address,
                port=self.port,
            )
            response = stub.RegisterService(request)
            return response.success

    def search_service(self, service_id: str) -> Optional[ServiceModel]:
        """
        Searches for a service in the Service Registry.

        Args:
            service_id (str): Unique identifier for the service.

        Returns:
            ServiceModel: ServiceModel if the service is found, None otherwise.
        """
        try:
            with grpc.insecure_channel(self.registry_address) as channel:
                stub = service_registry_pb2_grpc.ServiceRegistryStub(channel)
                request = service_registry_pb2.DiscoverRequest(service_id=service_id)
                response = stub.DiscoverService(request)
                json_response = json_format.MessageToDict(
                    response,
                    preserving_proto_field_name=True,
                )
                service_model = {
                    "service_id": service_id,
                    "service_type": json_response.get("service_type", None),
                    "address": json_response.get("address", None),
                    "port": json_response.get("port", None),
                }
                return ServiceModel.model_validate(service_model)
        except Exception as e:
            logger.error(f"Error searching for service: {e}")
            return None

    def deregister_service(self):
        """
        Deregisters the service from the Service Registry.

        Args:
            service_id (str): Unique identifier for the service.

        Returns:
            bool: True if deregistration is successful, False otherwise.
        """
        try:
            with grpc.insecure_channel(self.registry_address) as channel:
                stub = service_registry_pb2_grpc.ServiceRegistryStub(channel)
                request = service_registry_pb2.DeregisterRequest(
                    service_id=self.service_id
                )
                response = stub.DeregisterService(request)
                return response.success
        except Exception:
            logger.error("Error deregistering service: %s", self.service_port)
            return False

    def execute_service(self, service_id: str, input_data: dict) -> Optional[dict]:
        raise NotImplementedError

    def get_service_input(
        self, service_id: str, llm_format: bool = False
    ) -> Optional[ServiceModel]:
        """
        Get the input of a service.

        Args:
            service_id (str): Unique identifier for the service.

        Returns:
            bool: True if the service is found, False otherwise.
        """
        try:
            service_model: ServiceModel = self.search_service(service_id)

            if service_model is None:
                raise ValueError(
                    f"The service: {service_id} is not found in the service registry"
                )

            with grpc.insecure_channel(
                f"{service_model.address}:{service_model.port}"
            ) as channel:
                stub = trigger_service_pb2_grpc.TriggerServiceStub(channel)
                request = trigger_service_pb2.GetTriggerInputRequest(
                    trigger_id=service_model.service_id,
                    llm_format=llm_format,
                )
                print(service_model)
                response = stub.GetTriggerInput(request)
                json_response = json_format.MessageToDict(
                    response,
                    preserving_proto_field_name=True,
                )
                return json_response
        except Exception as e:
            logger.error(f"Error retreaving inputs for service {service_id}: {e}")
            return None

    def serve(self) -> None:
        """
        Starts the service server, binds it to the specified port, and waits for termination.

        The server runs indefinitely until an external interruption or termination.
        """
        try:
            if self.register_service():
                super().serve()
            else:
                raise Exception("Service registration failed.")
        finally:
            self.deregister_service()
            print("Service deregistered.")

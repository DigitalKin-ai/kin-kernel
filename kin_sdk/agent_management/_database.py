"""
TODO: Implement database for agent management
"""

from dataclasses import dataclass
from google.protobuf import json_format

from digitalkin.setup.v2.setup_pb2 import ReadSetupRequest, GetInstanceSetupRequest
from digitalkin.setup.v2.setup_service_pb2_grpc import SetupServiceStub
from digitalkin.project.v1.project_service_pb2_grpc import ProjectServiceStub
from digitalkin.project.v1.workflow_pb2 import ReadWorkflowRequest
from kin_sdk.certificates._certificates import grpc_channel
from kin_sdk.common.logger import logger


@dataclass
class ParamsModuleDatabase:
    """
    The ParamsModuleRegistry class represents the parameters required to create a ModuleDatabase object.
    """

    database_address: str


class ModuleDatabase:
    """
    The ModuleDatabase class represents the database for the agent management system.
    """

    def __init__(
        self,
        database_address: str,
    ):
        self._database_address = database_address

    @classmethod
    def from_params(cls, params: ParamsModuleDatabase) -> "ParamsModuleDatabase":
        """
        Creates a ModuleDatabase object from the given parameters.
        """
        return cls(**params.__dict__)

    async def load_workflow(self, kin_id: str) -> dict:
        """ "
        Load a workflow from the database.

        Args:
            kin_id (str): The kin_id of the workflow to load.

        Returns:
            dict: The workflow data.
        """
        try:
            channel = grpc_channel(self._database_address)
            stub = ProjectServiceStub(channel)
            request = ReadWorkflowRequest(kin_id=f"kins:{kin_id}")
            response_iterator = stub.ReadWorkflow(request)

            json_responses = None
            async for response in response_iterator:
                json_response = json_format.MessageToDict(
                    response,
                    preserving_proto_field_name=True,
                )
                json_responses = json_response
            return json_responses
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error loading workflow: %s", str(e))
            return None

    async def load_setup(self, setup_id: str) -> dict:
        """
        Load a setup from the database.

        Args:
            setup_id (str): The setup_id of the setup to load.

        Returns:
            dict: The setup data.
        """
        try:
            channel = grpc_channel(self._database_address)
            stub = SetupServiceStub(channel)
            request = ReadSetupRequest(setup_id=setup_id)
            response = await stub.ReadSetup(request)
            return json_format.MessageToDict(
                response,
                preserving_proto_field_name=True,
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error loading setup: %s", str(e))
            return None

    async def load_instance_setup(self, setup_id: str, instance_id: str) -> dict:
        """
        Load a specific instance setup from the database.

        Args:
            instance_id (str): The instance_id of the instance to load.
            setup_id (str): The setup_id of the setup to load.

        Returns:
            dict: The setup data.
        """
        try:
            print("Loading setup...", setup_id, instance_id)
            channel = grpc_channel(self._database_address)
            stub = SetupServiceStub(channel)
            request = GetInstanceSetupRequest(
                setup_id=setup_id, instance_id=instance_id
            )
            response = await stub.GetInstanceSetup(request)
            return json_format.MessageToDict(
                response,
                preserving_proto_field_name=True,
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error loading instance setup: %s", str(e))
            return None

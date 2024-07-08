"""
Todo: sphinx docstring
TODO: add await async every where
"""

import asyncio
from typing import Callable, Dict

from pydantic import BaseModel

from kin_sdk.grpc_services.models import ServiceModel
from kin_sdk.kin.base import BaseKin
from kin_sdk.common import logger
from kin_sdk.module.storage import DBStorage


class WorkflowInput(BaseModel):
    pass


class WorkflowOutput(BaseModel):
    numbers: float
    factor: float = 2.0  # Default factor is 2


class WorkflowSetup(BaseModel):
    result: float


class KinWorkflow(BaseKin):
    name: str = "Kin Workflow"
    description: str = "This is the Kin is in workflow mode."
    triggers: Dict[str, ServiceModel] = {}
    tools: Dict[str, ServiceModel] = {}
    input_format = WorkflowInput
    output_format = WorkflowOutput
    setup_format = WorkflowSetup

    def __init__(
        self,
        name: str,
        description: str,
        service_id: str,
        service_address: str,
        service_port: int,
        registry_address: str,
        max_workers: int = 10,
    ):
        self.name = name
        self.description = description
        super().__init__(
            service_id=service_id,
            service_address=service_address,
            service_port=service_port,
            registry_address=registry_address,
            max_workers=max_workers,
        )

        self.db_storage = DBStorage()

    def register_services(self, nodes: list[dict]) -> None:
        """
        Registers the services.
        """
        # add triggers and tools
        for x in nodes:
            # Retrieve the data from the node
            data = x.get("data", {})
            # Retrieve the data type from the node should be either trigger or tool
            data_type = data.get("type", None)
            # Retrieve the data id from the node
            data_id = data.get("id", None)

            # If the data_type is 'view', we skip the current node
            if data_type == "view":
                continue

            # If the data_id is None, we raise an error
            if data_id is None:
                raise ValueError(f"The {data_type}: id is missing")

            # Contact the service registry in order to find a specific trigger or tool
            service_model: ServiceModel = self.search_service(data_id)

            if service_model is None:
                raise ValueError(
                    f"The {data_type}: {data_id} is not found in the service registry"
                )

            # If the data_type is different from the service_type, we raise an error
            if data_type != service_model.service_type:
                raise ValueError(
                    f"The {data_type}: {data_id} has been registred as a {service_model.service_type} in the service registry but as a {service_model.service_type} in the workflow.",
                )

            if data_type == "trigger":
                self.triggers[data_id] = service_model
                logger.info("🏎️ Adding trigger service: %s to the list", data_id)
            elif data_type == "tool":
                self.tools[data_id] = service_model
                logger.info("🧰 Adding tool service: %s to the list", data_id)

    async def __load_workflow(self) -> None:
        """
        This method loads the workflow from the database.
        """
        workflows = await self.db_storage.storage_load(kin_id="test", table="workflows")
        if workflows is None:
            logger.error("Error loading workflow from the database.")
            return None
        return workflows[0]

    def start(self) -> None:
        """
        Starts the trigger.
        """
        # Load workflow from db
        workflow = asyncio.run(self.__load_workflow())

        # add triggers and tools
        self.register_services(workflow["nodes"])

        logger.info("🚀 Workflow has been started...")

    def execute(
        self,
        input_data: WorkflowInput,
        setup_data: WorkflowSetup,
        callback: Callable[[WorkflowOutput], None],
    ) -> None:
        """
        Executes the trigger.
        """
        # setup
        # kin_id
        # trigger_id
        print("Executing Kin Workflow...")

    def stop(self) -> None:
        """
        Stops the trigger.
        """
        print("Stopping Kin Workflow...")

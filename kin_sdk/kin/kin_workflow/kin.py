"""
Todo: sphinx docstring
TODO: add await async every where
"""

import asyncio
from typing import Callable, Dict, List, Any, Type
from pydantic import BaseModel, create_model, Field

from kin_sdk.grpc_services.models import ServiceModel
from kin_sdk.kin.base import BaseKin
from kin_sdk.common import logger
from kin_sdk.module.storage import DBStorage
from kin_sdk.kin.kin_workflow.graph import GraphExecutor


def update_model_with_fields(
    base_model: Type[BaseModel], fields_model: Type[BaseModel]
) -> Type[BaseModel]:
    """
    Update the base model with fields from another model.

    :param base_model: The base Pydantic model class to be updated.
    :param fields_model: The Pydantic model class whose fields will be added to the base model.
    :return: The updated Pydantic model class.
    """
    # Create a copy of the base model's annotations and fields
    updated_annotations = base_model.__annotations__.copy()
    updated_fields = {
        name: getattr(base_model, name) for name in base_model.__annotations__
    }

    # Add fields from the fields_model
    for field_name, field_type in fields_model.__annotations__.items():
        updated_annotations[field_name] = field_type
        updated_fields[field_name] = getattr(fields_model, field_name, ...)

    # Create a new model class with the updated annotations and fields
    updated_model = create_model(
        "UpdatedWorkflowInput",
        __base__=base_model,
        **{
            name: (field_type, updated_fields[name])
            for name, field_type in updated_annotations.items()
        },
    )

    return updated_model


class WorkflowInput(BaseModel):
    trigger_id: str = Field(..., description="trigger id of the class")


class WorkflowOutput(BaseModel):
    numbers: float
    factor: float = 2.0  # Default factor is 2


class WorkflowSetup(BaseModel):
    pass


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
        self.graphs_executor = None  # TODO manage multi connections

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
            if data_type != service_model.service_type.value:
                raise ValueError(
                    f"The {data_type}: {data_id} has been registred as a {service_model.service_type} in the service registry but as a {service_model.service_type} in the workflow.",
                )

            if data_type == "trigger":
                self.triggers[data_id] = service_model
                logger.info("🏎️ Adding trigger service: %s to the list", data_id)
            elif data_type == "tool":
                self.tools[data_id] = service_model
                logger.info("🧰 Adding tool service: %s to the list", data_id)

    async def __load_workflow(self, kin_id: str) -> List[Dict[str, Any]] | None:
        """
        This method loads the workflow from the database.

        :param kin_id: The kin_id of the workflow.
        :return: The workflow.
        """
        workflows = await self.db_storage.storage_load(kin_id=kin_id, table="workflows")
        if workflows is None:
            logger.error("Error loading workflow from the database.")
            return None
        return workflows[0]

    def get_kin_input(self) -> Dict[str, Any]:
        inputs_schema = {
            trigger_id: self.get_service_input(service_id=trigger_id)
            for _node_id, trigger_id in self.graphs_executor.get_services_nodes(
                "trigger"
            )
        }
        return inputs_schema

    async def get_kin_setup(self, kin_id, setup_id) -> Dict[str, Any]:
        setups = await self.db_storage.storage_load_setup(
            kin_id=kin_id, setup_id=setup_id
        )

        return setups

    def start(self, kin_id: str) -> None:
        """
        Starts the trigger.
        """
        try:
            # Load workflow from db
            workflow = asyncio.run(self.__load_workflow(kin_id=kin_id))

            # add triggers and tools
            self.register_services(workflow["nodes"])

            setups_id = "fibonacci_setup"  # TODO: get setup_id from params

            # load setups from db
            setups = asyncio.run(self.get_kin_setup(kin_id, setups_id))

            # create a graph executor
            self.graphs_executor = GraphExecutor(
                graph=workflow,
                setups=setups,
            )

            logger.info("🚀 Workflow has been started...")
        except Exception as e:
            logger.error(f"Error loading workflow: {e}")

        return None

    def execute(
        self,
        input_data: WorkflowInput,
        setup_id: str,
        callback: Callable[[WorkflowOutput], None],
    ) -> None:
        """
        Executes the trigger.
        """
        # dynamic input model
        print("trigger_id: ", input_data.trigger_id)
        inputs_schema = self.get_kin_input()
        print(inputs_schema.get(input_data.trigger_id, {}))

        initial_node = self.graphs_executor.get_node_id_by_service_id(
            input_data.trigger_id
        )

        sequence = [1, 1]

        async def service_callback(service_id: str):
            print(f"Service callback: {service_id}")
            if service_id == "fibonacci_trigger":
                return {"initial_numbers": (1, 1)}
            elif service_id == "sequence_tool":
                # inputs: initial_numbers / new_numbers
                return {"last_number": sequence[-1], "fibonacci_list": sequence}
            elif service_id == "addition_tool":
                # inputs: last_numbers (tuple)
                sequence.append(sequence[-1] + sequence[-2])
                return {"next_number": sequence[-1]}
            elif service_id == "display_tool":
                # inputs: fibonacci_list / new_number
                print(f"Sequence: {sequence}")
                return {}
            # raise NotImplementedError

        self.graphs_executor.execute(
            initial_node, service_callback
        )  # le noeud doit avoir des values
        # 2. declanchement du workflow avec les inputs du trigger
        print("Executing Kin Workflow...")

    def stop(self) -> None:
        """
        Stops the trigger.
        """
        print("Stopping Kin Workflow...")

"""
Todo: sphinx docstring
TODO: add await async every where
"""

import asyncio
from typing import Callable, Dict, List, Any, Type, Union
from pydantic import BaseModel, create_model, Field

from kin_sdk.grpc_system.models import ModuleModel
from kin_sdk.agent_module.kin.base import BaseKin
from kin_sdk.common import logger
from kin_sdk.agent_management import DBStorage
from kin_sdk.agent_module.kin.kin_workflow.graph import GraphExecutor


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
    """TODO : sphinx docstring"""

    trigger_id: str = Field(..., description="trigger id of the class")


class WorkflowOutput(BaseModel):
    """TODO : sphinx docstring"""

    numbers: float
    factor: float = 2.0  # Default factor is 2


class WorkflowSetup(BaseModel):
    """TODO : sphinx docstring"""


class KinWorkflow(BaseKin):
    """TODO : sphinx docstring"""

    name: str = "Kin Workflow"
    description: str = "This is the Kin is in workflow mode."
    triggers: Dict[str, ModuleModel] = {}
    tools: Dict[str, ModuleModel] = {}
    input_format = WorkflowInput
    output_format = WorkflowOutput
    setup_format = WorkflowSetup

    def __init__(
        self,
        name: str,
        description: str,
        module_id: str,
        module_address: str,
        module_port: int,
        registry_address: str,
        max_workers: int = 10,
    ):
        self.name = name
        self.description = description
        super().__init__(
            module_id=module_id,
            module_address=module_address,
            module_port=module_port,
            registry_address=registry_address,
            max_workers=max_workers,
        )

        self.db_storage = DBStorage()
        self.graphs_executor = None  # ! TODO manage multi connections

    def register_modules(self, nodes: list[dict]) -> None:
        """
        Registers the modules.
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

            # Contact the module registry in order to find a specific trigger or tool
            module_model: Union[ModuleModel, None] = self.search_module(data_id)

            if module_model is None:
                raise ValueError(
                    f"The {data_type}: {data_id} is not found in the module registry"
                )

            # If the data_type is different from the module_type, we raise an error
            if data_type != module_model.module_type.value:
                raise ValueError(
                    f"The {data_type}: {data_id} has been registred as a {module_model.module_type.value} in the module registry but as a {data_type} in the workflow.",
                )

            if data_type == "trigger":
                self.triggers[data_id] = module_model
                logger.info("🏎️ Adding trigger module: %s to the list", data_id)
            elif data_type == "tool":
                self.tools[data_id] = module_model
                logger.info("🧰 Adding tool module: %s to the list", data_id)

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
        """TODO : sphinx docstring"""
        inputs_schema = {
            trigger_id: self.get_module_input(module_id=trigger_id)
            for _node_id, trigger_id in self.graphs_executor.get_modules_nodes(
                "trigger"
            )
        }
        return inputs_schema

    async def get_kin_setup(self, kin_id, setup_id) -> Dict[str, Any]:
        """TODO : sphinx docstring"""
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
            self.register_modules(workflow["nodes"])

            setups_id = "fibonacci_setup"  # ! TODO: get setup_id from params

            # load setups from db
            setups = asyncio.run(self.get_kin_setup(kin_id, setups_id))

            # create a graph executor
            self.graphs_executor = GraphExecutor(
                graph=workflow,
                setups=setups,
            )

            logger.info("🚀 Workflow has been started...")
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error loading workflow: %s", e)

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
        # inputs_schema = self.get_kin_input()
        # print(inputs_schema.get(input_data.trigger_id, {}))

        initial_node = self.graphs_executor.get_node_id_by_module_id(
            input_data.trigger_id
        )

        sequence = [1, 1]

        async def module_callback(
            module_id: str, input_data: Dict[str, Any]
        ) -> Dict[str, Any]:
            # print(f"Module callback: {module_id}")
            print(f"input_data: {input_data}")
            response_iterator = self.start_module(
                module_id, input_data, setup_id, request_type="REQUEST_TYPE_VALIDATE"
            )
            result = {}
            for response in response_iterator:  # TODO, continue here
                response_type = response.get("response_type", None)
                print("\n---\nresponse_type: ", response_type)
                if (
                    response_type is not None
                    and response_type == "START_RESPONSE_TYPE_OUTPUT"
                ):
                    print(response)
                    output_response = response.get("output_response", {})
                    result = output_response.get("output", {})
                    print(f"response: {output_response.get('message', 'no message')}")
                    print(f"result: {result}")
                    break  # ? TODO check if we need to break here
                print(f"Response: {response}")
            # print(f"Input data: {input_data}")
            # if module_id == "fibonacci_trigger":
            #     return {"initial_numbers": (1, 1)}
            # elif module_id == "sequence_tool":
            #     # inputs: initial_numbers / new_numbers
            #     return {"last_number": sequence[-1], "fibonacci_list": sequence}
            # elif module_id == "addition_tool":
            #     # inputs: last_numbers (tuple)
            #     sequence.append(sequence[-1] + sequence[-2])
            #     return {"next_number": sequence[-1]}
            # elif module_id == "display_tool":
            #     # inputs: fibonacci_list / new_number
            #     print(f"Sequence: {sequence}")
            #     return {}
            return result
            # raise NotImplementedError

        self.graphs_executor.execute(
            initial_node, module_callback
        )  # le noeud doit avoir des values
        # 2. declanchement du workflow avec les inputs du trigger
        print("Executing Kin Workflow...")

    def stop(self) -> None:
        """
        Stops the trigger.
        """
        print("Stopping Kin Workflow...")

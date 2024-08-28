"""
Module for managing and executing workflows based on directed graphs of nodes.

This module includes the KinWorkflow class, which represents a workflow and provides
methods for registering modules, loading workflows, starting and stopping workflows,
and executing specific nodes.
"""

import asyncio
from typing import Callable, Dict, List, Any, Tuple, Union
from pydantic import BaseModel, create_model, Field

from kin_sdk.grpc_system.models import ModuleModel
from kin_sdk.agent_module.kin.base import BaseKin
from kin_sdk.common import logger
from kin_sdk.agent_management import DBStorage
from kin_sdk.agent_module.kin.kin_workflow.graph import GraphExecutor


# def update_model_with_fields(
#     base_model: Type[BaseModel], fields_model: Type[BaseModel]
# ) -> Type[BaseModel]:
#     """
#     Update the base model with fields from another model.

#     :param base_model: The base Pydantic model class to be updated.
#     :param fields_model: The Pydantic model class whose fields will be added to the base model.
#     :return: The updated Pydantic model class.
#     """
#     # Create a copy of the base model's annotations and fields
#     updated_annotations = base_model.__annotations__.copy()
#     updated_fields = {
#         name: getattr(base_model, name) for name in base_model.__annotations__
#     }

#     # Add fields from the fields_model
#     for field_name, field_type in fields_model.__annotations__.items():
#         updated_annotations[field_name] = field_type
#         updated_fields[field_name] = getattr(fields_model, field_name, ...)

#     # Create a new model class with the updated annotations and fields
#     updated_model = create_model(
#         "UpdatedWorkflowInput",
#         __base__=base_model,
#         **{
#             name: (field_type, updated_fields[name])
#             for name, field_type in updated_annotations.items()
#         },
#     )

#     return updated_model


class WorkflowInput(BaseModel):
    """
    Model for workflow input data.

    Attributes:
        trigger_id (str): The trigger ID of the workflow.
    """

    trigger_id: str = Field(..., description="Trigger ID of the workflow")


class WorkflowOutput(BaseModel):
    """
    Model for workflow output data.

    Attributes:
        done (bool): Define if the kin has done.
    """

    done: bool = False


class WorkflowSetup(BaseModel):
    """
    Model for workflow setup data.
    """


class KinWorkflow(BaseKin):
    """
    Manages and executes workflows based on directed graphs of nodes.

    Attributes:
        name (str): The name of the workflow.
        description (str): The description of the workflow.
        triggers (Dict[str, ModuleModel]): The triggers in the workflow.
        tools (Dict[str, ModuleModel]): The tools in the workflow.
        input_format (Type[BaseModel]): The input format for the workflow.
        output_format (Type[BaseModel]): The output format for the workflow.
        setup_format (Type[BaseModel]): The setup format for the workflow.
    """

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
        self._name = name
        self._description = description
        super().__init__(
            module_id=module_id,
            module_address=module_address,
            module_port=module_port,
            registry_address=registry_address,
            max_workers=max_workers,
        )

        self._db_storage = DBStorage()
        self._graphs_executor = None

    @property
    def db_storage(self) -> DBStorage:
        """Get the database storage."""
        return self._db_storage

    @property
    def graphs_executor(self) -> Union[GraphExecutor, None]:
        """Get the graphs executor."""
        return self._graphs_executor

    def get_modules_by_type(
        self, nodes: List[Dict[str, Any]]
    ) -> Dict[str, List[Tuple[str, ModuleModel]]]:
        """
        Retrieves modules by type from the given nodes.

        Args:
            nodes (List[Dict[str, Any]]): The nodes to retrieve modules from.

        Returns:
            Dict[str, List[Tuple[str, ModuleModel]]]: A dictionary with module types as keys and lists of ModuleModel as values.
        """
        modules_by_type = {"trigger": [], "tool": []}

        for x in nodes:
            data = x.get("data", {})
            data_type = data.get("type", None)
            data_id = data.get("id", None)

            if data_type == "view":
                continue

            if data_id is None:
                raise ValueError(f"The {data_type}: id is missing")

            module_model: Union[ModuleModel, None] = self.search_module(data_id)

            if module_model is None:
                raise ValueError(
                    f"The {data_type}: {data_id} is not found in the module registry"
                )

            if data_type != module_model.module_type.value:
                raise ValueError(
                    f"The {data_type}: {data_id} has been registered as a {module_model.module_type.value} in the module registry but as a {data_type} in the workflow.",
                )

            if data_type in modules_by_type:
                modules_by_type[data_type].append((data_id, module_model))

        return modules_by_type

    def register_modules(self, nodes: List[Dict[str, Any]]) -> None:
        """
        Registers the modules.

        Args:
            nodes (List[Dict[str, Any]]): The nodes to register.
        """
        modules_by_type = self.get_modules_by_type(nodes)

        for data_id, module_model in modules_by_type["trigger"]:
            self.triggers[data_id] = module_model
            logger.info("🏎️ Adding trigger module: %s to the list", data_id)

        for data_id, module_model in modules_by_type["tool"]:
            self.tools[data_id] = module_model
            logger.info("🧰 Adding tool module: %s to the list", data_id)

        # # Update the WorkflowInput model with the inputs from the triggers
        # self.update_workflow_input_model()

    async def _load_workflow(self, kin_id: str) -> Union[List[Dict[str, Any]], None]:
        """
        Loads the workflow from the database.

        Args:
            kin_id (str): The kin_id of the workflow.

        Returns:
            Union[List[Dict[str, Any]], None]: The workflow.
        """
        workflows = await self._db_storage.storage_load(
            kin_id=kin_id, table="workflows"
        )
        if workflows is None:
            logger.error("Error loading workflow from the database.")
            return None
        return workflows[0]

    # def get_kin_input(self) -> Dict[str, Any]:
    #     """
    #     Gets the input schema for the workflow.

    #     Returns:
    #         Dict[str, Any]: The input schema.
    #     """
    #     inputs_schema = {
    #         trigger_id: self.get_module_input(module_id=trigger_id)
    #         for _node_id, trigger_id in self._graphs_executor.get_modules_nodes(
    #             "trigger"
    #         )
    #     }
    #     return inputs_schema

    def update_workflow_input_model(self, nodes: List[Dict[str, Any]]) -> None:
        """
        Updates the WorkflowInput model with the inputs from the triggers.

        Args:
            nodes (List[Dict[str, Any]]): The nodes to register.
        """
        modules_by_type = self.get_modules_by_type(nodes)
        # Create a dictionary to store the trigger models
        trigger_models = {}

        # Add fields from each trigger
        for trigger_id, trigger_model in modules_by_type["trigger"]:
            trigger_inputs = self.get_module_input(trigger_id)
            if "properties" in trigger_inputs:
                trigger_fields = {
                    input_name: (input_type, ...)
                    for input_name, input_type in trigger_inputs["properties"].items()
                }
                trigger_model = create_model(f"{trigger_id}Input", **trigger_fields)
                trigger_models[trigger_id] = trigger_model

        # Create a new WorkflowInput model with the updated fields
        fields = {
            "trigger_id": (str, Field(..., description="Trigger ID of the workflow")),
            "triggers": (
                List[Union[tuple(trigger_models.values())]],
                Field(..., description="Triggers"),
            ),
        }
        self.input_format = create_model("WorkflowInput", **fields)

    async def get_kin_setup(self, kin_id: str, setup_id: str) -> Dict[str, Any]:
        """
        Gets the setup data for the workflow.

        Args:
            kin_id (str): The kin_id of the workflow.
            setup_id (str): The setup_id of the workflow.

        Returns:
            Dict[str, Any]: The setup data.
        """
        setups = await self._db_storage.storage_load_setup(
            kin_id=kin_id, setup_id=setup_id
        )
        return setups

    def start(self, kin_id: str, setups_id: str = "fibonacci_setup") -> None:
        """
        Starts the workflow.

        Args:
            kin_id (str): The kin_id of the workflow.
            setups_id (str): The setups_id of the workflow.
        """
        try:
            # Load workflow from db
            workflow = asyncio.run(self._load_workflow(kin_id=kin_id))

            # Add triggers and tools
            self.register_modules(workflow["nodes"])
            self.update_workflow_input_model(workflow["nodes"])
            import json

            print(json.dumps(self.input_format.model_json_schema(), indent=2))
            # Load setups from db
            setups = asyncio.run(self.get_kin_setup(kin_id, setups_id))

            # Create a graph executor
            self._graphs_executor = GraphExecutor(
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
        Executes the workflow.

        Args:
            input_data (WorkflowInput): The input data for the workflow.
            setup_id (str): The setup ID for the workflow.
            callback (Callable[[WorkflowOutput], None]): The callback function to handle the output.
        """
        initial_node = self._graphs_executor.get_node_id_by_module_id(
            input_data.trigger_id
        )

        async def module_callback(
            module_id: str, input_data: Dict[str, Any]
        ) -> Dict[str, Any]:
            response_iterator = self.start_module(
                module_id, input_data, setup_id, request_type="REQUEST_TYPE_VALIDATE"
            )
            result = {}
            for response in response_iterator:
                response_type = response.get("response_type", None)
                if (
                    response_type is not None
                    and response_type == "START_RESPONSE_TYPE_OUTPUT"
                ):
                    output_response = response.get("output_response", {})
                    result = output_response.get("output", {})
                    break
            callback(WorkflowOutput(done=False))
            return result

        self._graphs_executor.execute(initial_node, module_callback)
        print("Executing Kin Workflow...")
        callback(WorkflowOutput(done=True))

    def stop(self) -> None:
        """
        Stops the trigger.
        """
        print("Stopping Kin Workflow...")

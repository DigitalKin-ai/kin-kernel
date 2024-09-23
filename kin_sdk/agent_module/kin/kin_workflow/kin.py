"""
Module for managing and executing workflows based on directed graphs of nodes.

This module includes the KinWorkflow class, which represents a workflow and provides
methods for registering modules, loading workflows, starting and stopping workflows,
and executing specific nodes.
"""

import asyncio
from typing import Awaitable, Callable, Dict, List, Any, Tuple, Union
from pydantic import BaseModel, Field

from kin_sdk.models.module import ModuleModel
from kin_sdk.agent_module.kin.base import BaseKin
from kin_sdk.common.logger import logger
from kin_sdk.agent_management import DBStorage
from kin_sdk.agent_module.kin.kin_workflow.graph import GraphExecutor


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
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
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

    async def get_modules_by_type(
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

            module_model: Union[ModuleModel, None] = (
                await self.registry.find_module_by_id(data_id)
            )

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

    async def register_modules(self, nodes: List[Dict[str, Any]]) -> None:
        """
        Registers the modules.

        Args:
            nodes (List[Dict[str, Any]]): The nodes to register.
        """
        modules_by_type = await self.get_modules_by_type(nodes)

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
        workflows = await self.database.load_workflow(kin_id)
        if workflows is None:
            logger.error("Error loading workflow from the database.")
            return None
        return workflows

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
            kin_id=f"kins:{kin_id}", setup_id=setup_id
        )
        return setups

    async def start(self, setup_id: str = "fibonacci_setup") -> None:
        """
        Starts the workflow.

        Args:
            kin_id (str): The kin_id of the workflow.
            setups_id (str): The setups_id of the workflow.
        """
        try:
            logger.info("🚀 Starting workflow...")
            # Load workflow from db
            workflow = await self._load_workflow(kin_id=self.identity.id)
            print("debug 1")
            # Add triggers and tools
            await self.register_modules(workflow["nodes"])
            print("debug 2")

            # Load setups from db
            setups = await self.get_kin_setup(
                kin_id=self.identity.id, setup_id=setup_id
            )
            print("debug 3")

            # Create a graph executor
            self._graphs_executor = GraphExecutor(
                graph=workflow,
                setups=setups,
            )
            print("debug 4")

            print("Graphs Executor: ", self._graphs_executor)

            logger.info("🚀 Workflow has been started...")
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error loading workflow: %s", e)
            raise e

        return None

    async def execute(
        self,
        input_data: WorkflowInput,
        setup_id: str,
        callback: Callable[[WorkflowOutput], Awaitable[None]],
    ) -> None:
        """
        Executes the workflow.

        Args:
            input_data (WorkflowInput): The input data for the workflow.
            setup_id (str): The setup ID for the workflow.
            callback (Callable[[WorkflowOutput], None]): The callback function to handle the output.
        """
        logger.info("🚀 Executing Kin Workflow...")
        print("self._graphs_executor: ", self._graphs_executor)
        initial_node = self._graphs_executor.get_node_id_by_module_id(
            input_data.trigger_id
        )

        async def module_callback(
            module_id: str, input_data: Dict[str, Any], node_id: str
        ) -> Dict[str, Any]:
            print("--" * 10)
            response_iterator = self.registry.start_module(
                module_id=module_id,
                messages=[
                    {
                        "connection_request": {
                            "request_type": "REQUEST_TYPE_CONNECTION",
                            "module_role": "MODULE_ROLE_OWNER",
                        }
                    },
                    {
                        "input_request": {
                            "input_data": input_data,
                            "setup_id": f"{setup_id}::nodes:{node_id}",
                            "request_type": "REQUEST_TYPE_VALIDATE",
                        }
                    },
                ],
            )
            result = {}
            print("--" * 10)
            async for response in response_iterator:
                response_type = response.get("response_type", None)
                print(f"response_type: {response_type}")
                if (
                    response_type is not None
                    and response_type == "START_RESPONSE_TYPE_OUTPUT"
                ):
                    output_response = response.get("output_response", {})
                    result = output_response.get("output", {})
                    break
            print(WorkflowOutput(done=False))
            await asyncio.sleep(1)
            await callback(WorkflowOutput(done=False))
            await asyncio.sleep(1)
            print("--" * 10)
            return result

        await self._graphs_executor.execute(initial_node, module_callback)
        print("Executing Kin Workflow...")
        await callback(WorkflowOutput(done=True))

    async def stop(self) -> None:
        """
        Stops the trigger.
        """
        print("Stopping Kin Workflow...")

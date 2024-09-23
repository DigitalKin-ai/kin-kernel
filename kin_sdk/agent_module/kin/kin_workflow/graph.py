"""
Module for executing a directed graph of nodes asynchronously.

This module includes the GraphExecutor class, which represents a directed graph
of nodes and provides methods for executing the nodes in parallel and updating
their inputs and outputs.
"""

import datetime
import asyncio
from typing import Any, Awaitable, Dict, List, Callable, Union, Tuple, Optional
from queue import Queue

import networkx as nx

from kin_sdk.common.types import ModuleType
from kin_sdk.agent_module.kin.kin_workflow.edge import Edge
from kin_sdk.agent_module.kin.kin_workflow.node import InputData, Node, OutputData


class GraphExecutor:
    """
    Executes a directed graph of nodes asynchronously.
    TODO: check all @property that I should remove to keep only the one that are really needed.

    Attributes:
        _graph (nx.DiGraph): The directed graph.
        _nodes (Dict[str, Node]): The nodes in the graph.
        _setups (Dict[str, Any]): The setups configuration.
        _error_occurred (asyncio.Event): An event to signal if an error occurred.
        _execution_queue (Queue): A queue to manage node execution order.
        _lock (asyncio.Lock): A lock to ensure thread safety.
    """

    def __init__(self, graph: Dict[str, Any], setups: Dict[str, Any]):
        self._graph = nx.DiGraph()
        self._nodes = self._init_nodes(graph["nodes"], setups)
        self._init_edges(graph["edges"])
        self._setups = setups

        self._error_occurred = asyncio.Event()
        self._execution_queue = Queue()
        self._lock = asyncio.Lock()

    @property
    def graph(self) -> nx.DiGraph:
        """Get the directed graph."""
        return self._graph

    @property
    def nodes(self) -> Dict[str, Node]:
        """Get the nodes in the graph."""
        return self._nodes

    @property
    def setups(self) -> Dict[str, Any]:
        """Get the setups configuration."""
        return self._setups

    @property
    def execution_queue(self) -> Queue:
        """Get the execution queue."""
        return self._execution_queue

    def _init_nodes(
        self, nodes: List[Dict[str, Any]], setups: Dict[str, Any]
    ) -> Dict[str, Node]:
        """
        Initialize the nodes in the graph.

        Args:
            nodes (List[Dict[str, Any]]): The nodes to initialize.
            setups (Dict[str, Any]): The setups configuration.

        Returns:
            Dict[str, Node]: The initialized nodes.

        Raises:
            ValueError: If there's an error initializing nodes.
        """
        try:
            # Format the setups data
            formatted_setups = {
                data["module_id"]: data.get("content", {})
                for data in setups.get("data", [])
                if data.get("module_id") is not None
            }

            return {
                node["id"]: Node(
                    node_id=node["id"],
                    node_type=node["type"],
                    module_type=ModuleType.get(node.get("data", {})["type"]),
                    module_id=node.get("data", {})["id"],
                    inputs=node.get("data", {}).get("targets", []),
                    outputs=node.get("data", {}).get("sources", []),
                    setup=formatted_setups.get(
                        f"modules:{node.get('data', {})['id']}", {}
                    ),
                )
                for node in nodes
            }
        except Exception as e:  # pylint: disable=broad-except
            raise ValueError(f"Error initializing nodes: {str(e)}") from e

    def _init_edges(self, edges: List[Dict[str, Any]]) -> None:
        """
        Add edges to the graph.

        Args:
            edges (List[Dict[str, Any]]): The edges to add.

        Raises:
            ValueError: If there's an error initializing edges.
        """
        try:
            for edge in edges:
                source_handle = edge.get("source_handle", "").split(":::") + ["", ""]
                target_handle = edge.get("target_handle", "").split(":::") + ["", ""]

                # Add the edge to the graph
                self._graph.add_edge(
                    edge["source"],
                    edge["target"],
                    metadata=Edge(
                        source=edge["source"],
                        target=edge["target"],
                        source_handle={
                            "type": source_handle[0],
                            "label": source_handle[1],
                        },
                        target_handle={
                            "type": target_handle[0],
                            "label": target_handle[1],
                        },
                    ),
                )
        except Exception as e:  # pylint: disable=broad-except
            raise ValueError(f"Error initializing edges: {e}") from e

    def get_modules_nodes(self, module_type: ModuleType) -> List[Tuple[str, str]]:
        """
        Get nodes of a specific type from the graph.

        Args:
            module_type (ModuleType): The type of module to search for.

        Returns:
            List[Tuple[str, str]]: List of tuples containing node ID and module ID.
        """
        return [
            (node_id, node.module_id)
            for node_id, node in self._nodes.items()
            if node.module_type == module_type
        ]

    def get_node_id_by_module_id(self, module_id: str) -> str:
        """
        Returns the node id by module id.

        Args:
            module_id (str): The module id to search for.

        Returns:
            str: The ID of the node.
        """
        for node_id, node in self._nodes.items():
            if node.module_id == module_id:
                return node_id
        return ""

    def update_successor_inputs(
        self,
        successor_id: str,
        source_data: Dict[str, OutputData],
        edge_data_pred_succ: Union[Edge, None],
    ) -> None:
        """
        Update the inputs/target of a successor node based on the output/source of a predecessor node.

        Args:
            successor_id (str): The ID of the successor node.
            source_data (Dict[str, OutputData]): The output data from the predecessor node.
            edge_data_pred_succ (Optional[Edge]): The edge data connecting the predecessor node with successor.
        """
        if edge_data_pred_succ is None:
            print("No edge data")
            return

        successor: Union[Node, None] = self._nodes.get(successor_id, None)
        source_label = edge_data_pred_succ.get_source_label()
        target_label = edge_data_pred_succ.get_target_label()

        if successor is None or source_label is None or target_label is None:
            return

        for label in source_data:
            if label == source_label:
                successor.update_input(target_label, source_data[label].value)
                break

    @staticmethod
    def verify_input_values(input_data: Dict[str, InputData]) -> bool:
        """
        Verify if all inputs have values except for optional inputs.

        Args:
            input_data (Dict[str, InputData]): The input data for the node.

        Returns:
            bool: True if all inputs have values except for optional inputs, False otherwise.
        """
        return all(
            (input.value is not None or input.optional) for input in input_data.values()
        )

    @staticmethod
    def verify_update_values(
        input_data: Dict[str, InputData],
        last_execution: Optional[datetime.datetime],
    ) -> bool:
        """
        Verify if any nodes have been updated except for nodes that have never been executed.

        Args:
            input_data (Dict[str, InputData]): The input data for the node.
            last_execution (Optional[datetime.datetime]): The timestamp of the last execution.

        Returns:
            bool: True if any nodes have been updated except for nodes that have never been executed, False otherwise.
        """
        return any(
            (
                input.updated_at is None
                or last_execution is None
                or input.updated_at > last_execution
            )
            for input in input_data.values()
        )

    async def async_execute_node(
        self, node_id: str, module_callback: Callable[[Dict[str, Any]], Awaitable[None]]
    ) -> None:
        """
        Execute a single node and update its successors.

        Args:
            node_id (str): The ID of the node to execute.
            module_callback (Callable): The callback function to execute the module.

        Raises:
            ValueError: If the node is not found.
        """
        node = self._nodes.get(node_id, None)
        if node is None:
            raise ValueError(f"Node {node_id} not found.")

        # Construct input data
        input_data = {
            input.label: input for input in node.inputs if input.label is not None
        }

        # True if all inputs have values except for optional inputs, False otherwise.
        # Verify validity of inputs
        all_values_are_valid = self.verify_input_values(input_data)

        # Verify if any nodes has been updated except for nodes that have never been executed
        # Verify if any change has occurred in the input data
        any_value_has_been_updated = self.verify_update_values(
            input_data, node.last_execution
        )

        # Verify if it is the initial trigger node
        initial_trigger = (
            node.module_type == ModuleType.TRIGGER and node.last_execution is None
        )  # ! TODO: improve that

        try:
            # Verify if it is not the initial trigger and if all inputs have values except for optional inputs
            # and if all nodes have been updated except for nodes that have never been executed
            # if not, skip the node
            if not initial_trigger and (
                not all_values_are_valid or not any_value_has_been_updated
            ):
                return

            async with self._lock:
                # Launch the node execution in a thread-safe manner and retrieve the output data
                output_data = await node.execute(module_callback)

                # Propagate the output data to the successors
                for successor in self._graph.successors(node_id):
                    self.update_successor_inputs(
                        successor,
                        output_data,
                        self._graph.get_edge_data(node_id, successor).get(
                            "metadata", None
                        ),
                    )
                    # Automatically adding all successors to the execution queue
                    self._execution_queue.put(successor)

        except Exception as e:  # pylint: disable=broad-except
            print(f"{datetime.datetime.now()} - Error executing node {node_id}: {e}")
            self._error_occurred.set()

    async def execute(
        self,
        initial_node: str,
        module_callback: Callable[[Dict[str, Any]], Awaitable[None]],
    ) -> None:
        """
        Execute the graph starting from the initial node.

        Args:
            initial_node (str): The ID of the initial node to start execution from.
            module_callback (Callable): The callback function to execute the module.
        """
        # Start with the initial node
        self._execution_queue.put(initial_node)

        tasks = set()
        max_concurrent_tasks = 10  # Adjust this value as needed

        while not self._execution_queue.empty() or tasks:
            # Check if an error occurred during execution
            if self._error_occurred.is_set():
                break

            # Start new tasks if there's room and nodes in the queue
            while (
                len(tasks) < max_concurrent_tasks and not self._execution_queue.empty()
            ):
                node_id: Union[str, None] = self._execution_queue.get()
                # print(f"{datetime.datetime.now()} - node_id: {node_id}")
                if node_id is not None:
                    task = asyncio.create_task(
                        self.async_execute_node(node_id, module_callback)
                    )
                    tasks.add(task)

            # Wait for at least one task to complete
            if tasks:
                done, tasks = await asyncio.wait(
                    tasks, return_when=asyncio.FIRST_COMPLETED
                )

                for task in done:
                    try:
                        await task
                    except Exception as e:  # pylint: disable=broad-except
                        print(f"{datetime.datetime.now()} - Error executing node: {e}")
                        self._error_occurred.set()
                        break

            # Break the loop if an error occurred
            if self._error_occurred.is_set():
                break

            await asyncio.sleep(0.1)  # Small delay to prevent busy-waiting

        # Cancel any remaining tasks
        for task in tasks:
            task.cancel()

        if self._error_occurred.is_set():
            print(f"{datetime.datetime.now()} - Execution stopped due to an error.")
        else:
            print(f"{datetime.datetime.now()} - Graph execution completed.")
            print(
                f"{datetime.datetime.now()} - Queue empty: {self._execution_queue.empty()}"
            )
            print(
                [f"{node_id}: {self._nodes[node_id].status}" for node_id in self._nodes]
            )

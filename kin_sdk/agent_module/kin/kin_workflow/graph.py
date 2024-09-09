"""
Module for executing a directed graph of nodes.

This module includes the GraphExecutor class, which represents a directed graph
of nodes and provides methods for executing the nodes in parallel and updating
their inputs and outputs.
"""

import datetime
import asyncio
import threading
from typing import Any, Awaitable, Dict, List, Callable, Union
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed

import networkx as nx

from kin_sdk.common.types import ModuleType
from kin_sdk.agent_module.kin.kin_workflow.edge import Edge
from kin_sdk.agent_module.kin.kin_workflow.node import InputData, Node, OutputData


class GraphExecutor:
    """
    Executes a directed graph of nodes.
    TODO: check all @property that I should remove to keep only the one that are really needed.

    Attributes:
        graph (nx.DiGraph): The directed graph.
        nodes (Dict[str, Node]): The nodes in the graph.
        lock (threading.Lock): A lock to ensure thread safety.
        error_occurred (threading.Event): An event to signal if an error occurred.
        execution_queue (Queue): A queue to manage node execution order.
    """

    def __init__(self, graph: Dict[str, Any], setups: Dict[str, Any]):
        self._graph = nx.DiGraph()
        self._nodes = self._init_nodes(graph["nodes"], setups)
        self._init_edges(graph["edges"])
        self._setups = setups

        self._error_occurred = threading.Event()
        self._execution_queue = Queue()
        self._lock = threading.Lock()

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
    def error_occurred(self) -> threading.Event:
        """Get the error occurred event."""
        return self._error_occurred

    @property
    def execution_queue(self) -> Queue:
        """Get the execution queue."""
        return self._execution_queue

    @property
    def lock(self) -> threading.Lock:
        """Get the lock for thread safety."""
        return self._lock

    def _init_nodes(
        self, nodes: List[Dict[str, Any]], setups: Dict[str, Any]
    ) -> Dict[str, Node]:
        """
        Initializes the nodes in the graph.

        Args:
            nodes (List[Dict[str, Any]]): The nodes to initialize.
            setups (Dict[str, Any]): The setups configuration.

        Returns:
            Dict[str, Node]: The initialized nodes.
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
                    module_type=ModuleType.get(node["data"]["type"]),
                    module_id=node["data"]["id"],
                    inputs=node["data"]["targets"],
                    outputs=node["data"]["sources"],
                    setup=formatted_setups.get(f"modules:{node['data']['id']}", {}),
                )
                for node in nodes
            }
        except Exception as e:  # pylint: disable=broad-except
            print(f"Error initializing nodes: {e}")
            return {}

    def _init_edges(self, edges: List[Dict[str, Any]]) -> None:
        """
        Adds edges to the graph.

        Args:
            edges (List[Dict[str, Any]]): The edges to add.
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
            print(f"Error initializing edges: {e}")

    def get_modules_nodes(self, module_type: ModuleType) -> List[str]:
        """
        Returns nodes from a specific type from the graph.

        Args:
            module_type (ModuleType): The type of module to search for.

        Returns:
            List[str]: The IDs of the found nodes.
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
        Updates the inputs/target of a successor node based on the output/source of a predecessor node.

        Args:
            successor_id (str): The ID of the successor node.
            source_data (Dict[str, OutputData]): The output data from the predecessor node.
            edge_data_pred_succ (Union[Edge, None]): The edge data connecting the predecessor node with successor.
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

    def verify_input_values(self, input_data: Dict[str, InputData]) -> bool:
        """
        Verifies if all inputs have values except for optional inputs.

        Args:
            input_data (Dict[str, InputData]): The input data for the node.

        Returns:
            bool: True if all inputs have values except for optional inputs, False otherwise.
        """
        return all(
            (input.value is not None or input.optional) for input in input_data.values()
        )

    def verify_update_values(
        self,
        input_data: Dict[str, InputData],
        last_execution: Union[datetime.datetime, None],
    ) -> bool:
        """
        Verifies if any nodes have been updated except for nodes that have never been executed.

        Args:
            input_data (Dict[str, InputData]): The input data for the node.
            last_execution (Union[datetime.datetime, None]): The timestamp of the last execution.

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
        Executes a single node and updates its successors.

        Args:
            node_id (str): The ID of the node to execute.
            module_callback (Callable): The callback function to execute the module.
        """
        node = self.nodes.get(node_id, None)
        if node is None:
            raise ValueError(f"Node {node_id} not found.")
        print(
            f"\n\n----\n{datetime.datetime.now()} - Executing node {node.module_type}:{node_id}."
        )
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
                print(f"all_values_are_valid: {all_values_are_valid}")
                print(f"any_value_has_been_updated: {any_value_has_been_updated}")
                print(
                    f"{datetime.datetime.now()} - Skipping node {node_id} due to input conditions."
                )
                return

            with self._lock:
                # Launch the node execution in a thread-safe manner and retrieve the output data
                output_data = await node.execute(module_callback)

                # Propagate the output data to the successors
                for successor in self._graph.successors(node_id):
                    print(f"\t-> node_id: {node_id} has successor: {successor}")
                    self.update_successor_inputs(
                        successor,
                        output_data,
                        self._graph.get_edge_data(node_id, successor).get(
                            "metadata", None
                        ),
                    )
                    # Automatically adding all successors to the execution queue
                    self._execution_queue.put(successor)
                    print(f"\t\t- Adding successor {successor} to the execution queue.")

        except Exception as e:  # pylint: disable=broad-except
            print(f"{datetime.datetime.now()} - Error executing node {node_id}: {e}")
            self._error_occurred.set()

    def execute_node(self, *args, **kwargs) -> None:
        """
        Executes a single node.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        asyncio.run(self.async_execute_node(*args, **kwargs))

    def execute(
        self,
        initial_node: str,
        module_callback: Callable[[Dict[str, Any]], Awaitable[None]],
    ) -> None:
        """
        Executes the graph starting from the initial node.

        Args:
            initial_node (str): The ID of the initial node to start execution from.
            module_callback (Callable): The callback function to execute the module.
        """
        # Start with the initial node
        self._execution_queue.put(initial_node)
        print(
            f"{datetime.datetime.now()} - Adding initial node {initial_node} to execution queue."
        )

        # Execute the nodes in parallel using a thread pool
        with ThreadPoolExecutor(max_workers=10) as executor:  # ! TODO thread number
            futures = {}
            # Keep executing nodes until the execution queue is empty and all nodes have completed
            while (
                not (
                    self._execution_queue.empty()
                    and not any(
                        self._nodes[node_id].status == "running"
                        for node_id in self._nodes
                    )
                )
                or futures
            ):  # ! This entire condition seem wrong
                # Check if an error occurred during execution
                if self._error_occurred.is_set():
                    break

                # While the execution queue is not empty, submit nodes for execution
                # Iterate over the node_id execution queue and store them inside futures
                # in order to execute them in parallel
                while not self._execution_queue.empty():
                    # Get the next node to execute
                    node_id: Union[str, None] = self._execution_queue.get()
                    print(
                        f"{datetime.datetime.now()} - Getting node {node_id} from execution queue."
                    )
                    # Submit the node for execution
                    if node_id is not None:
                        future = executor.submit(
                            self.execute_node, node_id, module_callback
                        )
                        futures[future] = node_id
                    print(
                        f"{datetime.datetime.now()} - {node_id}",
                        [f"{nid}: {self._nodes[nid].status}" for nid in self._nodes],
                    )

                # Check completed futures
                for future in as_completed(futures):
                    node_id = futures.pop(future)
                    try:
                        future.result()
                    except Exception as e:  # pylint: disable=broad-except
                        print(
                            f"{datetime.datetime.now()} - Error executing node [{node_id}]: {e}"
                        )
                        self._error_occurred.set()
                        break
                print()

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

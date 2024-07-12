import datetime
import asyncio
import threading
from typing import Any, Dict, List, Literal, Callable
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed

import networkx as nx

from kin_sdk.kin.kin_workflow.node import Node


class GraphExecutor:
    """
    Executes a directed graph of nodes.

    Attributes:
        graph (nx.DiGraph): The directed graph.
        nodes (Dict[str, Node]): The nodes in the graph.
        lock (threading.Lock): A lock to ensure thread safety.
        error_occurred (threading.Event): An event to signal if an error occurred.
        execution_queue (Queue): A queue to manage node execution order.
    """

    def __init__(self, graph: Dict[str, Any], setups: Dict[str, Any]):
        self.graph = nx.DiGraph()
        # format the setups data
        formated_setups = {
            data["service_id"]: data.get("content", {})
            for data in setups.get("data", [])
            if data.get("service_id", None) is not None
        }
        # create the nodes
        self.nodes = {
            node["id"]: Node(
                node_id=node["id"],
                node_type=node["type"],
                service_type=node["data"]["type"],
                service_id=node["data"]["id"],
                inputs=node["data"]["targets"],
                outputs=node["data"]["sources"],
                setup=formated_setups.get(f"services:{node['data']['id']}", {}),
            )
            for node in graph["nodes"]
        }
        self.add_edges(graph["edges"])
        self.error_occurred = threading.Event()
        self.execution_queue = Queue()
        self.lock = threading.Lock()
        self.setups = setups

    def get_services_nodes(
        self, service_type: Literal["trigger", "tool", "kin", "view"]
    ) -> List[str]:
        """
        Returns the trigger nodes in the graph.
        :param service_type: The type of service to search for.

        Returns:
            List[str]: The IDs of the trigger nodes.
        """
        return [
            (node_id, node.service_id)
            for node_id, node in self.nodes.items()
            if node.service_type == service_type
        ]

    def get_node_id_by_service_id(self, service_id: str) -> str:
        """
        Returns the node id by service id.
        :param service_id: The service id to search for.

        Returns:
            str: The ID of the node.
        """
        for node_id, node in self.nodes.items():
            if node.service_id == service_id:
                return node_id
        return ""

    def add_edges(self, edges: List[Dict[str, Any]]) -> None:
        """
        Adds edges to the graph.

        Args:
            edges (List[Dict[str, Any]]): The edges to add.
        """
        for edge in edges:
            source_handle = edge.get("sourceHandle", "").split(":::") + ["", ""]
            target_handle = edge.get("targetHandle", "").split(":::") + ["", ""]

            self.graph.add_edge(
                edge["source"],
                edge["target"],
                source_handle={
                    "type": source_handle[0],
                    "label": source_handle[1],
                },
                target_handle={
                    "type": target_handle[0],
                    "label": target_handle[1],
                },
            )

    def check_for_cycles(self) -> None:
        """
        Checks the graph for cycles and raises an exception if any are found.
        """
        try:
            cycles = list(nx.find_cycle(self.graph, orientation="original"))
            if cycles:
                raise nx.NetworkXUnfeasible("Graph contains a cycle")
        except nx.NetworkXNoCycle:
            pass

    def update_successor_inputs(
        self, successor_id: str, source_data: Dict[str, Any], edge_data: Dict[str, Any]
    ) -> None:
        """
        Updates the inputs of a successor node based on the output of a predecessor node.

        Args:
            successor_id (str): The ID of the successor node.
            source_data (Dict[str, Any]): The output data from the predecessor node.
            edge_data (Dict[str, Any]): The edge data connecting the nodes.
        """
        successor = self.nodes[successor_id]
        source_label = edge_data.get("source_handle", {}).get("label", None)
        target_label = edge_data.get("target_handle", {}).get("label", None)

        if source_label is None or target_label is None:
            return

        for label in source_data:
            if label == source_label:
                for input in successor.inputs:
                    if input["label"] == target_label:
                        input["value"] = source_data[label]
                        input["updated_at"] = datetime.datetime.now()
                break

    async def async_execute_node(
        self, node_id: str, service_callback: Callable
    ) -> None:
        """
        Executes a single node and updates its successors.

        Args:
            node_id (str): The ID of the node to execute.
        """
        node = self.nodes[node_id]
        print(
            f"\n\n----\n{datetime.datetime.now()} - Executing node {node.service_type}:{node_id}."
        )
        # construct input data
        input_data = {
            input["label"]: {
                "value": input.get("value", None),
                "updated_at": input.get("updated_at", None),
                "optional": input.get("optional", False),
            }
            for input in node.inputs
            if "label" in input
        }

        # Verify if all inputs have values except for optional inputs
        verify_values = [
            (values["value"] is not None or values.get("optional", False))
            for values in input_data.values()
        ]
        # Verify if all nodes has been updated except for nodes that have never been executed
        verify_update = [
            values["updated_at"] is None or values["updated_at"] > node.last_execution
            for values in input_data.values()
        ]

        # Verify if it is the initial trigger node
        initial_trigger = (
            node.service_type == "trigger" and node.last_execution is None
        )  # TODO: improve that

        try:
            # Verify if it not the initial_trigger and if all inputs have values except for optional inputs
            # and if all nodes has been updated except for nodes that have never been executed
            # if not, skip the node
            if not initial_trigger and not (all(verify_values) and any(verify_update)):
                print(
                    f"{datetime.datetime.now()} - Skipping node {node_id} due to input conditions."
                )
                return

            with self.lock:
                # Launch the node execution in a thread-safe manner and retrieve the output data
                output_data = await node.execute(input_data, service_callback)

                # Propagate the output data to the successors
                for successor in self.graph.successors(node_id):
                    self.update_successor_inputs(
                        successor,
                        output_data,
                        self.graph.get_edge_data(node_id, successor),
                    )

                    # construct input data for successor
                    successor_input_data = {
                        input["label"]: {
                            "value": input.get("value", None),
                            "updated_at": input.get("updated_at", None),
                            "optional": input.get("optional", False),
                        }
                        for input in self.nodes[successor].inputs
                        if "label" in input
                    }

                    # Verify if all inputs have values except for optional inputs
                    verify_successor_values = [
                        (values["value"] is not None or values.get("optional", False))
                        for values in successor_input_data.values()
                    ]
                    # Verify if all nodes has been updated except for nodes that have never been executed
                    verify_successor_update = [
                        values["updated_at"] is None
                        or values["updated_at"] > node.last_execution
                        for values in successor_input_data.values()
                    ]

                    # Verify if all inputs have values except for optional inputs
                    # and if all nodes has been updated except for nodes that have never been executed
                    # if not, skip the successor else add it to the execution queue
                    if not (
                        all(verify_successor_values) and any(verify_successor_update)
                    ):
                        print(
                            f"{datetime.datetime.now()} - Skipping successor {successor} due to input conditions."
                        )
                        return
                    else:
                        self.execution_queue.put(successor)
                        print(
                            f"{datetime.datetime.now()} - Adding node {successor} to execution queue."
                        )
                # Update the node execution count and timestamp
                self.nodes[node_id].last_execution = datetime.datetime.now()
        except Exception as e:
            print(f"{datetime.datetime.now()} - Error executing node {node_id}: {e}")
            self.error_occurred.set()

    def execute_node(self, *args, **kwargs) -> None:
        asyncio.run(self.async_execute_node(*args, **kwargs))

    def execute(self, initial_node: str, service_callback: Callable) -> None:
        """
        Executes the graph starting from the initial node.

        Args:
            initial_node (str): The ID of the initial node to start execution from.
        """
        # self.check_for_cycles()
        # Start with an initial node
        self.execution_queue.put(initial_node)
        print(
            f"{datetime.datetime.now()} - Adding initial node {initial_node} to execution queue."
        )

        # Execute the nodes in parallel using a thread pool
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {}
            # Keep executing nodes until the execution queue is empty and all nodes have completed and all futures have completed
            while (
                not (
                    self.execution_queue.empty()
                    and not any(
                        self.nodes[node_id].status == "running"
                        for node_id in self.nodes
                    )
                )
                or futures
            ):
                # Check if an error occurred during execution
                if self.error_occurred.is_set():
                    break

                # While the execution queue is not empty, submit nodes for execution
                while not self.execution_queue.empty():
                    # Get the next node to execute
                    node_id = self.execution_queue.get()
                    print(
                        f"{datetime.datetime.now()} - Getting node {node_id} from execution queue."
                    )
                    # Submit the node for execution
                    if node_id is not None:
                        future = executor.submit(
                            self.execute_node, node_id, service_callback
                        )
                        futures[future] = node_id
                    print(
                        f"{datetime.datetime.now()} - {node_id}",
                        [f"{nid}: {self.nodes[nid].status}" for nid in self.nodes],
                    )

                # Check completed futures
                for future in as_completed(futures):
                    node_id = futures.pop(future)
                    try:
                        future.result()
                    except Exception as e:
                        print(
                            f"{datetime.datetime.now()} - Error executing node {node_id}: {e}"
                        )
                        self.error_occurred.set()
                        break
                print()

        if self.error_occurred.is_set():
            print(f"{datetime.datetime.now()} - Execution stopped due to an error.")
        else:
            print(f"{datetime.datetime.now()} - Graph execution completed.")
            print(
                f"{datetime.datetime.now()} - queue empty {self.execution_queue.empty()}"
            )
            print(
                [f"{node_id}: {self.nodes[node_id].status}" for node_id in self.nodes]
            )

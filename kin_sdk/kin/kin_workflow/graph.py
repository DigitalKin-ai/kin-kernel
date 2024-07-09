import datetime
import threading
from typing import Any, Dict, List
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

    def __init__(self, graph: Dict[str, Any]):
        self.graph = nx.DiGraph()
        self.nodes = {
            node["id"]: Node(
                node_id=node["id"],
                node_type=node["type"],
                inputs=node["data"]["targets"],
                outputs=node["data"]["sources"],
            )
            for node in graph["nodes"]
        }
        self.add_edges(graph["edges"])
        self.error_occurred = threading.Event()
        self.execution_queue = Queue()
        self.lock = threading.Lock()

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

    def execute_node(self, node_id: str) -> None:
        """
        Executes a single node and updates its successors.

        Args:
            node_id (str): The ID of the node to execute.
        """
        node = self.nodes[node_id]
        input_data = {
            input["label"]: {
                "value": input.get("value", None),
                "updated_at": input.get("updated_at", None),
                "optional": input.get("optional", False),
            }
            for input in node.inputs
        }
        print(
            f"{datetime.datetime.now()} - Executing node {node_id} with inputs: {input_data}"
        )

        verify_values = [
            (values["value"] is not None or values.get("optional", False))
            for values in input_data.values()
        ]
        verify_update = [
            values["updated_at"] is None or values["updated_at"] > node.last_execution
            for values in input_data.values()
        ]

        try:
            if not (all(verify_values) and any(verify_update)):
                print(
                    f"{datetime.datetime.now()} - Skipping node {node_id} due to input conditions."
                )
                return

            with self.lock:
                output_data = node.execute(input_data)

                for successor in self.graph.successors(node_id):
                    self.update_successor_inputs(
                        successor,
                        output_data,
                        self.graph.get_edge_data(node_id, successor),
                    )

                    successor_input_data = {
                        input["label"]: {
                            "value": input.get("value", None),
                            "updated_at": input.get("updated_at", None),
                            "optional": input.get("optional", False),
                        }
                        for input in self.nodes[successor].inputs
                    }

                    verify_successor_values = [
                        (values["value"] is not None or values.get("optional", False))
                        for values in successor_input_data.values()
                    ]
                    verify_successor_update = [
                        values["updated_at"] is None
                        or values["updated_at"] > node.last_execution
                        for values in successor_input_data.values()
                    ]
                    if not (all(verify_values) and any(verify_update)):
                        print(
                            f"{datetime.datetime.now()} - Skipping successor {successor} due to input conditions."
                        )
                        return

                    if all(verify_successor_values) and any(verify_successor_update):
                        self.execution_queue.put(successor)
                        print(
                            f"{datetime.datetime.now()} - Adding node {successor} to execution queue."
                        )

                self.nodes[node_id].last_execution = datetime.datetime.now()
        except Exception as e:
            print(f"{datetime.datetime.now()} - Error executing node {node_id}: {e}")
            self.error_occurred.set()

    def execute(self, initial_node: str = "n_1") -> None:
        """
        Executes the graph starting from the initial node.

        Args:
            initial_node (str): The ID of the initial node to start execution from.
        """
        self.check_for_cycles()
        self.execution_queue.put(initial_node)
        print(
            f"{datetime.datetime.now()} - Adding initial node {initial_node} to execution queue."
        )

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {}
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
                if self.error_occurred.is_set():
                    break

                while not self.execution_queue.empty():
                    node_id = self.execution_queue.get()
                    print(
                        f"{datetime.datetime.now()} - Getting node {node_id} from execution queue."
                    )
                    if node_id is not None:
                        future = executor.submit(self.execute_node, node_id)
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

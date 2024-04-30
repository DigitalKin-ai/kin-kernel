import networkx as nx
import threading
import pickle
import matplotlib.pyplot as plt
import time
from queue import Queue


class Node:
    def __init__(self, node_id, node_type, inputs, outputs):
        self.node_id = node_id
        self.node_type = node_type
        self.inputs = inputs
        self.outputs = outputs
        self.status = "pending"  # 'pending', 'running', 'completed', 'failed'
        self.current_execution = 0
        self.lock = threading.Lock()

    def execute(self, input_data):
        with self.lock:
            self.status = "running"
            print(f"Executing node {self.node_id} of type {self.node_type}")
            # Simulate execution
            time.sleep(1)  # Simulate some work being done
            output_data = {
                output["label"]: f"output_of_{self.node_id}" for output in self.outputs
            }
            self.status = "completed"
            return output_data


class GraphExecutor:
    def __init__(self, graph):
        self.graph = nx.DiGraph()
        self.nodes = {
            node["id"]: Node(
                node_id=node["id"],
                node_type=node["type"],
                inputs=node["data"]["inputs"],
                outputs=node["data"]["outputs"],
            )
            for node in graph["nodes"]
        }
        self.add_edges(graph["edges"])
        self.node_outputs = {}
        self.lock = threading.Lock()
        self.error_occurred = threading.Event()
        self.execution_queue = Queue()

    def add_edges(self, edges):
        for edge in edges:
            self.graph.add_edge(edge["source"], edge["target"])

    def check_for_cycles(self):
        try:
            cycles = list(nx.find_cycle(self.graph, orientation="original"))
            if cycles:
                raise nx.NetworkXUnfeasible("Graph contains a cycle")
        except nx.NetworkXNoCycle:
            pass

    def execute_node(self, node_id):
        node = self.nodes[node_id]
        input_data = {
            input["label"]: self.node_outputs.get(input["label"], None)
            for input in node.inputs
        }
        try:
            output_data = node.execute(input_data)
            with self.lock:
                self.node_outputs.update(output_data)
                # Add successors to the queue if all their predecessors are completed
                for successor in self.graph.successors(node_id):
                    if all(
                        self.nodes[predecessor].status
                        == "completed"  # TODO, plusieurs predecesors sur meme input
                        for predecessor in self.graph.predecessors(successor)
                    ):
                        self.execution_queue.put(successor)
        except Exception as e:
            print(f"Error executing node {node_id}: {e}")
            self.error_occurred.set()

    def execute(self):
        self.check_for_cycles()

        # Initialize the execution queue with nodes that have no predecessors
        for node_id in nx.topological_sort(self.graph):
            if all(
                self.nodes[predecessor].status == "completed"
                for predecessor in self.graph.predecessors(node_id)
            ):
                self.execution_queue.put(node_id)

        threads = []
        while not self.execution_queue.empty() or any(
            thread.is_alive() for thread in threads
        ):
            if self.error_occurred.is_set():
                break
            if not self.execution_queue.empty():
                node_id = self.execution_queue.get()
                node = self.nodes[node_id]
                if node.status == "pending":
                    thread = threading.Thread(target=self.execute_node, args=(node_id,))
                    threads.append(thread)
                    thread.start()

        for thread in threads:
            thread.join()

        if self.error_occurred.is_set():
            print("Execution stopped due to an error.")
        else:
            print("Graph execution completed.")

    def save_state(self, filename):
        with open(filename, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load_state(filename):
        with open(filename, "rb") as f:
            return pickle.load(f)

    def visualize(self):
        pos = nx.spring_layout(self.graph)
        color_map = {
            "pending": "gray",
            "running": "yellow",
            "completed": "green",
            "failed": "red",
        }
        fig, ax = plt.subplots()
        for node_id, (x, y) in pos.items():
            node = self.nodes[node_id]
            color = color_map[node.status]
            ax.add_patch(
                plt.Rectangle((x - 0.1, y - 0.05), 0.2, 0.1, color=color, ec="black")
            )
            ax.text(
                x,
                y,
                node_id,
                ha="center",
                va="center",
                color="white",
                fontsize=8,
                fontweight="bold",
            )
            # Add inputs and outputs
            input_text = "\n".join([f"IN: {inp['label']}" for inp in node.inputs])
            output_text = "\n".join([f"OUT: {out['label']}" for out in node.outputs])
            ax.text(
                x - 0.15,
                y,
                input_text,
                ha="right",
                va="center",
                color="black",
                fontsize=6,
            )
            ax.text(
                x + 0.15,
                y,
                output_text,
                ha="left",
                va="center",
                color="black",
                fontsize=6,
            )

        nx.draw_networkx_edges(self.graph, pos, ax=ax)
        plt.axis("off")
        plt.show()


# Example usage
graph = {
    "edges": [
        {
            "source": "n_1",
            "sourceHandle": "text:::content",
            "target": "n_2",
            "targetHandle": "text:::FEC",
            "id": "xy-edge__n_1text:::content-n_2text:::FEC",
        },
        {
            "source": "n_2",
            "sourceHandle": "csv:::FEC",
            "target": "n_3",
            "targetHandle": "csv:::file",
            "id": "xy-edge__n_2csv:::FEC-n_3csv:::file",
        },
        {
            "source": "n_2",
            "sourceHandle": "text:::# facture manquante",
            "target": "n_4",
            "targetHandle": "text:::# facture",
            "id": "xy-edge__n_2text:::# facture manquante-n_4text:::# facture",
        },
    ],
    "nodes": [
        {
            "id": "n_1",
            "type": "wfbox",
            "data": {
                "id": "1",
                "name": "gmail",
                "type": "trigger",
                "color": "#686",
                "outputs": [
                    {"label": "smtp", "type": "url"},
                    {"label": "email", "type": "email"},
                    {"label": "password", "type": "text"},
                ],
                "inputs": [
                    {"label": "from", "type": "email"},
                    {"label": "content", "type": "text"},
                ],
            },
        },
        {
            "id": "n_2",
            "type": "wfbox",
            "data": {
                "id": "1",
                "name": "comptable",
                "type": "kin",
                "outputs": [
                    {"label": "FEC", "type": "text"},
                    {"label": "facture", "type": "text"},
                ],
                "inputs": [
                    {"label": "FEC", "type": "csv"},
                    {"label": "# facture manquante", "type": "text"},
                ],
            },
        },
        {
            "id": "n_3",
            "type": "wfbox",
            "data": {
                "id": "1",
                "name": "csv",
                "type": "view",
                "outputs": [{"label": "file", "type": "csv"}],
                "inputs": [],
            },
        },
        {
            "id": "n_4",
            "type": "wfbox",
            "data": {
                "id": "1",
                "name": "relance",
                "type": "kin",
                "outputs": [{"label": "# facture", "type": "text"}],
                "inputs": [{"label": "facture", "type": "text"}],
            },
        },
    ],
}

executor = GraphExecutor(graph)
executor.execute()
executor.visualize()
executor.save_state("graph_state.pkl")

# To load the state and continue execution
# executor = GraphExecutor.load_state('graph_state.pkl')
# executor.execute()
# executor.visualize()

import networkx as nx
import threading
import pickle
import matplotlib.pyplot as plt
import time
import datetime
from queue import Queue


# https://mermaid.live/edit#pako:eNqFVEty2kAQvUqXNtqYC7BIygZsbGNIlb2KyGKiaWBcUo88H1dStu-SLefgYukZGlASl8OK15_Xn9ejl6K2GothsXaq28DDeEnAv_Pq_NHGgA6a0mjQETqHrWFMFqOG3S9oFKxMg6BL_IF1DMbSt33yRfXFRgf1Rj1FlARmyBWGyUzrRIwc44MK0Se6skPShtYlYGCfByUNfFhqVD0oCpDqvBMEVKIP0CkPz0ZjYn6KpWnAsZkjuUrujos9Yw2RDv1os1rttg6ZmtPK2rZdgwF1KWXH1cS51L_ebQPWYbdF-Cy-SXUfbNehE3xZjSwFQ_FouapmCrq_e-WWBtiwMbd6YJtW4902xbrUPYtA2uH7okjGdTUrkTy231MBBM9TGupi8FCnRpAozRWJK6ksAiaUtyFxCnis3RZak6V5TGoeGrqpRkcBj-uKojISlC4SJR0l_raa5BH3Cf1GZz0mDyx2rn3gkqC7_5X7R5v56XSZ1se6Ru95zF7ehye1-EMveQ4wGHyCCznvDEZygBnIqxkn8LqI5hUmfcvc0itcyjnkhCu5hJN72rdkCqkwzQnXIu7JfdO3ZIqFKJQTbmX9Gcxk4xncyWYzmMvS-jMt9qA4K1p0rTKaPw8vybUswgZbXBZD_qtxpWITlsWS3jhUxWDvf1JdDIOLeFbETquAY6P42bcHo7NxvSmGK9V4Rp2ir9a2gt9-A4TCe7o


class Node:
    def __init__(self, node_id, node_type, inputs, outputs):
        self.node_id = node_id
        self.node_type = node_type
        self.inputs = inputs
        self.outputs = outputs
        self.status = "pending"  # 'pending', 'running', 'completed', 'failed'
        self.current_execution = 0
        self.last_execution = datetime.datetime.now()
        self.lock = threading.Lock()

    def execute(self, input_data):
        with self.lock:
            self.status = "running"
            print(f"Executing node {self.node_id} of type {self.node_type}")
            # Simulate execution
            time.sleep(1)  # Simulate some work being done
            output_data = {
                output["label"]: f"output_of_{output['label']}_{self.node_id}"
                for output in self.outputs
            }
            self.outputs = [
                {
                    **output,
                    "value": f"output_of_{output['label']}_{self.node_id}",
                    "updated_at": datetime.datetime.now(),
                }
                for output in self.outputs
            ]
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
        self.lock = threading.Lock()
        self.error_occurred = threading.Event()
        self.execution_queue = Queue()

    def add_edges(self, edges):
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

    def check_for_cycles(self):
        try:
            cycles = list(nx.find_cycle(self.graph, orientation="original"))
            if cycles:
                raise nx.NetworkXUnfeasible("Graph contains a cycle")
        except nx.NetworkXNoCycle:
            pass

    def update_successor_inputs(self, successor_id, source_data, edge_data):
        successor = self.nodes[successor_id]
        # {
        #     "source_handle": {"type": "text", "label": "content"},
        #     "target_handle": {"type": "text", "label": "FEC"},
        # }
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

    def execute_node(self, node_id):
        node = self.nodes[node_id]
        input_data = {
            input["label"]: {
                "value": input.get("value", None),
                "updated_at": input.get("updated_at", None),
                "optional": input.get("optional", False),
            }
            for input in node.inputs
        }
        print(f"Executing node {node_id} with inputs: {input_data}")

        # check if all inputs have a value and at least one input has been updated
        verify_values = [
            (values["value"] is not None or values.get("optional", False))
            for values in input_data.values()
        ]
        verify_update = [
            values["updated_at"] is None or values["updated_at"] > node.last_execution
            for values in input_data.values()
        ]

        try:
            # si tous les inputs ont une valeur et au moins un input a été mis à jour
            # alors on execute le noeud sinon on passe
            if not (all(verify_values) and any(verify_update)):
                return

            with self.lock:
                output_data = node.execute(input_data)

                # Add successors to the queue if all their predecessors are completed
                for successor in self.graph.successors(node_id):

                    # Update the inputs of the successor node
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

                    # check if all inputs have a value and at least one input has been updated
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
                        return

                    if all(verify_successor_values) and any(verify_successor_update):
                        self.execution_queue.put(successor)

                self.nodes[node_id].last_execution = datetime.datetime.now()
        except Exception as e:
            print(f"Error executing node {node_id}: {e}")
            self.error_occurred.set()

    def execute(self, initial_node="n_1"):
        self.check_for_cycles()
        self.execution_queue.put(initial_node)

        threads = []
        while not self.execution_queue.empty() or any(
            thread.is_alive() for thread in threads
        ):
            if self.error_occurred.is_set():
                break

            if not self.execution_queue.empty():
                node_id = self.execution_queue.get()
                if node_id is not None:
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
                "inputs": [
                    {
                        "label": "smtp",
                        "type": "url",
                        "value": "google.com",
                        "updated_at": datetime.datetime.now(),
                    },
                    {
                        "label": "email",
                        "type": "email",
                        "value": "test@gmail.com",
                    },
                    {
                        "label": "password",
                        "type": "text",
                        "value": "1234",
                        "updated_at": datetime.datetime.now(),
                    },
                ],
                "outputs": [
                    {
                        "label": "from",
                        "type": "email",
                    },
                    {
                        "label": "content",
                        "type": "text",
                    },
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
                "inputs": [
                    {"label": "FEC", "type": "text"},
                    {"label": "facture", "type": "text", "optional": True},
                ],
                "outputs": [
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
                "inputs": [{"label": "file", "type": "csv"}],
                "outputs": [],
            },
        },
        {
            "id": "n_4",
            "type": "wfbox",
            "data": {
                "id": "1",
                "name": "relance",
                "type": "kin",
                "inputs": [{"label": "# facture", "type": "text"}],
                "outputs": [{"label": "facture", "type": "text"}],
            },
        },
    ],
}

executor = GraphExecutor(graph)
executor.execute()
# executor.visualize()
# executor.save_state("graph_state.pkl")

# To load the state and continue execution
# executor = GraphExecutor.load_state('graph_state.pkl')
# executor.execute()
# executor.visualize()

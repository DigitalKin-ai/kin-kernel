"""
TODO: sphinx docstring
"""

# import json
from kin_sdk.agent_module import KinWorkflow
from kin_sdk.grpc_system.module_server import ModuleServer


# method to load json file from /examples/data/setup_example.json
# def load_json_file() -> Union[dict | None]:
#     try:
#         with open("examples/data/setup_example.json", "r") as file:
#             return json.load(file)
#     except FileNotFoundError:
#         print("File not found")
#         return None


# def callback(output: WorkflowOutput):
#     """TODO sphinx docstring"""
#     print("callback: ", output)


def main():
    """TODO sphinx docstring"""

    # test = dict(tuple=(1, 2))
    # test2 = dict(array=[1, 2])
    # test3 = {"tuple": (1, 2)}
    # test4 = {"array": [1, 2]}

    # print(test)
    # print(test2)
    # print(test3)
    # print(test4)

    kin_server = ModuleServer(
        module_class=KinWorkflow,
        module_id="fibonacci",
        module_address="localhost",
        module_port=50050,
        registry_address="localhost:50051",
        database_address="localhost:50040",
    )
    kin_server.asyncio_serve()

    # input_data = WorkflowInput(trigger_id="fibonacci_trigger")
    # setup_id = "setups:fibonacci_setup"

    # kin_workflow.execute(input_data, setup_id, callback)


if __name__ == "__main__":
    main()
    print("Hello, World!")

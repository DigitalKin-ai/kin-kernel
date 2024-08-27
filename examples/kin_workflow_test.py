"""
TODO: sphinx docstring
"""

# import json
# from typing import Union
import time
from kin_sdk.agent_module import KinWorkflow
from kin_sdk.agent_module.kin.kin_workflow.kin import WorkflowInput, WorkflowOutput


# method to load json file from /examples/data/setup_example.json
# def load_json_file() -> Union[dict | None]:
#     try:
#         with open("examples/data/setup_example.json", "r") as file:
#             return json.load(file)
#     except FileNotFoundError:
#         print("File not found")
#         return None


def callback(output: WorkflowOutput):
    """TODO sphinx docstring"""
    print("callback: ", output)


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

    # assert "a" == "b", "a is not equal to b"
    kin_workflow = KinWorkflow(
        name="First Kin Workflow",
        description="This is the first Kin workflow.",
        module_id="first kin workflow",
        module_address="localhost",
        module_port=50050,
        registry_address="localhost:50051",
    )
    kin_workflow.start(kin_id="fibonacci")
    time.sleep(5)
    input_data = WorkflowInput(trigger_id="fibonacci_trigger")
    setup_id = "setups:fibonacci_setup"

    kin_workflow.execute(input_data, setup_id, callback)


if __name__ == "__main__":
    main()
    print("Hello, World!")

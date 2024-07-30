"""
TODO: sphinx docstring
"""

# import json
# from typing import Union
import time
from kin_sdk.kin.kin_workflow import KinWorkflow
from kin_sdk.kin.kin_workflow.kin import WorkflowInput, WorkflowSetup, WorkflowOutput


# method to load json file from /examples/data/setup_example.json
# def load_json_file() -> Union[dict | None]:
#     try:
#         with open("examples/data/setup_example.json", "r") as file:
#             return json.load(file)
#     except FileNotFoundError:
#         print("File not found")
#         return None


def callback(output: WorkflowOutput):
    print("callback: ", output)


def main():
    kin_workflow = KinWorkflow(
        name="First Kin Workflow",
        description="This is the first Kin workflow.",
        service_id="first kin workflow",
        service_address="localhost",
        service_port=50050,
        registry_address="localhost:50051",
    )
    kin_workflow.start(kin_id="test")
    time.sleep(5)
    input_data = WorkflowInput(trigger_id="fibonacci_trigger")
    setup_data = WorkflowSetup()

    kin_workflow.execute(input_data, setup_data, callback)


if __name__ == "__main__":
    main()
    print("Hello, World!")

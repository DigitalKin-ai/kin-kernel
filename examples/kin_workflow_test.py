"""
TODO: sphinx docstring
"""

# import json
# from typing import Union
from kin_sdk.kin.kin_workflow import KinWorkflow


# method to load json file from /examples/data/setup_example.json
# def load_json_file() -> Union[dict | None]:
#     try:
#         with open("examples/data/setup_example.json", "r") as file:
#             return json.load(file)
#     except FileNotFoundError:
#         print("File not found")
#         return None


if __name__ == "__main__":
    kin_workflow = KinWorkflow(
        name="First Kin Workflow",
        description="This is the first Kin workflow.",
        service_id="first kin workflow",
        service_address="localhost",
        service_port=50050,
        registry_address="localhost:50051",
    )
    kin_workflow.start()
    print("Hello, World!")

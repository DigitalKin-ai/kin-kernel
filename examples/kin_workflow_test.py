"""
TODO: sphinx docstring
"""

# import json
from kin_sdk.agent_module import KinWorkflow
from kin_sdk.grpc_system.module_server import ModuleServer


def main():
    """TODO sphinx docstring"""

    kin_server = ModuleServer(
        module_class=KinWorkflow,
        module_id="fibonacci",
        module_address="localhost",
        module_port=50050,
        registry_address="localhost:50051",
        database_address="localhost:50040",
    )
    kin_server.asyncio_serve()


if __name__ == "__main__":
    main()
    print("Hello, World!")

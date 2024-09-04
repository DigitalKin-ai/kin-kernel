"""
This example demonstrates how to start a ModuleRegistry server.
"""

from kin_sdk.grpc_system import ModuleRegistryServer


def main():
    """
    Starts the ModuleRegistry server.
    """
    server = ModuleRegistryServer(50051)
    server.asyncio_serve()


if __name__ == "__main__":
    main()

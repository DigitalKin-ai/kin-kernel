"""
This example demonstrates how to start a ModuleRegistry server.
"""

import asyncio

from kin_sdk.grpc_system import ModuleRegistryServer


async def main():
    """
    Starts the ModuleRegistry server.
    """
    server = ModuleRegistryServer(50051)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())

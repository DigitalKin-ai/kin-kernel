"""
TODO: Add a description of the module
"""

import asyncio
import signal

from examples.fibonacci.addition_tool import AdditionTool
from examples.fibonacci.fibonacci_trigger import CronTrigger
from examples.fibonacci.sequence_tool import SequenceTool
from examples.fibonacci.display_tool import DisplayTool
from kin_sdk.grpc_system import GRPCServerBase, ModuleRegistryServer
from kin_sdk.grpc_system.module_server import ModuleServer


class ServerManager:
    """
    A class to manage multiple servers.
    """

    def __init__(self):
        self.servers = []
        self._stop_event = asyncio.Event()

    def add_server(self, module: GRPCServerBase, *args, **kwargs) -> None:
        """
        Add a server to the manager.
        """
        server = module(*args, **kwargs)
        self.servers.append(server)
        if "module_class" in kwargs:
            print(
                f"Added server: {server.__class__.__name__} with module class: {kwargs['module_class'].__name__}"
            )
        else:
            print(f"Added server: {server.__class__.__name__}")

    async def _run_server(self, server: GRPCServerBase) -> None:
        """
        Run a server asynchronously.
        """
        await server.serve()

    async def start_all(self) -> None:
        """
        Start all servers asynchronously.
        """
        print("\nStarting all servers...")
        tasks = [self._run_server(server) for server in self.servers]
        await asyncio.gather(*tasks)
        print("All servers started successfully.")

    async def stop_all(self) -> None:
        """
        Stop all servers asynchronously.
        """
        self._stop_event.set()
        module_registry_server = None
        other_module_servers = []

        # Separate the ModuleRegistryServer from other servers
        for server in self.servers:
            if isinstance(server, ModuleRegistryServer):
                module_registry_server = server
            else:
                other_module_servers.append(server)

        # Stop other servers first
        stop_tasks = [server.stop() for server in other_module_servers]
        await asyncio.gather(*stop_tasks)
        # Stop the ModuleRegistryServer last
        if module_registry_server:
            print("-" * 50)
            print("-" * 50)
            print("-" * 50)
            await module_registry_server.stop()

        print("All servers stopped.")


async def main():
    """
    Main function to start and manage servers.
    """
    manager = ServerManager()

    # Start the moduleRegistryServer module registry
    manager.add_server(ModuleRegistryServer, 50051)

    # Start the AdditionTool module
    manager.add_server(
        ModuleServer,
        module_class=AdditionTool,
        module_id="addition_tool",
        module_address="localhost",
        module_port=50052,
        registry_address="localhost:50051",
    )
    # Start the SequenceTool module
    manager.add_server(
        ModuleServer,
        module_class=SequenceTool,
        module_id="sequence_tool",
        module_address="localhost",
        module_port=50053,
        registry_address="localhost:50051",
    )
    # Start the DisplayTool module
    manager.add_server(
        ModuleServer,
        module_class=DisplayTool,
        module_id="display_tool",
        module_address="localhost",
        module_port=50054,
        registry_address="localhost:50051",
    )
    # Start the CronTrigger module
    manager.add_server(
        ModuleServer,
        module_class=CronTrigger,
        module_id="fibonacci_trigger",
        module_address="localhost",
        module_port=50055,
        registry_address="localhost:50051",
    )

    loop = asyncio.get_running_loop()

    def signal_handler():
        print("Signal received, stopping all servers...")
        asyncio.create_task(manager.stop_all())

    loop.add_signal_handler(signal.SIGINT, signal_handler)
    loop.add_signal_handler(signal.SIGTERM, signal_handler)

    await manager.start_all()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("KeyboardInterrupt received, stopping all servers...")

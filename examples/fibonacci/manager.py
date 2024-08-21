import threading
import signal
import sys

from examples.fibonacci.addition_tool import AdditionTool
from examples.fibonacci.fibonacci_trigger import CronTrigger
from examples.fibonacci.sequence_tool import SequenceTool
from examples.fibonacci.display_tool import DisplayTool
from kin_sdk.grpc_system import GRPCServerBase, ModuleRegistryServer


class ServerManager:
    def __init__(self):
        self.servers = []
        self.threads = []
        self._stop_event = threading.Event()

    def add_server(self, module: GRPCServerBase, *args, **kwargs) -> None:
        server = module(*args, **kwargs)
        self.servers.append(server)

    def _run_server(self, server: GRPCServerBase) -> None:
        server.serve()

    def start_all(self) -> None:
        for server in self.servers:
            thread = threading.Thread(target=self._run_server, args=(server,))
            thread.start()
            self.threads.append(thread)
        print("All servers started.")

    def stop_all(self) -> None:
        self._stop_event.set()
        module_registry_server = []
        other_module_server = []

        # Stop the ModuleRegistryServer first
        for server in self.servers:
            if server.__class__.__name__ == "ModuleRegistryServer":
                module_registry_server.append(server)
            else:
                other_module_server.append(server)

        for server in other_module_server:
            server.serve_stop()

        for server in module_registry_server:
            server.serve_stop()

        for thread in self.threads:
            thread.join()

        print("All servers stopped.")


def signal_handler(sig, frame) -> None:
    print("Signal received, stopping all servers...")
    manager.stop_all()
    sys.exit(0)


if __name__ == "__main__":
    manager = ServerManager()

    # Start the moduleRegistryServer module registry
    manager.add_server(ModuleRegistryServer, 50051)

    # Start the AdditionTool module
    manager.add_server(
        AdditionTool,
        module_id="addition_tool",
        module_address="localhost",
        module_port=50052,
        registry_address="localhost:50051",
    )
    # Start the SequenceTool module
    manager.add_server(
        SequenceTool,
        module_id="sequence_tool",
        module_address="localhost",
        module_port=50053,
        registry_address="localhost:50051",
    )
    # Start the DisplayTool module
    manager.add_server(
        DisplayTool,
        module_id="display_tool",
        module_address="localhost",
        module_port=50054,
        registry_address="localhost:50051",
    )
    # Start the CronTrigger module
    manager.add_server(
        CronTrigger,
        module_id="fibonacci_trigger",
        module_address="localhost",
        module_port=50055,
        registry_address="localhost:50051",
    )

    signal.signal(signal.SIGINT, signal_handler)
    manager.start_all()
    signal.pause()  # Wait for signal

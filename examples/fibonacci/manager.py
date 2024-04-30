import threading
import signal
import sys

from examples.fibonacci.addition_tool import AdditionTool
from examples.fibonacci.fibonacci_trigger import CronTrigger
from examples.fibonacci.sequence_tool import SequenceTool
from examples.fibonacci.display_tool import DisplayTool
from kin_sdk.grpc_services import GRPCServerBase, ServiceRegistryServer


class ServerManager:
    def __init__(self):
        self.servers = []
        self.threads = []
        self._stop_event = threading.Event()

    def add_server(self, service: GRPCServerBase, *args, **kwargs) -> None:
        server = service(*args, **kwargs)
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
        service_registry_server = []
        other_service_server = []

        # Stop the ServiceRegistryServer first
        for server in self.servers:
            if server.__class__.__name__ == "ServiceRegistryServer":
                service_registry_server.append(server)
            else:
                other_service_server.append(server)

        for server in other_service_server:
            server.serve_stop()

        for server in service_registry_server:
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

    # Start the ServiceRegistryServer service registry
    manager.add_server(ServiceRegistryServer, 50051)

    # Start the AdditionTool service
    manager.add_server(
        AdditionTool,
        service_id="addition_tool",
        service_address="localhost",
        service_port=50052,
        registry_address="localhost:50051",
    )
    # Start the SequenceTool service
    manager.add_server(
        SequenceTool,
        service_id="sequence_tool",
        service_address="localhost",
        service_port=50053,
        registry_address="localhost:50051",
    )
    # Start the DisplayTool service
    manager.add_server(
        DisplayTool,
        service_id="display_tool",
        service_address="localhost",
        service_port=50054,
        registry_address="localhost:50051",
    )
    # Start the CronTrigger service
    manager.add_server(
        CronTrigger,
        service_id="fibonacci_trigger",
        service_address="localhost",
        service_port=50055,
        registry_address="localhost:50051",
    )

    signal.signal(signal.SIGINT, signal_handler)
    manager.start_all()
    signal.pause()  # Wait for signal

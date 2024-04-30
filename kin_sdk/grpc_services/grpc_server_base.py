from concurrent import futures
from typing import Any
import grpc

from kin_sdk.common.logger import logger


class GRPCServerBase:
    """
    Base class for creating a gRPC server.

    Attributes:
        servicer (Any): The gRPC servicer instance that handles the service's RPCs.
        port (str): The port number on which the server should listen.
        max_workers (int): Maximum number of worker threads for the server.

    Methods:
        serve(): Starts the server and waits for termination.
        add_to_server(server): Abstract method to add the servicer to the server.
    """

    def __init__(self, servicer: Any, port: str, max_workers: int = 10) -> None:
        """
        Initializes the GRPCServerBase instance.

        Args:
            servicer (Any): An instance of a gRPC servicer.
            port (str): The port number to bind the server to.
            max_workers (int): The maximum number of worker threads.
        """
        self.servicer = servicer
        self.port = port
        self.max_workers = max_workers

    def serve(self) -> None:
        """
        Starts the server, binds it to the specified port, and waits for termination.

        The server runs indefinitely until an external interruption or termination.
        """
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.max_workers))
        self.servicer.add_to_server(server)
        server.add_insecure_port(f"[::]:{self.port}")
        logger.info("Server starting on port %s...", self.port)
        server.start()
        server.wait_for_termination()

    @classmethod
    def add_to_server(cls, server: grpc.Server) -> None:
        """
        Abstract method to add the servicer to the server. Must be implemented by subclasses.

        Args:
            server (grpc.Server): The gRPC server instance to which the servicer will be added.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Must be implemented by subclass.")

"""TODO: Add a description here"""

import asyncio
import signal
from concurrent import futures
from typing import NoReturn
import grpc
from grpc.aio._server import Server

from kin_sdk.common.logger import logger
from kin_sdk.certificates import get_certificates, CertValues


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

    def __init__(
        self,
        port: int,
        max_workers: int = 10,
    ) -> None:
        """
        Initializes the GRPCServerBase instance.

        Args:
            servicer_class (Type): The class of the gRPC servicer.
            port (str): The port number to bind the server to.
            servicer_args (tuple): Arguments for the servicer's constructor.
            servicer_kwargs (dict): Keyword arguments for the servicer's constructor.
            max_workers (int): The maximum number of worker threads.
        """
        self.port = port
        self.max_workers = max_workers
        self._server: Server = None

        self._certificates, self._use_ssl = get_certificates()

    def _init_credentials(self) -> grpc.ServerCredentials:
        """
        Initializes the gRPC server credentials.
        """
        server_cert: CertValues = self._certificates.server_cert

        return grpc.ssl_server_credentials(
            private_key_certificate_chain_pairs=[
                (
                    server_cert.private_key,
                    server_cert.certificate_chain,
                )
            ],
            root_certificates=server_cert.root_certificates,
            require_client_auth=False,
        )

    def _init_server(self) -> grpc.aio.Server:
        """
        Initializes the gRPC server instance, configures it with the specified port and credentials, and returns it.

        Returns:
            grpc.aio.Server: The gRPC server instance.
        """
        server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=self.max_workers)
        )
        if self._use_ssl:
            server_credentials = self._init_credentials()
            server.add_secure_port(f"[::]:{self.port}", server_credentials)
            logger.info("🔒 Starting secure gRPC server on port %s", self.port)
        else:
            server.add_insecure_port(f"[::]:{self.port}")
            logger.info("🔓 Starting insecure gRPC server on port %s", self.port)
        return server

    async def serve(self) -> None:
        """
        Starts the server, binds it to the specified port, and waits for termination.

        The server runs indefinitely until an external interruption or termination.
        """
        self._server = self._init_server()
        self.add_to_server(self._server)
        logger.info("🤖 Module starting on port %s", self.port)
        await self._server.start()
        await self._server.wait_for_termination()

    async def stop(self, grace: int = 0) -> None:
        """
        Stops the server.
        """
        logger.info("🛑 Stopping module on from %s", self.port)
        await self._server.stop(grace)

    def asyncio_serve(self) -> NoReturn:
        """
        Synchronous method to start the server and handle graceful shutdown.

        This method sets up signal handlers for graceful shutdown and runs
        the server in an asyncio event loop.

        Raises:
            KeyboardInterrupt: If the server is stopped by a keyboard interrupt.
        """

        async def main() -> None:
            """
            Main coroutine to run the server and handle shutdown.
            """
            loop = asyncio.get_running_loop()

            # Set up signal handlers
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(
                    sig, lambda s=sig: asyncio.create_task(shutdown(s))
                )

            try:
                await self.serve()
            except asyncio.CancelledError:
                pass

        async def shutdown(sig: signal.Signals) -> None:
            """
            Coroutine to handle graceful shutdown of the server.

            Args:
                sig (signal.Signals): The signal that triggered the shutdown.
            """
            logger.info("Received exit signal %s", sig.name)
            logger.info("Shutting down server")
            await self.stop()
            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            loop = asyncio.get_running_loop()
            loop.stop()

        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            pass

    def add_to_server(self, server: grpc.aio.Server) -> None:
        """
        Abstract method to add the servicer to the server. Must be implemented by subclasses.

        Args:
            server (grpc.aio.Server): The gRPC server instance to which the servicer will be added.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Must be implemented by subclass.")

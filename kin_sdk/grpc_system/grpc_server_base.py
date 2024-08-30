"""TODO: Add a description here"""

from concurrent import futures
import grpc
from grpc.aio._server import Server

from kin_sdk.common import logger, get_certificates, Certificates, CertValues


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
        servicer_class: "GRPCServerBase",
        port: int,
        servicer_args: tuple = (),
        servicer_kwargs: dict = None,
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
        self.servicer_class = servicer_class
        self.servicer_args = servicer_args
        self.servicer_kwargs = servicer_kwargs if servicer_kwargs else {}
        self.port = port
        self.max_workers = max_workers
        self._server: Server = None
        self._credentials = grpc.ssl_channel_credentials(
            root_certificates=None,  # Use None to use the default root certificates
            private_key=None,  # Use None if client authentication is not required
            certificate_chain=None,  # Use None if client authentication is not required
        )

    def _init_credentials(self) -> grpc.ServerCredentials:
        """
        Initializes the gRPC server credentials.
        """
        certificates: Certificates = get_certificates()
        server_cert: CertValues = certificates.server_cert

        return grpc.ssl_server_credentials(
            private_key_certificate_chain_pairs=[
                (
                    server_cert.private_key,
                    server_cert.certificate_chain,
                )
            ],
            root_certificates=server_cert.root_certificates,
            require_client_auth=True,
        )

    async def serve(self) -> None:
        """
        Starts the server, binds it to the specified port, and waits for termination.

        The server runs indefinitely until an external interruption or termination.
        """
        self._server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=self.max_workers)
        )
        servicer: GRPCServerBase = self.servicer_class(
            *self.servicer_args, **self.servicer_kwargs
        )
        servicer.add_to_server(self._server)
        self._server.add_secure_port(
            address=f"[::]:{self.port}", server_credentials=self._init_credentials()
        )
        logger.info("🤖 Service starting on port %s", self.port)
        await self._server.start()
        await self._server.wait_for_termination()

    async def serve_stop(self, grace: int = 0) -> None:
        """
        Stops the server.
        """
        logger.info("🛑 Stopping service on port %s", self.port)
        await self._server.stop(grace)

    def add_to_server(self, server: grpc.aio.Server) -> None:
        """
        Abstract method to add the servicer to the server. Must be implemented by subclasses.

        Args:
            server (grpc.aio.Server): The gRPC server instance to which the servicer will be added.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Must be implemented by subclass.")

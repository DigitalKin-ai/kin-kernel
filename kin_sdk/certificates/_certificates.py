"""
Gestion des certificats pour le SDK
"""

import os
from typing import Annotated, Optional, Tuple, Union

import grpc
from pydantic import BaseModel, Field

from kin_sdk.common.logger import logger


class CertValues(BaseModel):
    """
    Client certificate for the SDK
    """

    root_certificates: Annotated[
        Optional[bytes], Field(None, description="Root certificates (CA)")
    ]
    certificate_chain: Annotated[
        Optional[bytes], Field(None, description="Certificate chain (cert)")
    ]
    private_key: Annotated[
        Optional[bytes], Field(None, description="Private key (key)")
    ]


class Certificates(BaseModel):
    """
    Certificates for the SDK
    """

    client_cert: Annotated[CertValues, Field(..., description="Client certificate")]
    server_cert: Annotated[CertValues, Field(..., description="Server certificate")]


def get_certificates() -> Tuple[Certificates, bool]:
    """
    Get certificates for the SDK
    """
    ca_pem = os.getenv("CA_PEM", None)
    server_cert_pem = os.getenv("SERVER_CERT_PEM", None)
    server_key_pem = os.getenv("SERVER_KEY_PEM", None)
    client_cert_pem = os.getenv("CLIENT_CERT_PEM", None)
    client_key_pem = os.getenv("CLIENT_KEY_PEM", None)

    # Check if the certificates are set
    if (
        ca_pem is None
        or server_cert_pem is None
        or server_key_pem is None
        or client_key_pem is None
        or client_key_pem is None
    ):
        return Certificates(
            client_cert=CertValues(
                root_certificates=None,
                certificate_chain=None,
                private_key=None,
            ),
            server_cert=CertValues(
                root_certificates=None,
                certificate_chain=None,
                private_key=None,
            ),
        )

    # Read the certificates
    try:
        with open(ca_pem, "rb") as f:
            root_certificates = f.read()
    except FileNotFoundError:
        root_certificates = None
        logger.error("Root certificates file not found")

    # Server certificates
    try:
        with open(server_cert_pem, "rb") as f:
            server_certificate_chain = f.read()
    except FileNotFoundError:
        server_certificate_chain = None
        logger.error("Certificate chain file not found")
    try:
        with open(server_key_pem, "rb") as f:
            server_private_key = f.read()
    except FileNotFoundError:
        server_private_key = None
        logger.error("Private key file not found")

    # Client certificates
    try:
        with open(client_cert_pem, "rb") as f:
            client_certificate_chain = f.read()
    except FileNotFoundError:
        client_certificate_chain = None
        logger.error("Certificate chain file not found")
    try:
        with open(client_key_pem, "rb") as f:
            client_private_key = f.read()
    except FileNotFoundError:
        client_private_key = None
        logger.error("Private key file not found")

    all_certs_present = all(
        [
            root_certificates,
            server_certificate_chain,
            server_private_key,
            client_certificate_chain,
            client_private_key,
        ]
    )
    return (
        Certificates(
            server_cert=CertValues(
                root_certificates=root_certificates,
                certificate_chain=server_certificate_chain,
                private_key=server_private_key,
            ),
            client_cert=CertValues(
                root_certificates=root_certificates,
                certificate_chain=client_certificate_chain,
                private_key=client_private_key,
            ),
        ),
        all_certs_present,
    )


def init_server_credentials() -> Union[grpc.ChannelCredentials, None]:
    """
    Initializes the gRPC server credentials.

    Returns:
        grpc.ChannelCredentials: The gRPC channel credentials or None if SSL is not used.
    """
    certificates, use_ssl = get_certificates()
    server_cert: CertValues = certificates.server_cert

    return (
        grpc.ssl_channel_credentials(
            root_certificates=server_cert.root_certificates,
            private_key=server_cert.private_key,
            certificate_chain=server_cert.certificate_chain,
        )
        if use_ssl
        else None
    )


def init_channel_credentials() -> Union[grpc.ChannelCredentials, None]:
    """
    Initializes the gRPC channel credentials.

    Returns:
        grpc.ChannelCredentials: The gRPC channel credentials or None if SSL is not used.
    """
    certificates, use_ssl = get_certificates()
    client_cert: CertValues = certificates.client_cert

    return (
        grpc.ssl_channel_credentials(
            root_certificates=client_cert.root_certificates,
            private_key=client_cert.private_key,
            certificate_chain=client_cert.certificate_chain,
        )
        if use_ssl
        else None
    )


def grpc_channel(target: str) -> grpc.aio.Channel:
    """
    Creates a secure gRPC channel to the Module Registry.
    """
    credentials = init_channel_credentials()

    return (
        grpc.aio.insecure_channel(target=target)
        if credentials is None
        else grpc.aio.secure_channel(target=target, credentials=credentials)
    )

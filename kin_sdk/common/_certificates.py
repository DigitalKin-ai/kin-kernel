"""
Gestion des certificats pour le SDK
"""

import os
from typing import Annotated, Optional

from pydantic import BaseModel, Field

from kin_sdk.common import logger


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


def get_certificates() -> Certificates:
    """
    Get certificates for the SDK
    """
    ca_pem = os.getenv("CA_PEM", None)
    cert_pem = os.getenv("CERT_PEM", None)
    key_pem = os.getenv("KEY_PEM", None)

    # Check if the certificates are set
    if ca_pem is None or cert_pem is None or key_pem is None:
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
    try:
        with open(cert_pem, "rb") as f:
            certificate_chain = f.read()
    except FileNotFoundError:
        certificate_chain = None
        logger.error("Certificate chain file not found")

    try:
        with open(key_pem, "rb") as f:
            private_key = f.read()
    except FileNotFoundError:
        private_key = None
        logger.error("Private key file not found")

    return Certificates(
        client_cert=CertValues(
            root_certificates=root_certificates,
            certificate_chain=certificate_chain,
            private_key=private_key,
        ),
        server_cert=CertValues(
            root_certificates=root_certificates,
            certificate_chain=certificate_chain,
            private_key=private_key,
        ),
    )

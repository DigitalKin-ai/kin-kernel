"""
Setup configuration for the kin_sdk package.

This script defines the package structure, dependencies, and metadata for the kin_sdk package.
It includes configuration to incorporate gRPC generated files from the 'proto' directory.
"""

import os
from typing import Dict, Any, List
from setuptools import setup, find_packages

# Read version from file
version: Dict[str, Any] = {}
with open(os.path.join("kin_sdk", "_version.py"), encoding="utf-8") as fp:
    exec(fp.read(), version)  # pylint: disable=exec-used

# Read long description from README
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Define package requirements
requirements: List[str] = [
    "loguru>=0.7.2",
    "pydantic>=2.9.1",
    "pydantic-settings>=2.5.2",
    "opentelemetry-api>=1.21.0",
    "opentelemetry-sdk>=1.21.0",
    "protovalidate==0.4.0",
    "grpcio>=1.66.1",
    "googleapis-common-protos>=1.65.0",
    "networkx>=3.3",
]


def remove_proto_prefix(items):
    """
    Remove the 'proto.' prefix from the given list of items.
    """
    return [
        item.replace("proto.", "", 1) if item.startswith("proto.") else item
        for item in items
    ]


def remove_items_with_proto(items):
    """
    Remove items with 'proto' in the
    """
    return [item for item in items if "proto" not in item]


# Find all packages in the proto directory
proto_packages = remove_proto_prefix(find_packages(where="proto"))
proto_packages_dir = [item for item in proto_packages if "." not in item]
kin_sdk_packages = remove_items_with_proto(find_packages())

print(f"proto_packages: {proto_packages}")
print(f"proto_packages_dir: {proto_packages_dir}")
print(f"kin_sdk_packages: {kin_sdk_packages}")

print(
    {
        pkg: os.path.join("proto", pkg.replace(".", os.path.sep))
        for pkg in proto_packages_dir
    }
)

setup(
    name="kin_sdk",
    version=version["__version__"],
    author="DigitalKin.ai",
    author_email="contact@digitalkin.ai",
    description="kin-kernel contain the default templates of Cells that compose a Kin.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/DigitalKin-ai/kin-kernel",
    packages=kin_sdk_packages + proto_packages,
    package_dir={
        "kin_sdk": "kin_sdk",
        "proto": "proto",
        **{
            pkg: os.path.join("proto", pkg.replace(".", os.path.sep))
            for pkg in proto_packages_dir
        },
    },
    package_data={
        "kin_sdk": ["py.typed"],
        "proto": ["proto/*"],
    },
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.10",
    license="CC BY-NC-SA 4.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries",
        "Operating System :: OS Independent",
    ],
    keywords="kin_sdk cells autonomous-agents IoA DigitalKin",
)

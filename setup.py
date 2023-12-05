"""
    setup.py
"""
from typing import Dict, Any
from setuptools import setup, find_packages

version: Dict[str, Any] = {}
with open("kinkernel/_version.py") as fp:
    exec(fp.read(), version)

setup(
    name="kin-kernel",
    version=version["__version__"],
    author="DigitalKin.ai",
    author_email="contact@digitalkin.ai",
    packages=find_packages(),
    # package_dir={"": "src"},
    license="LICENSE.txt",
    description="kin-kernel contain the default templates of a kin and agents that compose a Kin.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/DigitalKin-ai/kin-kernel",
    install_requires=[
        "pydantic>=1.8.2",
    ],
    python_requires=">=3.10",
)

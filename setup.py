"""
    setup.py
"""
from typing import Dict, Any
from setuptools import setup, find_packages

version: Dict[str, Any] = {}
with open("kinkernel/_version.py", encoding="utf-8") as fp:
    exec(fp.read(), version)  # pylint: disable=w0122

setup(
    name="kin-kernel",
    version=version["__version__"],
    author="DigitalKin.ai",
    author_email="contact@digitalkin.ai",
    packages=find_packages(),
    license="CC BY-NC-SA 4.0",
    description="kin-kernel contain the default templates of Cells that compose a Kin.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/DigitalKin-ai/kin-kernel",
    install_requires=[
        "pydantic>=2.5.2",
        "pydantic-settings>=2.1.0",
        "loguru>=0.7.2",
        "opentelemetry-api>=1.21.0",
        "opentelemetry-sdk>=1.21.0",
    ],
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries",
        "Operating System :: OS Independent",
    ],
    keywords="kin-kernel cells autonomous-agents IoA DigitalKin",
    include_package_data=True,
)

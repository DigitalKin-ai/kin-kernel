# 📖 DigitalKin.ai - KinKernel

[![PyPI version](https://badge.fury.io/py/kin-kernel.svg)](https://badge.fury.io/py/kin-kernel)
[![Python version](https://img.shields.io/pypi/pyversions/kin-kernel.svg)](https://pypi.python.org/pypi/kin-kernel/)
[![License](https://img.shields.io/github/license/DigitalKin/kin-kernel.svg)](https://github.com/DigitalKin-ai/kin-kernel/blob/main/LICENSE)
[![DigitalKin](https://img.shields.io/badge/DigitalKin-connect-001945)](https://vision.digitalkin.ai)
[![Discord](https://img.shields.io/badge/Discord-join-blue)](https://discord.com/invite/yVstHVcx)

Welcome to the DigitalKin KinKernel ! This package is designed to enable developers to create Cells, which are autonomous agents that can be integrated into the Internet of Agents (IoA) ecosystem powered by DigitalKin.

## 👀 Overview

The KinKernel provides a framework for creating and managing Cells. Each Cell represents a distinct autonomous agent with a specific role and behavior within the IoA. The KinKernel ensures that all Cells adhere to a standard interface and can communicate effectively within the ecosystem.

## 💡 Features

- Abstract base classes for standardizing Cell creation
- Response models for consistent communication
- Helper methods for schema information access
- Configuration management
- Example Cell implementation

## 🛠️ Installation

Before installing the KinKernel, ensure you have Python installed on your system. This package requires Python 3.10 or higher.

To install the KinKernel
With pipy:

```shell
pip install kin-kernel
```

Or clone the repository and install the dependencies:

```shell
git clone https://github.com/DigitalKin/kin-kernel.git
cd kin-kernel-kit
pip install -r requirements/prod.txt
```

For development purposes, you may also want to install the development dependencies:

```shell
pip install -r requirements/dev.txt
```

## ✨ Linter

Execute linters:

```bash
   flake8 kinkernel
   black kinkernel --check --diff
   black kinkernel
   mypy kinkernel
   pylint kinkernel
```

## 💻 Usage

To create a new Cell, you'll need to subclass the `Cell` class provided in the kinKernel and implement the required methods and properties.

Here's a simple example of a Cell that processes input data:

```python
from pydantic import BaseModel

from kinkernel import Cell
from kinkernel.config import ConfigModel, EnvVar


class MyInputModel(BaseModel):
    value1: int
    value2: str


class MyOutputModel(BaseModel):
    processed_value: int


class MyCell(Cell[MyInputModel, MyOutputModel]):
    role = "Processor"
    description = "Processes input data"
    input_format = MyInputModel
    output_format = MyOutputModel
    config = ConfigModel(
        env_vars=[
            EnvVar(key="ENV_VAR_1", value="value1"),
            EnvVar(key="ENV_VAR_2", value="value2"),
        ]
    )

    async def _execute(self, input_data: MyInputModel) -> MyOutputModel:
        # Process the input_data as needed
        exec_result = {"processed_value": input_data.value1 * 2}
        return MyOutputModel(**exec_result)
```

You can then instantiate and execute your Cell as follows:

```python
my_cell = MyCell()
input_data = MyInputModel(value1=10, value2="example")
output_data = my_cell.execute(input_data)
print(output_data)
```

For a more detailed example, refer to the `examples/simple_cell_example.py` file in the repository.

## 🧪 Testing

The CDK comes with a set of unit tests to ensure that your Cells work as expected. To run the tests, execute the following command:

```shell
pytest
```

## 👥 Contribution

Contributions to the KinKernel are welcome! If you have suggestions for improvements or find any issues, please open an issue on our GitHub repository.

## 🤗 Support

If you have any questions or need support with the KinKernel, please reach out to us at contact@digitalkin.ai.

Thank you for using the DigitalKin Cell Development Kit. We look forward to seeing the innovative Cells you'll create for the Internet of Agents!

---

Kin-kernel © 2023 by DigitalKin is licensed under CC BY-NC-SA 4.0

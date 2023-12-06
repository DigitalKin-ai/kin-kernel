Quickstart
==========

.. include:: _sidebar.rst

Installation
------------

To install kin-kernel, simply run the following command:

.. code-block:: bash

    pip install kin-kernel

For more details, visit the `kin-kernel PyPI page <https://pypi.org/project/kin-kernel/>`_.


Usage Example
-------------

Here is a simple example of how to use kin-kernel:

.. code-block:: python

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

        def execute(self, input_data: MyInputModel) -> MyOutputModel:
            # Process the input_data as needed
            exec_result = {"processed_value": input_data.value1 * 2}
            return MyOutputModel(**exec_result)

    if __name__ == "__main__":
        my_cell = MyCell()
        input_dt = MyInputModel(value1=10, value2="example")
        output = my_cell.execute(input_dt)
        print(output)
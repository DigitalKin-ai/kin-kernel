"""
Example module demonstrating how to developpe a Cell.
"""
from pydantic import BaseModel

from kinkernel import Cell
from kinkernel.config import ConfigModel, EnvVar


class MyInputModel(BaseModel):
    """
    A Pydantic model representing the input data for the cell.

    :param value1: An integer value as part of the input.
    :type value1: int
    :param value2: A string value as part of the input.
    :type value2: str
    """

    value1: int
    value2: str


class MyOutputModel(BaseModel):
    """
    A Pydantic model representing the output data of the cell.

    :param processed_value: An integer representing the processed result.
    :type processed_value: int
    """

    processed_value: int


class MyCell(Cell[MyInputModel, MyOutputModel]):
    """
    A cell that processes input data and produces an output.

    Inherits from the generic ``Cell`` class with input and output types specified.

    :ivar role: The role of the cell in processing.
    :ivar description: A brief description of the cell's functionality.
    :ivar input_format: The expected input data format.
    :ivar output_format: The expected output data format.
    :ivar config: Configuration parameters for the cell, including environment variables.
    """

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
        """
        Executes the cell's processing logic on the given input data.

        :param input_data: The input data to process.
        :type input_data: MyInputModel
        :return: The result of processing in the form of an output model.
        :rtype: MyOutputModel
        """
        # Process the input_data as needed
        exec_result = {"processed_value": input_data.value1 * 2}
        return MyOutputModel(**exec_result)


if __name__ == "__main__":
    my_cell = MyCell()
    input_dt = MyInputModel(value1=10, value2="example")
    output = my_cell.execute(input_dt)
    print(output)

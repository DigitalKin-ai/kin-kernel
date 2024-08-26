"""TODO sphinx docstring"""


class LoadingWorkflowException(Exception):
    """TODO sphinx docstring"""

    def __init__(self, original_exception):
        super().__init__(f"Caught an exception: {original_exception}")
        self.original_exception = original_exception

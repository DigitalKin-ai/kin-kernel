"""
TODO: Add sphinx docstring
"""


class ValidatedRequest:
    """TODO: Add sphinx docstring"""

    def __init__(self, request, success: bool, details: str):
        self.request = request
        self.success = success
        self.details = details

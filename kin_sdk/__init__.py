"""
This package provides the core components required to define and configure Kin modules within the system.

A Kin module is an autonomous agent characterized by its role, input and output formats, and the ability to execute specific tasks based on provided input data.
"""

import sys
import warnings
import re

original_showwarning = warnings.showwarning


def custom_showwarning(message, category, filename, lineno, file=None, line=None):
    """
    Custom warning function to ignore warnings from Protobuf.
    It ignores warnings that contain the string "Protobuf gencode version".
    """
    if not re.search(r"Protobuf gencode version", str(message)):
        original_showwarning(message, category, filename, lineno, file, line)


warnings.showwarning = custom_showwarning

# Checking version
if sys.version_info < (3, 10, 11):
    raise RuntimeError("This project requires Python 3.10.11 or higher.")

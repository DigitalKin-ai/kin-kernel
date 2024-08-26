"""
Logger module to set up a logger with a rotating file handler.
"""

import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logger(name, log_file, level=logging.INFO, output="console"):
    """Function to set up a logger with a rotating file handler."""
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    init_logger = logging.getLogger(name)
    init_logger.setLevel(level)

    if output == "file" and log_file:
        file_handler = RotatingFileHandler(log_file, maxBytes=10000, backupCount=3)
        file_handler.setFormatter(formatter)
        init_logger.addHandler(file_handler)
    else:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        init_logger.addHandler(stream_handler)

    return init_logger


# Example usage: Set up a global logger for the SDK
log_output = os.getenv("LOG_OUTPUT", "console")
log_level = os.getenv("LOG_LEVEL", "INFO").upper()

# Convert log level string to logging level
log_level = getattr(logging, log_level, logging.INFO)

LOG_DIRECTORY = "/logs"
if log_output == "file" and not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)

log_file_path = (
    os.path.join(LOG_DIRECTORY, "kin_sdk.log") if log_output == "file" else None
)

logger = setup_logger(
    "kin_sdk", log_file=log_file_path, level=log_level, output=log_output
)
logger.info("📝 Logger has been set up.")

import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logger(name, log_file, level=logging.INFO):
    """Function to set up a logger with a rotating file handler."""
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create handlers
    handler = RotatingFileHandler(log_file, maxBytes=10000, backupCount=3)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


# Example usage: Set up a global logger for the SDK
log_directory = os.path.join(os.path.dirname(__file__), "../../logs")
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logger = setup_logger("kin_sdk", os.path.join(log_directory, "kin_sdk.log"))

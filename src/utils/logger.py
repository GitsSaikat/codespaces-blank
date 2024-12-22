# src/utils/logger.py

import logging
import os

def setup_logger(name: str, log_file: str = 'me_pavement_design.log', level: int = logging.INFO) -> logging.Logger:
    """
    Sets up a logger with the specified name and log file.

    :param name: Name of the logger.
    :param log_file: File where logs will be saved.
    :param level: Logging level.
    :return: Configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding multiple handlers to the logger
    if not logger.handlers:
        # Create handlers
        fh = logging.FileHandler(log_file)
        fh.setLevel(level)
        ch = logging.StreamHandler()
        ch.setLevel(level)

        # Create formatter and add it to handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger

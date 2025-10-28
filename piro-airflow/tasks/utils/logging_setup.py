import sys
import logging


def get_logger() -> logging.Logger:
    """Get and configure out standard logger."""

    logger = logging.getLogger("piro-builder")
    logger.setLevel(logging.DEBUG)

    # add a handler to also print to stdout, if not already added
    if not logger.handlers:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%m/%d/%y %H:%M:%S %z",
        )
        stdout_handler.setFormatter(formatter)
        logger.addHandler(stdout_handler)

    return logger

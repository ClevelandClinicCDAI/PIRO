import logging
import os
import sys

from loguru import logger


def configure_logging():
    level = os.getenv("PIRO_LOG_LEVEL", "INFO").upper()
    logger.remove()
    logger.add(
        sys.stderr,
        level=level,
        format=(
            "{time:YYYY-MM-DDTHH:mm:ss.SSSZZ} | {level} | "
            "pid={process.id} | {name}:{function}:{line} | {message}"
        ),
        diagnose=False,
        colorize=False,
    )
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    handler = next(
        (
            existing
            for existing in root_logger.handlers
            if existing.get_name() == "piro.console"
        ),
        None,
    )
    if handler is None:
        handler = logging.StreamHandler(sys.stderr)
        handler.set_name("piro.console")
        root_logger.addHandler(handler)
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | pid=%(process)d | "
            "%(name)s:%(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    )


configure_logging()

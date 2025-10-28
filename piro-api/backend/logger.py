import sys

from loguru import logger

logger.add(sys.stderr, format="{time} {level} {message}")

logger.add("piro.log", rotation="1 week")

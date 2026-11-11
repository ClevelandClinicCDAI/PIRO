import logging
from pathlib import Path
import sys
from uuid import uuid4


def main():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
    from logger import logger

    marker = f"PIRO_LOGGING_CHECK_{uuid4().hex}"
    print(f"{marker} stdout", flush=True)
    print(f"{marker} stderr", file=sys.stderr, flush=True)
    logger.info("{} loguru", marker)
    logging.getLogger("piro.logging_check").info("%s standard_logging", marker)
    try:
        raise RuntimeError("Synthetic logging verification error")
    except RuntimeError:
        logger.exception("{} traceback", marker)


if __name__ == "__main__":
    main()

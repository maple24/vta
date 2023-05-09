from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add(
    "log.log",
    backtrace=True,
    diagnose=False,
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    level="TRACE"
    )


logger.info("hello")
logger.trace("debug")
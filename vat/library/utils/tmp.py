from loguru import logger

container = []

logger.add(
    container.append,
    level="ERROR",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
)

logger.info("hello")
logger.error("error")
logger.exception("exc")

print(container)

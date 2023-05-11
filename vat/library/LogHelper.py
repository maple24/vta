from loguru import logger
import os
import time
import sys

ROOT = "\\".join(os.path.abspath(__file__).split("\\")[:-3])
logger.remove()
logger.add(sys.stdout, level="INFO")
# logfile = logger.add(
#     f"{ROOT}\\log\\log_{time.strftime('%m%d%Y_%H%M%S')}.log",
#     backtrace=True,
#     diagnose=False,
#     format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
#     rotation="1 week",
#     level="TRACE",
# )
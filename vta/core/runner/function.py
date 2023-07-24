import os
import time
from datetime import datetime
from robot import run_cli
from loguru import logger
import sys
import argparse
from utils import rotate_folder, find_file

# User argument interface
parser = argparse.ArgumentParser()
parser.add_argument("--task", type=str, required=True, help="robot task file")
parser.add_argument("--slot", default=1, type=int, help="slot number")

parser.add_argument(
    "--name", default="Functional Test", type=str, help="name of combined test suite"
)
parser.add_argument(
    "--listener", default="FunctionListener.py", type=str, help="listener file"
)
parser.add_argument("--modifier", type=str, help="modifier file")
args = parser.parse_args()

TASK = args.task  # required
SLOT = args.slot  # default to be 1
REPORTNAME = args.name  # default to be `Functional Test`
LISTENER = args.listener  # default to be `FunctionListener.py`
MODIFIER = args.modifier  # default to be None

"""
=============================== DO NOT CHANGE ===============================
"""
ROOT = "\\".join(os.path.abspath(__file__).split("\\")[:-4])
LOGPATH = os.path.join(
    ROOT,
    "log",
    f"{datetime.now().strftime('%A')}_{time.strftime('%m%d%Y_%H%M')}_SLOT{SLOT}",
)
TASKPATH = find_file(os.path.join(ROOT, "vta", "tasks"), TASK)
if LISTENER:
    LISTENERPATH = os.path.join(ROOT, "vta", "core", LISTENER)
if MODIFIER:
    MODIFIERPATH = os.path.join(ROOT, "vta", "core", MODIFIER)
logger.remove()
logger.add(sys.stdout, level="DEBUG")
mylogger = logger.add(
    f"{LOGPATH}\\log_{time.strftime('%m%d%Y_%H%M%S')}.log",
    backtrace=True,
    diagnose=False,
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    rotation="1 week",
    level="TRACE",
)
rotate_folder(os.path.join(ROOT, "log"))
"""
=============================== DO NOT CHANGE ===============================
"""

# Function Runner
if not os.path.exists(TASKPATH):
    logger.error(f"{TASK} not exist!")
    exit(1)

common = [
    "--exitonfailure",
    "--outputdir",
    f"{LOGPATH}",
]
if LISTENER:
    common += ["--listener", f"{LISTENERPATH}"]
if MODIFIER:
    common += ["--prerunmodifier", f"{MODIFIERPATH}"]
variable = ["--variable", f"SLOT:SLOT_{SLOT}"]
rc = run_cli(common + variable + ["--exclude", "skip", f"{TASKPATH}"], exit=False)

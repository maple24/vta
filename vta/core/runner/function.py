import argparse
import sys
import time
from datetime import datetime
from loguru import logger
from robot import run_cli
from utils import find_file, rotate_folder
from pathlib import Path

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str, required=True, help="robot task file")
    parser.add_argument("--slot", default=1, type=int, help="slot number")
    parser.add_argument("--name", default="Functional Test", type=str, help="name of combined test suite")
    parser.add_argument("--listener", default="FunctionListener.py", type=str, help="listener file")
    parser.add_argument("--modifier", type=str, help="modifier file")
    return parser.parse_args()

def main():
    logger.info("!!Start running functional test!!")
    args = parse_arguments()

    # ====================================DO NOT CHANGE====================================
    ROOT = Path(__file__).resolve().parent.parent.parent.parent
    LOG_PATH = ROOT / "log" / f"{datetime.now().strftime('%A')}_{time.strftime('%m%d%Y_%H%M')}_SLOT{args.slot}"
    TASK_PATH = find_file(ROOT / "vta" / "tasks", args.task)
    LISTENER_PATH = ROOT / "vta" / "core" / args.listener if args.listener else None
    MODIFIER_PATH = ROOT / "vta" / "core" / args.modifier if args.modifier else None
    logger.remove()
    logger.add(sys.stdout, level="DEBUG")
    logger.add(f"{LOG_PATH}/log_{time.strftime('%m%d%Y_%H%M%S')}.log",
               backtrace=True, diagnose=False,
               format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
               rotation="1 week",
               level="TRACE")
    rotate_folder(ROOT / "log")
    # ====================================DO NOT CHANGE====================================

    if not TASK_PATH.exists():
        logger.error(f"{args.task} not exist!")
        sys.exit(1)

    common = ["--exitonfailure", "--outputdir", str(LOG_PATH)]
    if LISTENER_PATH:
        common.extend(["--listener", str(LISTENER_PATH)])
    if MODIFIER_PATH:
        common.extend(["--prerunmodifier", str(MODIFIER_PATH)])
    variable = ["--variable", f"SLOT:SLOT_{args.slot}"]
    run_cli(common + variable + ["--exclude", "skip", str(TASK_PATH)], exit=True)


if __name__ == "__main__":
    main()

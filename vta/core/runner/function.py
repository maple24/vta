# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from loguru import logger
from robot import run_cli

from .utils import find_file, rotate_folder


@click.command()
@click.option("--task", type=str, required=True, help="robot task file")
@click.option("--slot", default=1, type=int, help="slot number")
@click.option(
    "--name",
    default="Functional Test",
    type=str,
    help="name of combined test suite",
)
@click.option(
    "--listener",
    default="FunctionListener.py",
    type=str,
    help="listener file",
)
@click.option("--modifier", type=str, help="modifier file")
def runner(
    task: str,
    name: str,
    slot: int,
    listener: str,
    modifier: Optional[str],
) -> None:
    logger.info("!!Start running functional test!!")

    # ====================================DO NOT CHANGE====================================
    ROOT: Path = Path(__file__).resolve().parent.parent.parent.parent
    LOG_PATH: Path = (
        ROOT
        / "log"
        / f"{datetime.now().strftime('%A')}_{time.strftime('%m%d%Y_%H%M')}_SLOT{slot}"
    )
    TASK_PATH = find_file(ROOT / "vta" / "tasks", task)
    LISTENER_PATH: Optional[Path] = (
        ROOT / "vta" / "core" / listener if listener else None
    )
    MODIFIER_PATH: Optional[Path] = (
        ROOT / "vta" / "core" / modifier if modifier else None
    )
    logger.remove()
    logger.add(sys.stdout, level="DEBUG")
    logger.add(
        f"{LOG_PATH}/log_{time.strftime('%m%d%Y_%H%M%S')}.log",
        backtrace=True,
        diagnose=False,
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
        rotation="1 week",
        level="TRACE",
    )
    rotate_folder(ROOT / "log")
    # ====================================DO NOT CHANGE====================================

    if TASK_PATH is None:
        logger.error(f"{task} not exist!")
        sys.exit(1)

    common: list[str] = [
        "--exitonfailure",
        "--name",
        name,
        "--outputdir",
        str(LOG_PATH),
    ]
    if LISTENER_PATH:
        common.extend(["--listener", str(LISTENER_PATH)])
    if MODIFIER_PATH:
        common.extend(["--prerunmodifier", str(MODIFIER_PATH)])
    variable: list[str] = ["--variable", f"SLOT:SLOT_{slot}"]
    run_cli(common + variable + ["--exclude", "skip", str(TASK_PATH)], exit=True)


if __name__ == "__main__":
    runner()

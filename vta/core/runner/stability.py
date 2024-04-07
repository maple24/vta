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
from robot import rebot_cli, run_cli

from .utils import find_file, rotate_folder


@click.command()
@click.option("--task", type=str, required=True, help="robot task file")
@click.option("--slot", default=1, type=int, help="slot number")
@click.option("--max-loop", default=1, type=int, help="maximum number of loops")
@click.option(
    "--name",
    default="Stability Test",
    type=str,
    help="name of combined test suite",
)
@click.option(
    "--listener",
    default="StabilityListener.py",
    type=str,
    help="listener file",
)
@click.option("--modifier", type=str, help="modifier file")
def runner(
    task: str,
    slot: int,
    max_loop: int,
    name: str,
    listener: str,
    modifier: Optional[str],
) -> None:
    # ====================================DO NOT CHANGE====================================
    ROOT: Path = Path(__file__).resolve().parent.parent.parent.parent
    LOG_PATH: Path = (
        ROOT
        / "log"
        / f"{datetime.now().strftime('%A')}_{time.strftime('%m%d%Y_%H%M')}_SLOT{slot}"
    )
    TASK_PATH: Path = find_file(ROOT / "vta" / "tasks", task)
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

    if not TASK_PATH.exists():
        logger.error(f"{task} not exist!")
        sys.exit(1)

    count = 1
    for i in range(max_loop):
        logger.info("!!Start running stability test!!")
        try:
            logger.remove()
        except ValueError:
            logger.warning("Logger handler has been removed!")
        logger.add(
            f"{LOG_PATH}/log_{count}.log",
            backtrace=True,
            diagnose=False,
            format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
            rotation="1 week",
            level="TRACE",
        )
        common = [
            "--exitonfailure",
            "--outputdir",
            f"{LOG_PATH}",
            "--output",
            f"output_{count}.xml",
            "--log",
            f"log_{count}.html",
            "--report",
            "none",
        ]
        if LISTENER_PATH:
            common += ["--listener", str(LISTENER_PATH)]
        if MODIFIER_PATH:
            common += ["--prerunmodifier", str(MODIFIER_PATH)]
        variable = ["--variable", f"SLOT:SLOT_{slot}"]
        rc = run_cli(
            common + variable + ["--exclude", "skip", str(TASK_PATH)], exit=False
        )
        logger.info(f"Finish running loop {i+1}")
        if rc != 0:
            logger.warning(f"Test terminated due to exitcode {rc}!")
            break
        count += 1

    try:
        rebot_cli(
            [
                "--name",
                name,
                "--outputdir",
                f"{LOG_PATH}/report",
                f"{LOG_PATH}/*.xml",
            ]
        )
        logger.success("Reports are combined successfully!")
    except SystemExit:
        # normal exit by rebot cli
        pass
    except Exception as e:
        logger.exception("Unable to combine outputs:", e)


if __name__ == "__main__":
    runner()

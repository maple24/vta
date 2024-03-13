import os
import subprocess
import sys
import threading
import time

import schedule
from loguru import logger

sys.path.append(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2]))
from vta.api.ArtifaHelper import ArtifaHelper


class PeriodicReleaseChecker:
    """
    # Task scheduling
    def greet(name):
        print('Hello', name)

    schedule.every(2).seconds.do(greet, name='Alice')
    schedule.every(4).seconds.do(greet, name='Bob')

    from schedule import every, repeat

    @repeat(every().second, "World")
    @repeat(every().day, "Mars")
    def hello(planet):
        print("Hello", planet)
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.records = []
        self.file = os.path.join(os.path.dirname(__file__), "records.txt")

    def get(self):
        with self.lock:
            try:
                with open(self.file, "r") as f:
                    for line in f:
                        self.records.append(line.strip())
            except FileNotFoundError:
                logger.warning("Record file does not exist")

    def update(self, record):
        with self.lock:
            with open(self.file, "a") as f:
                f.write(record + "\n")

    def periodic_job(self, artifacts: list, scripts: list, condition=24, timeout=60):
        for art, scr in zip(artifacts, scripts):
            ar = ArtifaHelper(**art)
            is_new_released, version = ar.monitor(thres=condition)
            self.get()
            if is_new_released and version not in self.records:
                self.update(record=version)
                self.run_task(scr)
            else:
                logger.info("Release is not new")

    def run_task(self, script: str):
        logger.success(f"Start task {script}!")
        try:
            result = subprocess.run([script], shell=True)
            if result.returncode != 0:
                logger.error(
                    f"Schedule terminated due to errorcode! {result.returncode}"
                )
                exit()
        except subprocess.CalledProcessError as e:
            logger.error("Error executing batch script:", e)
            exit()

    def run_scheduler(self):
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == "__main__":
    ROOT = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2])
    artifacts = [
        {
            "repo": "zeekr-dhu-repos/builds/rb-zeekr-dhu_hqx424-pcs01_main_binary/daily/",
            "pattern": "_userdebug_binary.tgz$",
        },
        {
            "repo": "zeekr-dhu-repos/builds/rb-zeekr-dhu_hqx424-pcs01_main_dev/daily/",
            "pattern": "_userdebug.tgz$",
        },
        {
            # "server": "https://rb-cmbinex-fe-p1.de.bosch.com/artifactory/",
            "repo": "zeekr-dhu-repos/builds/rb-zeekr-dhu_hqx424-pcs01_main_dev_zeekr_dhu_r1_release/daily/",
            "pattern": "_userdebug.tgz$",
        },
        {
            # "server": "https://rb-cmbinex-fe-p1.de.bosch.com/artifactory/",
            "repo": "zeekr-dhu-repos/builds/rb-zeekr-dhu_hqx424-pcs01_main_binary_zeekr_dhu_r1_release/daily/",
            "pattern": "_userdebug_binary.tgz$",
        },
    ]
    scripts = [
        os.path.join(ROOT, "QVTa_binary.bat"),
        os.path.join(ROOT, "QVTa_source.bat"),
        os.path.join(ROOT, "QVTa_release_source.bat"),
        os.path.join(ROOT, "QVTa_release_binary.bat"),
    ]
    release_checker = PeriodicReleaseChecker()
    release_checker.periodic_job(artifacts=artifacts, scripts=scripts)
    schedule.every(5).minutes.do(
        release_checker.periodic_job, artifacts=artifacts, scripts=scripts
    )
    # threading.Thread(target=release_checker.run_scheduler).start()
    release_checker.run_scheduler()

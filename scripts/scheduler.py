import schedule
import threading
import subprocess
import sys
import os
import time
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

    def periodic_job(self, script: str, condition = 24):
        ar = ArtifaHelper(
            repo="zeekr-dhu-repos/builds/rb-zeekr-dhu_hqx424-pcs01_main_dev/daily/",
            pattern="_userdebug_binary_\d+_\d+.tgz$",
        )
        is_new_released, version = ar.monitor(thres=condition)
        self.get()
        if is_new_released and version not in self.records:
            self.run_task(script)
            self.update(record=version)
        else:
            logger.info("Release is not new")

    def run_task(self, script: str):
        logger.success("Start task!")
        try:
            subprocess.Popen([script], shell=True)
        except subprocess.CalledProcessError as e:
            logger.error("Error executing batch script:", e)

    def run_scheduler(self):
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == "__main__":
    ROOT = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2])
    script = os.path.join(ROOT, "QVTa.bat")
    release_checker = PeriodicReleaseChecker()
    schedule.every(1).hour.do(release_checker.periodic_job, script=script)
    # threading.Thread(target=release_checker.run_scheduler).start()
    release_checker.run_scheduler()

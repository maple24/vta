import os
import re
from typing import Union, Tuple
import serial
import time
import threading
import queue
from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, level="INFO")
logger.add(
    os.path.abspath("log\\log.log"),
    backtrace=True,
    diagnose=False,
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    rotation="1 week",
    level="TRACE",
)


class putty_helper:
    def __init__(self):
        self.putty_object = None
        self.matchTrace_queue: queue.Queue[tuple[float, str]] = queue.Queue()
        self.monitorTrace_queue: queue.Queue[tuple[float, str]] = queue.Queue()
        self.event_putty_wait4trace = threading.Event()
        self.event_putty_monitor = threading.Event()
        self.event_putty_running = threading.Event()

    def __read(self) -> None:
        """
        Description: Continuously read data from buffer
        """
        while True:
            if not self.event_putty_running.isSet():
                logger.warning("Serial event is cancelled!")
                break

            line = self.putty_object.readline().decode().strip()
            if line:
                logger.trace("[{stream}] - {message}", stream="PuttyRx", message=line)
                now_tick = time.time()
                if self.event_putty_monitor.isSet():
                    self.monitorTrace_queue.put((now_tick, line))
                if self.event_putty_wait4trace.isSet():
                    self.matchTrace_queue.put((now_tick, line))

    def __isLoginedin(self) -> bool:
        """
        Description: press enter to check if the serial locked
        """
        res, _ = self.wait_for_trace("Incorrect", "\n", 3)
        if res:
            logger.error("Login error! Please restart!")
            return False
        res, _ = self.wait_for_trace("(login:.*)", "\n", 3)
        if res:
            logger.info("Serial console is locked, need login in")
            return False
        logger.info("Serial console already logged in")
        return True

    def connect(self, dPutty: dict) -> None:
        """
        Description: Initiate the putty interface
        """
        if not dPutty.get("putty_enabled"):
            logger.warning("[Putty] Putty disabled, skip initiating")
            return

        logger.info("Start initiating PuTTY interface ...")
        comport = dPutty.get("putty_comport")
        baudrate = int(dPutty.get("putty_baudrate", 115200))
        self.username = dPutty.get("putty_username", "root")
        self.password = dPutty.get("putty_password")
        self.event_putty_running.set()
        try:
            self.putty_object = serial.Serial(
                port=comport, baudrate=baudrate, timeout=3.0
            )
        except:
            logger.exception("Failed to open serial port!")
            exit(1)
        t = threading.Thread(target=self.__read)
        t.setDaemon(True)
        t.start()

    def disconnect(self) -> None:
        """
        Description: De-Init the putty serial interface
        """
        self.event_putty_running.clear()
        self.putty_object.close()
        logger.info("Close serial connection!")

    def send_command(self, cmd: str) -> None:
        """
        Description: Send the command string to PuTTY interface
        """
        if not self.putty_object:
            logger.error("No serial object found!")
            return

        cmd = cmd.rstrip()
        self.putty_object.write(cmd.encode())
        self.putty_object.write("\n".encode())
        self.putty_object.flushInput()
        logger.info("[{stream}] - {message}", stream="PuttyTx", message=cmd)

    def wait_for_trace(
        self, pattern: str, cmd: str = "", timeout: float = 5.0
    ) -> Tuple[bool, Union[Tuple[str], None]]:
        """
        Description: Trigger the command and wait for expected trace pattern w/ defined timeout
        """
        self.event_putty_wait4trace.set()
        ts = time.time()
        self.send_command(cmd)

        while True:
            if time.time() - ts > timeout:
                logger.warning(
                    f"Max timeout reached, unable to match pattern `{pattern}`!"
                )
                return False, None
            try:
                time_tick, trace = self.matchTrace_queue.get(block=False)
            except queue.Empty:
                continue
            else:
                self.matchTrace_queue.task_done()
            match = re.search(pattern, trace)
            if match:
                break

        matched = match.groups()
        logger.info(
            f"OK! Found matched - {matched}, elapsed time is {round(time_tick - ts, 2)}s"
        )
        self.event_putty_wait4trace.clear()
        self.matchTrace_queue.queue.clear()
        return True, matched

    def login(self) -> None:
        """
        Description: Login the putty console with user / password
        """
        if self.__isLoginedin():
            logger.info("Info: No need to login putty console")
            return

        retry = 0
        while retry < 5:
            retry += 1
            logger.info(f"Trying to login putty console Nr.{retry} ...")
            res, _ = self.wait_for_trace(
                "(Password:.*)|(Logging in with home .*)", self.username, 5
            )
            if not res:
                continue
            res, _ = self.wait_for_trace("(Logging in with home .*)", self.password, 5)
            if res:
                logger.info("Success to login")
                return
        logger.error("Fail to login!")

    def enable_monitor(self) -> None:
        """
        Description: Enable the trace monitor, each trace line will be pushed to this container
        """
        self.monitorTrace_queue.queue.clear()
        self.event_putty_monitor.set()
        logger.info("PuTTY monitor enabled")

    def disable_monitor(self) -> None:
        """
        Description: Disable the trace monitor, each trace line will be pushed to this container
        """
        self.event_putty_monitor.clear()
        logger.info("PuTTY monitor disabled")

    def get_trace_container(self) -> list:
        """
        Description: get the monitorTrace_queue
        """
        logger.info("Get trace container")
        traces = list(self.monitorTrace_queue.queue)
        return traces


if __name__ == "__main__":
    """
    Result:\\s(.*) bosch_swdl -b normal
    """
    mputty = putty_helper()
    dputty = {
        "putty_enabled": True,
        "putty_comport": "COM15",
        "putty_baudrate": 115200,
        "putty_username": "root",
        "putty_password": "6679836772",
    }
    mputty.connect(dputty)
    res, matched = mputty.wait_for_trace(
        pattern="Result:\\s(.*)", cmd="bosch_swdl -b normal"
    )
    print(matched)

import re
from typing import Optional, Tuple
import serial
import time
import threading
import queue
from loguru import logger


class PuttyHelper:
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self):
        self.putty_object = None
        self.waitTrace_queue: queue.Queue[tuple[float, str]] = queue.Queue()
        self.monitorTrace_queue: queue.Queue[tuple[float, str]] = queue.Queue()
        self.event_waitTrace = threading.Event()
        self.event_monitorTrace = threading.Event()
        self.event_reader = threading.Event()

    def _serial_reader(self) -> None:
        """
        Description: Continuously read data from buffer
        """
        while True:
            if not self.event_reader.isSet():
                logger.warning("Serial reader event is cancelled!")
                break

            line = self.putty_object.readline().decode("utf-8", "ignore").strip()
            if line:
                logger.debug("[{stream}] - {message}", stream="PuttyRx", message=line)
                now_tick = time.time()
                if self.event_monitorTrace.isSet():
                    self.monitorTrace_queue.put((now_tick, line))
                if self.event_waitTrace.isSet():
                    self.waitTrace_queue.put((now_tick, line))

    def _isLoginedin(self) -> bool:
        """
        Description: press enter to check if the serial locked
        """
        res, _ = self.wait_for_trace("Login incorrect", "\n", 3, False)
        if res:
            logger.error("Login error! Please restart!")
            return False
        res, _ = self.wait_for_trace("(login:.*)", "\n", 3, False)
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
        self.event_reader.set()
        try:
            self.putty_object = serial.Serial(
                port=comport, baudrate=baudrate, timeout=3.0
            )
        except:
            logger.exception("Failed to open serial port!")
            exit(1)
        t = threading.Thread(target=self._serial_reader)
        t.setDaemon(True)
        t.start()

    def disconnect(self) -> None:
        """
        Description: De-Init the putty serial interface
        """
        self.event_reader.clear()
        if self.putty_object:
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

    def send_command_and_return_traces(self, cmd: str, wait: float = 2.0) -> list:
        """
        Description: Send the command and return traces
        """
        self.login()
        self.event_waitTrace.set()
        self.send_command(cmd)
        time.sleep(wait)
        traces = [x[1] for x in self.waitTrace_queue.queue]
        self.waitTrace_queue.queue.clear()
        self.event_waitTrace.clear()
        return traces

    def wait_for_trace(
        self, pattern: str, cmd: str = "", timeout: float = 10.0, login: bool = True
    ) -> Tuple[bool, Optional[list]]:
        """
        Description: Trigger the command and wait for expected trace pattern w/ defined timeout
        """
        if not self.putty_object:
            logger.error("No serial object found!")
            return
        if login:
            self.login()
        self.event_waitTrace.set()
        ts = time.time()
        self.send_command(cmd)

        while True:
            time.sleep(0.005)
            if time.time() - ts > timeout:
                logger.warning(
                    f"Max timeout reached, unable to match pattern `{pattern}`!"
                )
                return False, None
            try:
                time_tick, trace = self.waitTrace_queue.get(block=False)
            except queue.Empty:
                continue
            else:
                self.waitTrace_queue.task_done()
            match = re.search(pattern, trace)
            if match:
                break

        matched = match.groups()
        logger.success(
            f"OK! Found matched - {matched}, elapsed time is {round(time_tick - ts, 2)}s"
        )
        self.event_waitTrace.clear()
        self.waitTrace_queue.queue.clear()
        return True, matched

    def login(self) -> None:
        """
        Description: Login the putty console with user / password
        """
        if self._isLoginedin():
            logger.info("Info: No need to login putty console")
            return

        retry = 0
        while retry < 5:
            retry += 1
            logger.info(f"Trying to login putty console Nr.{retry} ...")
            res, _ = self.wait_for_trace(
                "(Password:.*)|(Logging in with home .*)", self.username, 5, False
            )
            if not res:
                continue
            res, _ = self.wait_for_trace(
                "(Logging in with home .*)", self.password, 5, False
            )
            if res:
                logger.success("Success to login")
                return
        logger.error("Fail to login!")

    def enable_monitor(self) -> None:
        """
        Description: Enable the trace monitor, each trace line will be pushed to this container
        """
        self.monitorTrace_queue.queue.clear()
        self.event_monitorTrace.set()
        logger.info("PuTTY monitor enabled")

    def disable_monitor(self) -> None:
        """
        Description: Disable the trace monitor, each trace line will be pushed to this container
        """
        self.event_monitorTrace.clear()
        logger.info("PuTTY monitor disabled")

    def get_trace_container(self) -> list:
        """
        Description: get the monitorTrace_queue
        """
        if self.event_monitorTrace.isSet():
            logger.info("Get trace container")
            return [x[1] for x in self.monitorTrace_queue.queue]
        logger.warning("Please make sure trace monitor is enabled!")


if __name__ == "__main__":
    """
    Result:\\s(.*) bosch_swdl -b normal
    """
    mputty = PuttyHelper()
    dputty = {
        "putty_enabled": True,
        "putty_comport": "COM15",
        "putty_baudrate": 115200,
        "putty_username": "zeekr",
        "putty_password": "Aa123123",
    }
    mputty.connect(dputty)
    res, matched = mputty.wait_for_trace(
        pattern="Result:\\s(.*)", cmd="bosch_swdl -b normal"
    )
    print(matched)

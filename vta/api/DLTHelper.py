import queue
import re
import threading
import time
from typing import Optional, Tuple

import serial
from loguru import logger


class DLTHelper:
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self):
        self.dlt_object = None
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

            data = self.dlt_object.read_until(expected=b"DLS")
            if tmp := self._filter(data):
                line = tmp.strip()
                logger.debug("[{stream}] - {message}", stream="DLTRx", message=line)
                now_tick = time.time()
                if self.event_monitorTrace.isSet():
                    self.monitorTrace_queue.put((now_tick, line))
                if self.event_waitTrace.isSet():
                    self.waitTrace_queue.put((now_tick, line))

    def _filter(self, rawBytes):
        # test
        data = (
            rawBytes[15:19] + b" " + rawBytes[19:23] + b" " + rawBytes[28:-3]
        ).decode("utf-8", errors="ignore")
        # zeerk
        # data = (
        #     rawBytes[5:8]
        #     + b" "
        #     + rawBytes[19:23]
        #     + b" "
        #     + rawBytes[23:27]
        #     + b" "
        #     + rawBytes[33:-3]
        # ).decode("utf-8", errors="ignore")
        # gwm
        # data = (
        #     rawBytes[5:8]
        #     + b" "
        #     + rawBytes[15:19]
        #     + b" "
        #     + rawBytes[19:23]
        #     + b" "
        #     + rawBytes[28:-3]
        # ).decode("utf-8", errors="ignore")
        if len(data) < 20 or "MAIN" in data:
            return
        return data

    def connect(self, dDlt: dict) -> None:
        """
        Description: Initiate the DLT interface
        """
        if not dDlt.get("dlt_enabled"):
            logger.warning("[DLT] Dlt disabled, skip initiating")
            return

        logger.info("Start initiating DLT interface ...")
        comport = dDlt.get("dlt_comport")
        self.event_reader.set()
        try:
            self.dlt_object = serial.Serial(port=comport, baudrate=115200, timeout=3.0)
        except:
            logger.exception("Failed to open serial port!")
            exit(1)
        t = threading.Thread(target=self._serial_reader)
        t.setDaemon(True)
        t.start()

    def disconnect(self) -> None:
        """
        Description: De-Init the DLT serial interface
        """
        self.event_reader.clear()
        if self.dlt_object:
            self.dlt_object.close()
            logger.info("Close serial connection!")

    def send_command(self, cmd: str) -> None:
        """
        Description: Send the command string to DLT interface
        """
        if not self.dlt_object:
            logger.error("No serial object found!")
            return

        cmd = cmd.rstrip()
        self.dlt_object.write(cmd.encode())
        self.dlt_object.write("\n".encode())
        self.dlt_object.flushInput()
        logger.info("[{stream}] - {message}", stream="DLTTx", message=cmd)

    def send_command_and_return_traces(self, cmd: str, wait: float = 2.0) -> list:
        """
        Description: Send the command and return traces
        """
        self.event_waitTrace.set()
        self.send_command(cmd)
        time.sleep(wait)
        traces = [x[1] for x in self.waitTrace_queue.queue]
        self.waitTrace_queue.queue.clear()
        self.event_waitTrace.clear()
        return traces

    def wait_for_trace(
        self, pattern: str, cmd: str = "", timeout: float = 10.0
    ) -> Tuple[bool, Optional[list]]:
        """
        Description: Trigger the command and wait for expected trace pattern w/ defined timeout
        """
        if not self.dlt_object:
            logger.error("No serial object found!")
            return
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

    def enable_monitor(self) -> None:
        """
        Description: Enable the trace monitor, each trace line will be pushed to this container
        """
        self.monitorTrace_queue.queue.clear()
        self.event_monitorTrace.set()
        logger.info("DLT monitor enabled")

    def disable_monitor(self) -> None:
        """
        Description: Disable the trace monitor, each trace line will be pushed to this container
        """
        self.event_monitorTrace.clear()
        logger.info("DLT monitor disabled")

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
    mdlt = DLTHelper()
    dDlt = {
        "dlt_enabled": True,
        "dlt_comport": "COM7",
    }
    mdlt.connect(dDlt)
    time.sleep(5)

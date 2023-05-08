import os
import re
import serial
import time
import threading
import queue
import collections
import copy
from loguru import logger

logger.add(os.path.abspath("log\\log.log"), rotation="1 week")


class putty_helper:
    def __init__(self):
        self.putty_object = None
        self.putty_ex_filter = []
        self.putty_wait4trace_queue: queue.Queue[tuple[float, str]] = queue.Queue()
        self.putty_monitor_queue: collections.deque[
            tuple[float, str]
        ] = collections.deque()
        self.putty_monitor_lock = threading.Lock()
        self.event_putty_wait4trace = threading.Event()
        self.event_putty_monitor = threading.Event()
        self.event_putty_running = threading.Event()

    def __serial_thread(
        self, com_port: str, baud_rate: int = 115200, timeout: float = 2.0
    ):
        """
        Description: Continuously read data from buffer
        :param com_port the serial port id
        :param baud_rate the baudrate for this serial port
        :param timeout the max timeout for reading
        :return
        """
        try:
            logger.info("Start thread serial port reading ...")
            self.event_putty_running.clear()

            self.putty_object = serial.Serial(com_port, baud_rate)
            if self.putty_object is None:
                logger.info("Error! Fail to init putty object", "error")
                return

            if self.putty_object.isOpen():
                self.putty_object.close()

            self.putty_object.open()
            if self.putty_object.isOpen():
                logger.info("OK! Open putty serial port Success")
            else:
                logger.info("NOK! Failed to open putty serial port !")

        except:
            logger.error("Error! Initiating putty rx", "error")
            return

        settings_dict = self.putty_object.get_settings()
        settings_dict["timeout"] = timeout
        self.putty_object.apply_settings(settings_dict)
        self.putty_object.set_buffer_size(rx_size=1024 * 10)
        self.event_putty_running.set()

        rx_ln = ""
        while True:
            if not self.event_putty_running.isSet():
                logger.info("Requesting stopping Thread-Read-Putty-Port !")
                break

            rx_ln = self.putty_object.readline()

            try:
                bLine2Drop = False
                dstr = rx_ln.decode("utf-8", "ignore").strip()
                if dstr == "":
                    continue

                for p in self.putty_ex_filter:
                    m = p.search(dstr)
                    if m is None:
                        continue
                    bLine2Drop = True
                    break

            except:
                logger.info("Error! Decode serial raw data !", "error")
                dstr = ""

            finally:
                if bLine2Drop is True:
                    continue
                if dstr != "":
                    logger.info(dstr, "trace", stream="PuttyRx")

                now_tick = time.time()
                if self.event_putty_monitor.isSet():
                    self.putty_monitor_lock.acquire()
                    self.putty_monitor_queue.append((now_tick, dstr))
                    self.putty_monitor_lock.release()

                if self.event_putty_wait4trace.isSet():
                    self.putty_wait4trace_queue.put((now_tick, dstr))

        # Thread stopped
        logger.info("Quitting Putty-Read-Thread ...")
        self.event_putty_running.clear()
        self.event_putty_wait4trace.clear()
        self.event_putty_monitor.clear()
        self.putty_wait4trace_queue.queue.clear()
        self.putty_monitor_lock.acquire()
        self.putty_monitor_queue.clear()
        self.putty_monitor_lock.release()

    def __isLoginedin(self) -> bool:
        """
        Description: press enter to check if the serial locked
        :return: true for logged in, false for locked
        """
        _, mat = self.wait_for_trace("(login:.*)", "\n", 3)
        if mat:
            logger.info("Serial console is locked, need login in")
            return False
        logger.info("Serial console already logged in")
        return True

    def connect(self, dPutty: list) -> None:
        """
        Description: Initiate the putty interface
        :param dPutty the dict parameters for initiating
        :param report_folder the log file will be preserved in this report folder
        """

        self.putty_enabled = eval(dPutty["putty_enabled"].capitalize())
        if self.putty_enabled is False:
            logger.info("[Putty] Putty disabled, skip initiating")
            return

        logger.info("Start initiating PuTTY interface ...")

        com_port = dPutty.get("putty_comport", "COM0")
        putty_baudrate = int(dPutty.get("putty_baudrate", 115200))
        self.putty_login_user = dPutty.get("putty_username", "root")
        self.putty_login_passwrod = dPutty.get("putty_password", "")
        self.putty_ex_filter = [re.compile(x) for x in dPutty["putty_ex_filter"]]
        logger.info(
            "Info: Putty exclude filter is - '{}'".format(
                repr(dPutty["putty_ex_filter"])
            )
        )

        if self.putty_enabled is False:
            logger.info("Warn! PuTTY disabled !")
            return

        self.thrd_putty_obj = threading.Thread(
            target=self.__serial_thread, args=(com_port, putty_baudrate)
        )
        self.thrd_putty_obj.setDaemon(True)
        self.thrd_putty_obj.start()
        logger.info("Waiting threading initiating ...")
        self.event_putty_running.wait(30.0)
        logger.info("Putty interface initialized")

    def disconnect(self) -> None:
        """
        Description: De-Init the putty serial interface
        """
        self.event_putty_running.clear()

    def cmd(self, sCmd):
        """
        Description: Send the command string to PuTTY interface
        :param sCmd, the raw command string
        """
        if self.putty_enabled is False:
            logger.warning("[PuttyCmd] Warn! PuTTY Cmd disabled !")
            return

        try:
            if sCmd.startswith("\n"):
                logger.info("Input <ENTER>", stream="PuttyTx")
                self.putty_object.write("\n".encode("utf-8"))
                self.putty_object.flushInput()
                sCmd = sCmd[1:]

            sCmd = sCmd.rstrip()
            if sCmd == "":
                return
            self.putty_object.write(sCmd.encode("raw_unicode_escape"))
            self.putty_object.write("\n".encode("raw_unicode_escape"))
            self.putty_object.flushInput()
            logger.info(f"[PuttyCmd] {sCmd}", stream="PuttyTx")

        except:
            logger.info("Error! occurred in Cmd() !", "error")

    def wait_for_trace(self, pattern, cmd="", timeout=10.0):
        """
        Description: Trigger the command and wait for expected trace pattern w/ defined timeout
        :param pattern the trace pattern to be waited for
        :param cmd the command string to be sent via interface
        :param timeout the max timeout
        :return int, (None, tuple)
        """
        matched = None

        if self.putty_enabled is False:
            logger.warning("[PuTTYWait4Trace] Warn! PuTTY Wait4Trace disabled !")
            return res, None

        try:
            self.putty_wait4trace_queue.queue.clear()
            self.event_putty_wait4trace.set()
            ts = time.time()
            self.cmd(cmd)

            while True:
                if time.time() - ts > timeout:
                    logger.info("[PuttyResponse] Reach max timeout !")
                    break

                if self.putty_wait4trace_queue.empty():
                    continue

                time_tick, trace = self.putty_wait4trace_queue.get(block=False)
                matched = re.search(pattern, trace)
                if matched:
                    break

            # Check final result
            if matched is None:
                info2print = "[PuttyResponse] NOK! Not found pattern {}".format(
                    repr(pattern)
                )
                logger.info(info2print)

            else:
                matched = matched.groups()
                info2print = "[PuttyResponse] OK! Found matched - {}, elapsed time is {}s".format(
                    repr(matched), round(time_tick - ts, 2)
                )
                logger.info(info2print)

        except:
            logger.info("Error! PuTTY wait_for_trace !", "error")

        finally:
            self.event_putty_wait4trace.clear()
            self.putty_wait4trace_queue.queue.clear()
            return res, matched

    def login(self):
        """
        Description: Login the putty console with user / password
        """
        if self.putty_enabled is False:
            logger.warning("[Putty] Putty disabled, skip login")
            return res

        logger.info("Try to login PuTTY serial console")

        if self.__isLoginedin():
            logger.info("Info: No need to login putty console")
            return res

        logger.info(
            "Trying to login with {}@{} ".format(
                self.putty_login_user, self.putty_login_passwrod
            )
        )
        retry = 0
        max_retry = 5
        while retry < max_retry:
            retry += 1
            logger.info(
                "Trying to login putty console Nr.{}/{} ...".format(retry, max_retry)
            )
            res, mat = self.wait_for_trace(
                "(Password:.*)|(Logging in with home .*)", "root", 5
            )
            if mat is None:
                logger.info(
                    "Login Error with {}@{} ".format(
                        self.putty_login_user, self.putty_login_passwrod
                    )
                )
                res = Res["ERR"]
                continue
            else:
                if mat[1] is not None:
                    res = Res["OK"]
                    break

            res, mat2 = self.wait_for_trace(
                "(Logging in with home .*)", self.putty_login_passwrod, 5
            )
            if mat2:
                res = Res["OK"]
                break
            else:
                logger.info("Login Error !")
                res = Res["ERR"]

        if res == Res["OK"]:
            logger.info("OK! Success to login finally")
        else:
            logger.info(
                "NOK! Failed to login after {} retries finally !".format(max_retry)
            )

        return res

    def enable_monitor(self) -> None:
        """
        Description: Enable the trace monitor, each trace line will be pushed to this container
        """
        self.putty_monitor_lock.acquire()
        self.putty_monitor_queue.clear()
        self.putty_monitor_lock.release()
        self.event_putty_monitor.set()
        logger.info("PuTTY monitor enabled")

    def disable_monitor(self) -> None:
        """
        Description: Disable the trace monitor, each trace line will be pushed to this container
        """
        self.event_putty_monitor.clear()
        logger.info("PuTTY monitor disabled")

    def send_cmd_and_fetch_trace_container(self, cmd2sent="", timeout=10):
        """
        Description: Fetch the trace from putty in next given timeouts after sent command if necessary
        """
        if self.putty_enabled is False:
            logger.warning("[PuTTYSendCmdAndFetchTraceContainer] Putty disabled !")
            return

        traces = []
        try:
            self.enable_monitor()
            self.cmd(cmd2sent)
            Wait(timeout, "s")

        except:
            logger.info("Error! [GetTraceBlock]", "error")

        finally:
            self.disable_monitor()
            while True:
                if not self.putty_monitor_queue:
                    break
                self.putty_monitor_lock.acquire()
                _, trace = self.putty_monitor_queue.popleft()
                self.putty_monitor_lock.release()
                traces.append(trace)

            return traces

    def fetch_trace_container(self) -> list:
        """
        Description: Get the putty runtime trace container directly
        """
        traces = []
        end_tick = time.time()
        while True:
            if not self.putty_monitor_queue:
                break
            self.putty_monitor_lock.acquire()
            tick, trace = self.putty_monitor_queue.popleft()
            self.putty_monitor_lock.release()
            if tick - end_tick >= 0:
                break
            traces.append(trace)

        return traces

    def get_trace_container(self):
        """
        Description: Copy the putty_monitor_queue and return the traces
        """
        traces = []
        end_tick = time.time()
        try:
            self.putty_monitor_lock.acquire()
            putty_queue = copy.deepcopy(self.putty_monitor_queue)
            self.putty_monitor_lock.release()
            while True:
                if not putty_queue:
                    break
                tick, trace = putty_queue.popleft()
                if tick - end_tick >= 0:
                    break
                traces.append(trace)
        except:
            get_traceback()
        finally:
            del putty_queue
            return traces

    def clear_trace_container(self) -> None:
        """
        Description: Clear message queue of putty helper
        """
        logger.debug("Try to clear trace container")
        self.putty_monitor_lock.acquire()
        self.putty_monitor_queue.clear()
        self.putty_monitor_lock.release()
        logger.debug("Succeeded to clear trace container")

    def wait_for_multi_trace(self, pattern, cmd, rep, timeout=10):
        """
        Description: Send command and wait for multiply trace candidates
        :param "pattern", the pattern to be matched
        :param "cmd", the command to be sent
        :param "rep", how many repetition expected
        :param "timeout", max. time to waiting for trace
        :return int
        """
        counter = 0
        matchedItems = []

        if self.putty_enabled is False:
            logger.warning("[PuTTYWait4MultiTrace] Putty disabled !")
            return Res["ERR"], None

        traces = self.send_cmd_and_fetch_trace_container(cmd2sent=cmd, timeout=timeout)

        for ln in traces:
            m = re.search(pattern, ln)
            if m is None:
                continue
            logger.debug("[Wait4MultiTrace] Found candidate - {}".format(m.group(0)))
            if not m.groups():
                matchedItems.append(m.group(0))
            else:
                matchedItems.append(m.groups())

            counter += 1

        if counter != rep:
            logger.error(
                "[Wait4MultiTrace] NOK! Counter not matched [Found] {} != {} [Exp.] !".format(
                    counter, rep
                )
            )
            res = Res["ERR"]

        else:
            logger.error(
                "[Wait4MultiTrace] OK! Counter matched [Found] {} == {} [Exp.]".format(
                    counter, rep
                )
            )
            res = Res["OK"]

        return res, matchedItems

    def send_cmds_and_match_patterns(
        self, cmds=[], patterns=[], timeout=10, search_from_start=False
    ):
        """
        Description: Send commands and wait timeout, finally check traces received are matched with patterns ony by one.
        """
        res = Res["ERR"]
        if self.putty_enabled is False:
            logger.warning("[PuTTYSendCmdsAndWaitPatterns] Warn! PuTTY disabled !")
            return res

        if not patterns:
            logger.info(
                "[SendCmdsMatchPatterns] Error! No valid patterns input !", "error"
            )
            return res

        traces = []
        try:
            self.enable_monitor()
            for cmd in cmds:
                self.cmd(cmd)
            Wait(timeout, "s")

        except:
            logger.info("Error! [SendCmdsMatchPatterns]", "error")

        finally:
            self.disable_monitor()
            while True:
                if not self.putty_monitor_queue:
                    break
                self.putty_monitor_lock.acquire()
                tick, trace = self.putty_monitor_queue.popleft()
                self.putty_monitor_lock.release()
                traces.append(trace)

        # Check patterns
        last_index = 0
        results = [Res["ERR"]] * len(patterns)
        for x in range(len(patterns)):
            patt = patterns[x]
            logger.debug(">> Matching pattern: " + patt)
            traces = traces[last_index:]
            for i in range(len(traces)):
                ln = traces[i]
                m = re.search(patt, ln)
                if m is None:
                    continue
                logger.info("OK! Found matched pattern - '{}'".format(patt), "info")
                # New added
                if search_from_start is False:
                    last_index = i
                else:
                    pass
                results[x] = Res["OK"]
                break
            else:
                logger.info("NOK! Not found pattern - '{}'".format(patt), "info")

        res = Res["ERR"] if Res["ERR"] in results else Res["OK"]
        return res

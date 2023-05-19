from datetime import datetime
from enum import Enum
from multiprocessing import Event, Lock, Condition
from multiprocessing.managers import BaseManager
import psutil
import time


ADDRESS = r"\\.\pipe\str_flexray_agent"


class NoClientsFoundException(Exception):
    pass


class ClientStatus(Enum):
    OFFLINE = 0
    INIT = 1
    READY_FOR_SUSPEND = 2
    READY_FOR_STOP_FLEXRAY = 3
    READY_FOR_RESUME = 4


def _log(msg: str):
    print(f'[{datetime.now().strftime("%Y%m%d %H:%M:%S.%f")}] {msg}')


class SharedController(object):
    def __init__(self):
        self.client_pid_status_table: dict[int, ClientStatus] = {}
        self.client_pid_status_table_lock = Lock()
        self.client_pid_status_table_update_event = Event()

        self.suspend_condition = Condition()
        self.stop_flexray_condition = Condition()
        self.resume_condition = Condition()

        self.server_waiting_for = ClientStatus.READY_FOR_SUSPEND
        self.server_waiting_for_lock = Lock()

    def client_register(self, pid: int):
        with self.client_pid_status_table_lock:
            if pid in self.client_pid_status_table:
                return
            self.client_pid_status_table[pid] = ClientStatus.INIT

    def client_deregister(self, pid: int):
        with self.client_pid_status_table_lock:
            if pid not in self.client_pid_status_table:
                return
            del self.client_pid_status_table[pid]

    def client_update_status(self, pid: int, status: ClientStatus):
        _log(f"client: attempts to update status: {pid}: {status}")
        while True:
            with self.server_waiting_for_lock:
                if self.server_waiting_for == status:
                    break

                time.sleep(1)

        with self.client_pid_status_table_lock:
            self.client_pid_status_table[pid] = status

    def client_wait_suspend_condition(self):
        _log("client wait suspend condition")
        with self.suspend_condition:
            self.suspend_condition.wait()

    def client_wait_stop_flexray_condition(self):
        _log("client wait suspend condition")
        with self.stop_flexray_condition:
            self.stop_flexray_condition.wait()

    def client_wait_resume_condition(self):
        _log("client wait resume condition")
        with self.resume_condition:
            self.resume_condition.wait()

    def server_wait_for_all_clients_ready_for_suspend(self):
        # Ugly code here, but keep it easy to understand
        while True:
            try:
                self.server_wait_for_all_clients_in_special_status(
                    ClientStatus.READY_FOR_SUSPEND
                )
            except NoClientsFoundException:
                time.sleep(10)
            else:
                break

    def server_wait_for_all_clients_ready_for_stop_flexray(self):
        self.server_wait_for_all_clients_in_special_status(
            ClientStatus.READY_FOR_STOP_FLEXRAY
        )

    def server_wait_for_all_clients_ready_for_resume(self):
        self.server_wait_for_all_clients_in_special_status(
            ClientStatus.READY_FOR_RESUME
        )

    def server_wait_for_all_clients_in_special_status(
        self, excepted_status: ClientStatus
    ):
        _log(f"server wait for all clients in {excepted_status}")

        with self.server_waiting_for_lock:
            self.server_waiting_for = excepted_status

        while True:
            time.sleep(1)
            if not self.client_pid_status_table_lock.acquire(block=False):
                continue

            alive_client_pids = psutil.pids() & self.client_pid_status_table.keys()

            # remove the non-existed pid in clients_pid_status_table
            for pid in self.client_pid_status_table.keys() - alive_client_pids:
                del self.client_pid_status_table[pid]

            if not self.client_pid_status_table:
                self.client_pid_status_table_lock.release()
                raise NoClientsFoundException

            is_any_not_init = False
            for pid, current_status in self.client_pid_status_table.items():
                if current_status == ClientStatus.INIT:
                    continue

                if current_status != excepted_status:
                    # Some clients status not match, keep waiting
                    self.client_pid_status_table_lock.release()
                    break

                is_any_not_init = True
            else:
                self.client_pid_status_table_lock.release()
                if is_any_not_init:
                    # All clients' status match
                    # Or some of them match, other are INIT,
                    # but not all are INIT
                    return

    def server_notify_suspend_condition(self):
        with self.suspend_condition:
            self.suspend_condition.notify_all()

    def server_notify_stop_flexray_condition(self):
        with self.stop_flexray_condition:
            self.stop_flexray_condition.notify_all()

    def server_notify_resume_condition(self):
        with self.resume_condition:
            self.resume_condition.notify_all()

    def print_clients_table(self):
        # We ignore clients_pid_status_table_lock here
        with self.client_pid_status_table_lock:
            if not self.client_pid_status_table:
                return
            print("-" * 40)
            for pid, status in self.client_pid_status_table.items():
                print(f"{pid}: {status}")

            print("-" * 40)


class MySyncManager(BaseManager):
    """
    def __init__(self,
                 address: str,
                 authkey: bytes) -> None:
        super().__init__(address, authkey)
    """

    # Just for type hints, nothing else
    def SharedController(self) -> SharedController:
        ...


_shared_controller = SharedController()


def callback_get_shared_controller():
    return _shared_controller

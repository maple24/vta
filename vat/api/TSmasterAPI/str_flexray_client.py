"""Geely STR Flexray Agent
"""
from lib_str_flexray_agent import ADDRESS, SharedController, MySyncManager, ClientStatus
import os
import random
import time


def _get_shared_controller() -> SharedController:
    MySyncManager.register(typeid="SharedController")
    manager = MySyncManager(address=ADDRESS, authkey=ADDRESS.encode())
    manager.connect()
    return manager.SharedController()


def _ready_for(status: ClientStatus):
    shared_controller = _get_shared_controller()
    shared_controller.client_update_status(os.getpid(), status)
    {
        ClientStatus.READY_FOR_SUSPEND: shared_controller.client_wait_suspend_condition,
        ClientStatus.READY_FOR_STOP_FLEXRAY: shared_controller.client_wait_stop_flexray_condition,
        ClientStatus.READY_FOR_RESUME: shared_controller.client_wait_resume_condition,
    }.get(status, lambda: None)()


def register():
    shared_controller = _get_shared_controller()
    shared_controller.client_register(os.getpid())


def deregister():
    shared_controller = _get_shared_controller()
    shared_controller.client_deregister(os.getpid())


def ready_for_suspend():
    _ready_for(ClientStatus.READY_FOR_SUSPEND)


def ready_for_stop_flexray():
    _ready_for(ClientStatus.READY_FOR_STOP_FLEXRAY)


def ready_for_resume():
    _ready_for(ClientStatus.READY_FOR_RESUME)


def test() -> None:
    register()

    while True:
        ready_for_suspend()
        print("client suspend")
        time.sleep(random.randint(15, 30))
        print("client suspend done")

        ready_for_stop_flexray()
        time.sleep(random.randint(5, 10))
        print("client stop flexray done")

        is_crashed = False
        if random.randrange(3) == 1:
            print("Oops, client crashed")
            is_crashed = True

        ready_for_resume()
        if not is_crashed:
            print("client resume")
            time.sleep(random.randint(15, 30))
            print("client resume done")
            continue
        else:
            print("gather log")
            time.sleep(40)
            print("gather log done")


if __name__ == "__main__":
    test()

"""Geely STR Flexray Agent
"""
import os
import time


from lib_str_flexray_agent import (
    ADDRESS,
    SharedController,
    MySyncManager,
    NoClientsFoundException,
    callback_get_shared_controller,
)
from tsmaster_midware import TsmasterMidware


def lock_vehicle_by_key(tsmaster: TsmasterMidware):
    tsmaster.set_usage_mode_inactive()
    time.sleep(1)
    tsmaster.change_single_frame_signals(
        {"LockgCenSts_UB": 1, "LockgCenStsTrigSrc": 2, "LockgCenStsLockSt": 1}
    )
    time.sleep(1)
    tsmaster.change_signal("LockgCenStsLockSt", 3)


def main_loop(shared_controller: SharedController):
    time.sleep(1)

    tsmaster = TsmasterMidware(
        r"..\..\rbs\SDB22200_G426_ICE_High_BackboneFR_220706.xml"
    )
    tsmaster.do_init()
    tsmaster.start()
    tsmaster.set_usage_mode_driving()

    while True:
        shared_controller.server_wait_for_all_clients_ready_for_suspend()
        lock_vehicle_by_key(tsmaster)
        shared_controller.server_notify_suspend_condition()
        print("server sent flexray suspend")

        try:
            shared_controller.server_wait_for_all_clients_ready_for_stop_flexray()
        except NoClientsFoundException:
            print("No client found when waiting for ready to stop flexray")
            print("Server sent driving again")
            tsmaster.set_usage_mode_driving()
            continue

        tsmaster.stop()
        shared_controller.server_notify_stop_flexray_condition()
        print("server stopped flexray")

        try:
            shared_controller.server_wait_for_all_clients_ready_for_resume()
        except NoClientsFoundException:
            print("No client found when waiting for ready to resume")
            tsmaster.start()
            tsmaster.set_usage_mode_driving()
            continue

        # invoke notify_resume_condition before start()
        # to get screen resume duration more precisely
        shared_controller.server_notify_resume_condition()
        tsmaster.start()
        tsmaster.set_usage_mode_driving()
        print("server sent flexray resume")


def server_thread(manager: MySyncManager):
    manager.get_server().serve_forever()


def main() -> None:
    print(f"server pid: {os.getpid()}")

    # shared_controller = SharedController()

    MySyncManager.register(
        typeid="SharedController", callable=callback_get_shared_controller
    )
    manager = MySyncManager(address=ADDRESS, authkey=ADDRESS.encode())
    manager.start()

    main_loop(manager.SharedController())


if __name__ == "__main__":
    main()

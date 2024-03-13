import time

import pythoncom
import win32com.client
from loguru import logger


class TSCOM:
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self) -> None:
        pythoncom.CoInitialize()
        self.com = None
        self.app = None

    def connect(self, dtsmaster: dict):
        self.tsmaster_enabled = dtsmaster.get("tsmaster_enabled")
        if not self.tsmaster_enabled:
            logger.warning("[TSMaster] TSMaster disabled, skip initiating ...")
            return
        self.app = win32com.client.Dispatch("TSMaster.TSApplication")
        self.com = self.app.TSCOM()
        self.app.connect()
        time.sleep(1)

    def startup(self):
        self.com.flexray_rbs_set_signal_value_by_address(
            "0/BackboneFR/CDM/CemBackBoneFr02/VehModMngtGlbSafe1UsgModSts", 11
        )
        self.com.flexray_rbs_set_signal_value_by_address(
            "0/BackboneFR/CDM/CemBackBoneFr02/VehModMngtGlbSafe1CarModSts1", 0
        )

    def shutdown(self):
        self.com.flexray_rbs_set_signal_value_by_address(
            "0/BackboneFR/CDM/CemBackBoneFr02/VehModMngtGlbSafe1CarModSts1", 1
        )
        self.com.flexray_rbs_set_signal_value_by_address(
            "0/BackboneFR/CDM/CemBackBoneFr02/VehModMngtGlbSafe1UsgModSts", 0
        )

    def disconnect(self):
        if self.app:
            self.app.disconnect()

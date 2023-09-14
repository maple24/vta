import os
import sys
import serial
import time
from loguru import logger


class PPSHelper:
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self):
        self.obj_pps = None

    def init_pps(self, dPPS: dict):
        self.pps_enabled = dPPS["pps_enabled"]
        if not self.pps_enabled:
            logger.warning("[PPS] PPS disabled, skip initiating")
        logger.info("[PPS] Start initiating PPS ...")
        self.pps_port_name = dPPS["pps_comport"]
        self.pps_baurdate = int(dPPS["pps_baudrate"])
        self.pps_ctrl_channel = int(dPPS["pps_channel_used"])

    def __connect_pps(self):
        self.obj_pps = serial.Serial(self.pps_port_name, self.pps_baurdate, timeout=2)
        if self.obj_pps.isOpen():
            self.obj_pps.close()
        self.obj_pps.open()

    def __disconnect_pps(self):
        if self.obj_pps.isOpen():
            self.obj_pps.close()

    def __getvalue(self):
        val = self.obj_pps.readline()
        val = val.decode("utf-8").strip()
        data = -1 if val == "" else float(val)
        return data

    def __set_volt_scpi(self, volt, channel):
        self.__connect_pps()
        self.pps_cmd(":INST:NSEL {};:VOLT {}".format(channel, volt))
        self.__disconnect_pps()

    def pps_cmd(self, sCmd=None):
        if not sCmd.endswith("\n"):
            sCmd += "\n"
        self.obj_pps.write(sCmd.encode("utf-8"))
        self.obj_pps.flush()

    def set_volt(self, volt, channel=-1):
        channel = self.pps_ctrl_channel if channel == -1 else channel
        self.__set_volt_scpi(volt, channel)

    def get_volt(self, channel=-1):
        volt = -1
        channel = self.pps_ctrl_channel if channel == -1 else channel
        try:
            self.__connect_pps()
            self.pps_cmd(":INST:NSEL {};:MEAS:VOLT?".format(channel))
            data = self.__getvalue()
            volt = -1 if data is None else float(data)
            logger.info("Get PPS channel {0} voltage {1}V".format(channel, volt))
        except:
            logger.error("Error PPS GetVolt !")
        finally:
            self.__disconnect_pps()
            return volt

    def get_current(self, channel=-1):
        current = -1
        channel = self.pps_ctrl_channel if channel == -1 else channel
        try:
            self.__connect_pps()
            self.pps_cmd(":INST:NSEL {};:MEAS:CURR?".format(channel))
            data = self.__getvalue()
            current = -1 if data is None else float(data)
            logger.info("Get PPS channel {0} current {1}A".format(channel, current))
        except:
            logger.error("Error PPS GetCurrent !")
        finally:
            self.__disconnect_pps()
            return current


if __name__ == "__main__":
    dPPS = {
        "pps_enabled": True,
        "pps_comport": "COM16",
        "pps_baudrate": 9600,
        "pps_channel_used": 1,
    }
    mpps = PPSHelper()
    mpps.init_pps(dPPS=dPPS)
    mpps.get_volt()
    mpps.get_current()
    mpps.set_volt("12")

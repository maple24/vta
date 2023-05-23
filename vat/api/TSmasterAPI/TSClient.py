from msl.loadlib import Client64
from loguru import logger
import sys
import os

sys.path.append(os.path.dirname(__file__))


class TSClient(Client64):
    def __init__(self):
        self.tsmaster_enable = None
        self.tsmaster_rbs = None
        self.tsmaster_channel = None

    def __getSigVal(self, signalAddress):
        """
        signalAddress {channel}/{cluster}/{ecu}/{frame}/{signal}
        """
        # channel = self.tsmaster_channel_vgm if 'CEM' in signalAddress else self.tsmaster_channel_vddm
        # signalAddress = f'{channel}/{signalAddress}'
        value = self.request32("get_signal_value", signalAddress)
        return value

    def __setSigVal(self, signalAddress, value):
        """
        signalAddress {channel}/{cluster}/{ecu}/{frame}/{signal}
        """
        # channel = self.tsmaster_channel_vgm if 'VGM' in signalAddress else self.tsmaster_channel_vddm
        # signalAddress = f'{channel}/{signalAddress}'
        self.request32("set_signal_value", signalAddress, int(value))

    def init_tsmaster(self, dTSMaster):
        """
        Use TSMasterAPI to initialize the TSMaster
        :param dTSMaster: setup of RBS
        :return: void
        """
        super(TSClient, self).__init__(module32="TSAgent")
        self.tsmaster_enabled = dTSMaster.get("tsmaster_enabled", False)
        if not self.tsmaster_enabled:
            logger.warning("[TSMaster] TSMaster disabled, skip initiating ...")
            return

        self.tsmaster_rbs = dTSMaster.get("tsmaster_rbs")
        self.tsmaster_channel_vgm = dTSMaster.get("tsmaster_channel_vgm", "0")
        self.tsmaster_channel_vddm = dTSMaster.get("tsmaster_channel_vddm", "0")
        if not self.tsmaster_rbs:
            logger.warning("Warn! No TSMAster simulation cfg defined!")
            return

        logger.info("[TSMaster] Start initiating TSMaster interface ...")
        self.request32("init_tsmaster", self.tsmaster_rbs)

    def start_simulation(self):
        """
        Description: Start TSMaster simulation measurement
        """
        # print("[TSMaster] Set NM signal value before start measurement!")
        # self.set_signal('BackboneFR/VGM/VgmBackBoneFr00/NM_Vote_BackboneFR_VGM', 1)
        # self.set_signal('BackboneFR/VGM/VgmBackBoneFr00/NM_PNI_BackboneFR_VGM', 1)
        self.request32("start_simulation")
        logger.success("OK! Success to start measurement!")

    def stop_simulation(self):
        """
        Description: Stop TSMaster simulation measurement
        """
        self.request32("stop_simulation")
        logger.info("OK! Success to stop measurement!")

    def set_signal(self, signalAddress, value):
        """
        Description: set rbs signal value by address
        :param: signalAddress {cluster}/{ecu}/{frame}/{signal}
        :param: cluster: BackboneFR
        :param: ecu: VGM/VDDM/IHU
        :param: frame: VgmBackBoneFr00...
        :param: signal: NM_Vote_BackboneFR_VGM
        :param: value: int value
        :return ctypes(int)
        """
        self.__setSigVal(signalAddress, value)
        logger.info(f"OK! Set signal {signalAddress} value {value} !")

    def get_signal(self, signalAddress):
        """
        Description: get rbs signal value by address
        :param: signalAddress {cluster}/{ecu}/{frame}/{signal}
        :param: cluster: BackboneFR
        :param: ecu: VGM/VDDM/IHU
        :param: frame: VgmBackBoneFr00...
        :param: signal: NM_Vote_BackboneFR_VGM
        :return ctypes(int)
        """
        sig_val = self.__getSigVal(signalAddress)
        logger.info(f"OK! Get signal {signalAddress} with value: {sig_val} !")
        return sig_val


if __name__ == "__main__":
    tsmasterapi_dict = {
        "tsmaster_enabled": True,
        "tsmaster_rbs": "C:\\Users\\EZO1SGH\\Desktop\\Vehicle_test\\RBS_projects\\Tosun_Wakeup\\Tosun",
        "tsmaster_channel_vgm": 0,
        "tsmaster_channel_vddm": 1,
    }

    ts_app = TSClient()
    # ts_app.init_tsmaster(tsmasterapi_dict)

    # ts_app.start_simulation()
    # ts_app.set_signal(
    #     "0/BackboneFR/CEM/CemBackBoneFr02/VehModMngtGlbSafe1UsgModSts", 11
    # )
    # ts_app.set_signal("0/BackboneFR/CEM/CemBackBoneFr02/VehModMngtGlbSafe1_UB", 1)
    # ts_app.get_signal("0/BackboneFR/CEM/CemBackBoneFr02/VehModMngtGlbSafe1UsgModSts")
    # ts_app.get_signal("0/BackboneFR/CEM/CemBackBoneFr02/VehModMngtGlbSafe1_UB")
    # ts_app.stop_simulation()

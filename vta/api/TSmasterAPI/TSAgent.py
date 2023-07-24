from ctypes import c_bool, c_double, byref
from msl.loadlib import Server32


class TSAgent(Server32):
    def __init__(self, host, port, **kwargs):
        """
        Description to initialize the TSMaster
        :param:
        :return: void
        """
        self.app_name = b"TSMaster"
        self.dll_path = "TSMaster.dll"
        super(TSAgent, self).__init__(self.dll_path, "windll", host, port, **kwargs)
        self.dll = self.lib

    def init_tsmaster(self, project):
        """
        Description: initialize the TSMaster with rbs project
        :param: project: rbs project absolute path
        :return: void
        """
        self.deinitialize()
        self.dll.initialize_lib_tsmaster_with_project(
            self.app_name, project.encode("utf-8")
        )

    def start_simulation(self):
        """
        Description: start rbs simulation
        :param AChnIdx: flexray channel index
        :param ATimeout: timeout
        :return void
        """
        self.dll.tscom_flexray_rbs_enable(c_bool(True))
        self.dll.tscom_flexray_rbs_start()
        # self.dll.tsflexray_start_net(c_int(AChnIdx), c_int32(ATimeout))
        self.dll.tsapp_connect()

    def stop_simulation(self):
        """
        Description: stop rbs simulation
        :param AChnIdx: flexray channel index
        :param ATimeout: timeout
        :return void
        """
        # self.dll.tsflexray_stop_net(c_int(AChnIdx), c_int32(ATimeout))
        self.dll.tscom_flexray_rbs_enable(c_bool(False))
        self.dll.tscom_flexray_rbs_stop()
        self.dll.tsapp_disconnect()

    def set_signal_value(self, signalAddress, value):
        """
        Description: set rbs signal value by address
        :param: signalAddress {channel}/{cluster}/{ecu}/{frame}/{signal}
        :param: channel: 0 or 1
        :param: cluster: BackboneFR
        :param: ecu: VGM/VDDM/IHU
        :param: frame: VgmBackBoneFr00...
        :param: signal: NM_Vote_BackboneFR_VGM
        :param: value: int value
        :return ctypes(int)
        """
        AValue = c_double(value)
        AAddr = signalAddress.encode()
        ret = self.dll.tscom_flexray_rbs_set_signal_value_by_address(AAddr, AValue)
        return ret

    def get_signal_value(self, signalAddress):
        """
        Description: get rbs signal value by address
        :param: signalAddress {channel}/{cluster}/{ecu}/{frame}/{signal}
        :param: channel: 0 or 1
        :param: cluster: BackboneFR
        :param: ecu: VGM/VDDM/IHU
        :param: frame: VgmBackBoneFr00...
        :param: signal: NM_Vote_BackboneFR_VGM
        :return ctypes(int)
        """
        AAddr = signalAddress.encode()
        AValue = c_double(0)
        ret = self.dll.tscom_flexray_rbs_get_signal_value_by_address(
            AAddr, byref(AValue)
        )
        if ret == 0:
            return AValue.value
        return self.dll.tsapp_get_error_description(ret)

    def deinitialize(self):
        """
        Description: free resources
        :return void
        """
        self.dll.finalize_lib_tsmaster()

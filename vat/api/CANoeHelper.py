from loguru import logger
import win32com.client


class canoe_helper:
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self):
        self.project_name = None
        self.device_name = None
        self.network_name = None
        self.diagDev = None
        self.bDiagEnabled = None

    def __getEnvVar(self, var):
        """
        Description: Get the existing environment variable from CANoe interface
        :param var the environment variable name
        :return int
        """
        if self.application:
            result = self.application.Environment.GetVariable(var)
            return result.Value
        else:
            logger.info("CANoe is not open,unable to GetVariable")
            return

    def __setEnvVar(self, var, value):
        """
        Description: Set the existing environment variable from CANoe interface
        :param var the environment variable name
        :param value the variable value to be set
        """
        if self.application:
            # set the environment varible
            result = self.application.Environment.GetVariable(var)
            if isinstance(result.value, float):
                result.Value = float(value)
            elif isinstance(result.value, int):
                result.value = int(value)
            else:
                result.value = str(value)
        else:
            logger.error("CANoe is not open,unable to SetVariable")

    def __getSigVal(self, msg_name, sig_name, bus_type="CAN", channel_num=1):
        """
        Description Get the value of a raw CAN signal on the CAN simulation bus
        :param channel_num - Integer value to indicate from which channel we will read the signal, usually start from 1,
                            Check with CANoe can channel setup.
        :param msg_name - String value that indicate the message name to which the signal belong. Check DBC setup.
        :param sig_name - String value of the signal to be read
        :param bus_type - String value of the bus type - e.g. "CAN", "LIN" and etc.
        :return The CAN signal value in floating point value.
                Even if the signal is of integer type, we will still return by
                floating point value.
        """
        if self.application:
            result = self.application.GetBus(bus_type).GetSignal(
                channel_num, msg_name, sig_name
            )
            return result.Value
        else:
            logger.error("CANoe is not open,unable to GetVariable")
            return

    def __setSigVal(self, msg_name, sig_name, sig_val, bus_type="CAN", channel_num=1):
        """
        Description Get the value of a raw CAN signal on the CAN simulation bus
        :param channel_num - Integer value to indicate from which channel we will read the signal, usually start from 1,
                            Check with CANoe can channel setup.
        :param msg_name - String value that indicate the message name to which the signal belong. Check DBC setup.
        :param sig_name - String value of the signal to be read
        :param sig_val  - signal value - Cao John new added
        :param bus_type - String value of the bus type - e.g. "CAN", "LIN" and etc.
        :return The CAN signal value in floating point value.
                Even if the signal is of integer type, we will still return by
                floating point value.
        """
        if self.application:
            result = self.application.GetBus(bus_type).GetSignal(
                channel_num, msg_name, sig_name
            )
            if isinstance(result.value, float):
                result.Value = float(sig_val)
            elif isinstance(result.value, int):
                result.value = int(sig_val)
            else:
                result.value = str(sig_val)

    def __getSysVar(self, ns_name, sysvar_name):
        """
        Description: Get the system variable from CANoe interface
        :param ns_name system variable name space
        :param sysvar_name system variable value
        :return int
        """
        if self.application:
            systemCAN = self.application.System.Namespaces
            sys_namespace = systemCAN(ns_name)
            sys_value = sys_namespace.Variables(sysvar_name)
            return sys_value.Value
        else:
            logger.error("CANoe is not open,unable to GetVariable")
            return

    def __setSysVar(self, ns_name, sysvar_name, var):
        """
        Description: Set the system variable from CANoe interface
        :param ns_name system variable name space
        :param sysvar_name system variable value
        :param var the variable value to be set
        """
        if self.application:
            systemCAN = self.application.System.Namespaces
            sys_namespace = systemCAN(ns_name)
            sys_value = sys_namespace.Variables(sysvar_name)
            if isinstance(sys_value.Value, float):
                sys_value.Value = float(var)
            elif isinstance(sys_value.value, int):
                sys_value.Value = int(var)
            else:
                sys_value.Value = str(var)

    def init_canoe(self, dCANoe):
        """
        Description: Initiatialize the CANoe interface
        :param dCANoe the dict parameters for CANoe initialization
        :return int
        """
        # re-dispatch object for CANoe Application
        canoe_enabled = dCANoe.get("canoe_enabled", False)
        if not canoe_enabled:
            logger.info("[CANoe] CANoe disabled, skip initiating")
            return

        logger.info("[CANoe] Start initiating CANoe interface ...")
        self.application = win32com.client.DispatchEx("CANoe.Application")
        self.ver = self.application.Version
        logger.info(f"Init canoe with version {self.ver}")

    def start_measurement(self):
        """
        Description: Start CANoe simulation measurement
        """
        retry = 0
        retry_counter = 5
        # try to establish measurement within 20s timeout
        while not self.application.Measurement.Running and (retry < retry_counter):
            logger.info("Info: Starting CANoe simulation ...")
            self.application.Measurement.Start()
            retry += 1
        if retry == retry_counter:
            logger.error(
                "Error! CANoe start measuremet failed, Please Check Connection!"
            )
        else:
            logger.info("Info: CANoe simulation started")

    def stop_measurement(self):
        """
        Description: Stop CANoe simulation measurement
        """
        logger.info("Info: Stopping CANoe simulation ...")
        if self.application.Measurement.Running:
            self.application.Measurement.Stop()
        else:
            logger.info("OK! CAN simu already stopped")

    def set_env_variable(self, env_var, env_val):
        """
        Description: Set CANoe Environment value
        :param env_var, environment variable name
        :param env_val, environment variable value
        :return int
        """
        self.__setEnvVar(env_var, int(env_val))
        logger.info("OK! Set CANoe Env {} to int {}".format(env_var, env_val))

    def get_env_variable(self, env_var):
        """
        Description: Set CANoe Environment value
        :param env_var, environment variable name
        :return int
        """
        env_val = self.__getEnvVar(env_var)
        logger.info("OK! Get CANoe Env {} with int {}".format(env_var, env_val))
        return env_val

    def set_sys_variable(self, sys_ns, sys_var, sys_val):
        """
        Description: Set CANoe Environment value
        :param sys_ns, system name space
        :param sys_var, system variable name
        :param sys_val, system variable value
        :return int
        """
        try:
            self.__setSysVar(sys_ns, sys_var, int(sys_val))
            logger.info(
                "OK! Set CANoe system {}::{} to int {}".format(sys_ns, sys_var, sys_val)
            )
        except:
            logger.error(f"Error! Set CANoe system variable {sys_var} value {sys_val}")

    def get_sys_variable(self, sys_ns, sys_var):
        """
        Description: Set CANoe Environment value
        :param sys_ns, system name space
        :param sys_var, system variable name
        :return int
        """
        sys_val = self.__getSysVar(sys_ns, sys_var)
        logger.info(
            "OK! Get CANoe system {}::{} with int {}".format(sys_ns, sys_var, sys_val)
        )
        return sys_val

    def set_signal(self, msg, sig_name, sig_val, bus_type="CAN", bus_index=1):
        """
        Description: Set CANoe signal value
        :param msg message name
        :param sig_name signal name
        :param sig_val signal value
        :param bus_type bus name CAN, LIN ...
        :param bus_index bus idnex default is 1
        :return int
        """
        try:
            self.__setSigVal(msg, sig_name, sig_val, bus_type, bus_index)
            logger.info(
                f"OK! Set signal msg {msg} signal {sig_name} value {sig_val} bus_type {bus_type} bus_index {bus_index}"
            )
        except:
            logger.error(
                f"Error! Set signal msg {msg} signal {sig_name} value {sig_val} bus_type {bus_type} bus_index {bus_index}"
            )

    def get_signal(self, msg, sig_name, bus_type="CAN", bus_index=1):
        """
        Description: Set CANoe signal value
        :param msg message name
        :param sig_name signal name
        :param bus_type bus name CAN, LIN ...
        :param bus_index bus idnex default is 1
        :return int
        """
        sig_val = self.__getSigVal(msg, sig_name, bus_type, bus_index)
        logger.info(
            f"OK! Get signal msg {msg} signal {sig_name} bus_type {bus_type} bus_index {bus_index} with value {sig_val}"
        )
        return sig_val

    def set_can_variable(self, dKey2Set=None):
        """
        Description: Set the Env. Sys, or signal value to CAN network
        :param "key2set", the key name defined in "/Config/CanDefinition.xml"
        :return Res, int
        """
        key_type = dKey2Set["type"]
        if key_type == "sys":
            key_ns = dKey2Set["namespace"]
            key_var = dKey2Set["var"]
            key_val = dKey2Set["value"]
            self.set_sys_variable(key_ns, key_var, key_val)
        elif key_type == "signal":
            key_msg = dKey2Set["msg"]
            key_sig = dKey2Set["sig"]
            key_val = dKey2Set["value"]
            key_channel = dKey2Set["channel"]
            key_bustype = dKey2Set["bustype"]
            self.set_signal(key_msg, key_sig, key_val, key_bustype, key_channel)
        elif key_type == "env":
            key_name = dKey2Set["var"]
            key_val = dKey2Set["value"]
            self.set_env_variable(key_name, key_val)

    def get_can_variable(self, dKey2Set=None):
        """
        Description: Get the Env. Sys, or signal value from CAN network
        :param "key2set", the key name defined in "/Config/CanDefinition.xml"
        :return Res, int
        """
        key_type = dKey2Set["type"]
        if key_type == "sys":
            key_ns = dKey2Set["namespace"]
            key_var = dKey2Set["var"]
            nValue = self.get_sys_variable(key_ns, key_var)
        elif key_type == "signal":
            key_msg = dKey2Set["msg"]
            key_sig = dKey2Set["sig"]
            key_channel = dKey2Set["channel"]
            key_bustype = dKey2Set["bustype"]
            nValue = self.get_signal(key_msg, key_sig, key_bustype, key_channel)
        elif key_type == "env":
            key_name = dKey2Set["var"]
            nValue = self.set_env_variable(key_name)

        return int(nValue)

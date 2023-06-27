import serial
from loguru import logger


class RelayHelper:
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self):
        self.dev_enabled = None
        self.cleware_batch = None
        self.cleware_id = None
        self.mcube_comport = None
        self.xinke_comport = None
        self.multiplexer_comport = None
        self.mcube_mode = None

    def init_relay(self, drelay):
        self.dev_enabled = drelay["relay_enabled"]
        device_count = 0
        if not self.dev_enabled:
            logger.warning("[Relay] No relay enabled this execution !")
            return

        if "xinke" in drelay.keys():
            if drelay["xinke"]["enabled"]:
                device_count += 1
                self.xinke_comport = drelay["xinke"]["comport"].upper()
                logger.info("[Relay.Xinke] Xinke controller initialized")
            else:
                logger.info("xinke not enabled,skip")

        if "multiplexer" in drelay.keys():
            if drelay["multiplexer"]["enabled"]:
                device_count += 1
                self.multiplexer_comport = drelay["multiplexer"]["comport"].upper()
                logger.info("[Relay.Multiplexer] Multiplexer controller initialized")
            else:
                logger.info("multiplexer not enabled,skip")

        if device_count == 0:
            logger.error("Error! No valid relay set!")

    def __set_xinke_port(self, port_index, state_code, xinke_type="KBC2105"):
        """
        Description: Set the Xinke relay box port, close=1 |  open=0
        :param "serial_port" the xinke relay serial port
        :param "port_index" the xinke relay port to be controlled
        :param "state_code" the xinke relay port state to be "0 | 1 | ALLON | ALLOFF"
        """
        funcCode = {"OFF": 0x11, "ON": 0x12, "ALLOFF": 0x14, "ALLON": 0x13}
        if xinke_type == "KBC2104":
            sendHead = 0x55
        else:
            sendHead = 0x33

        addrCode = 0x01
        preDataSection = [0x00, 0x00, 0x00]
        state_code = str(state_code).strip()
        state_code = state_code.upper()
        if state_code not in ["1", "0", "ALLOFF", "ALLON"]:
            logger.error("[XinkeRelay] INVALID state code assigned, '{state_code}' !")
            return
        if state_code == "ALLOFF" or state_code == "ALLON":
            nextDataSection = 0x00
            cmd_key = state_code
        elif state_code == "1":
            cmd_key = "ON"
            nextDataSection = int(str(port_index), 16)
        else:
            cmd_key = "OFF"
            nextDataSection = int(str(port_index), 16)

        # Start send command
        obj_xinke = None
        cmdList = []
        try:
            obj_xinke = serial.Serial(
                self.xinke_comport,
                baudrate=9600,
                bytesize=8,
                parity="N",
                stopbits=1,
                timeout=0.5,
            )
            if obj_xinke.isOpen() is False:
                logger.error(
                    f"[SetXinke] Fail to open xinke serial port={self.xinke_comport} !"
                )
                return
            cmdList.append(sendHead)
            cmdList.append(addrCode)
            cmdList.append(funcCode[cmd_key])
            cmdList = cmdList + preDataSection
            cmdList.append(nextDataSection)
            cmdList.append(sum(cmdList[0:7]) % 256)
            obj_xinke.write(cmdList)
            obj_xinke.flush()
            logger.success(
                f"[SetXinke] Succeed to open xinke serial port={port_index}, state_code={state_code}"
            )
        except:
            logger.error(
                f"[SetXinke] Exception set xinke "
                f"port {self.xinke_comport}, {port_index}, {state_code}"
            )
        finally:
            obj_xinke.close()

    def __set_multiplexer_port(self, port_index=None):
        """
        Description: This is mcube function entry for relay controlling
        :param "port_index" Candidate command is the keys of dict => multiplexer_map
        """
        obj_multiplexer = None
        multiplexer_map = {
            "11": [0x01, 0x01],  # In-1, Out-1
            "12": [0x01, 0x02],  # In-1, Out-2
            "13": [0x01, 0x03],  # In-1, Out-3
            "14": [0x01, 0x04],  # In-1, Out-4
            "21": [0x02, 0x01],  # In-2, Out-1
            "22": [0x02, 0x02],  # In-2, Out-2
            "23": [0x02, 0x03],  # In-2, Out-3
            "24": [0x02, 0x04],  # In-2, Out-4
            "30": [0x03, 0x00],  # Power relay 1, Off
            "31": [0x03, 0x01],  # Power relay 1, On
            "40": [0x04, 0x00],  # Power relay 2, Off
            "41": [0x04, 0x01],  # Power relay 2, On
            "50": [0x05, 0x00],  # Voltage ADC
            "f0": [0x0F, 0x00],  # MCU reset
            "f1": [0x0F, 0x01],  # USB In-Out selftest
            "f2": [0x0F, 0x02],  # Get device serial number
            "f3": [0x0F, 0x03],  # Get FW version
            "f4": [0x0F, 0x04],  # Get current IO state
        }

        try:
            time_out = 2 if port_index != "f1" else 10
            obj_multiplexer = serial.Serial(
                self.multiplexer_comport,
                baudrate=9600,
                bytesize=8,
                parity="N",
                stopbits=1,
                timeout=time_out,
            )
            if not obj_multiplexer.isOpen():
                logger.error(
                    f"[Set-Multiplexer] Fail to open multiplexer serial port={self.multiplexer_comport} !"
                )
                return

            port_index = str(port_index)
            if port_index not in multiplexer_map:
                logger.error(
                    f"[Error] Not found port_index={port_index} in multiplexer definition !"
                )
                return

            hexCmdList = list()
            cmdhead = [0x24]
            cmdtail = [0x24, 0x0D, 0x0A]
            cmdpayload = multiplexer_map[port_index]

            hexCmdList.extend(cmdhead)
            hexCmdList.extend(cmdpayload)
            hexCmdList.extend(cmdtail)
            obj_multiplexer.write(hexCmdList)
            obj_multiplexer.flush()

        except Exception as err:
            logger.exception(
                f"Unable to open multiplexer port {self.multiplexer_comport}"
            )

        finally:
            obj_multiplexer.close()

    def set_relay_port(self, dev_type=None, **kwargs):
        """
        Description: This is generic function entry for relay controlling
        :param "dev_type" This parameter is used to distinguish which relay type to be worked on
        :param "kwargs" the respective relay device parameters
        :return
        """
        if dev_type == None:
            logger.error("NOK! dev type should be defined!")
            return
        dev_type = dev_type.lower()

        if dev_type == "xinke":
            return self.__set_xinke_port(**kwargs)

        if dev_type == "multiplexer":
            return self.__set_multiplexer_port(**kwargs)


if __name__ == "__main__":
    obj_relay = RelayHelper()
    drelay = {
        "relay_enabled": True,
        "multiplexer": {"enabled": False, "comport": "COM13"},
        "cleware": {"enabled": False, "dev_id": "710452"},
        "xinke": {"enabled": False, "comport": "COM10"},
        "mcube": {"enabled": True, "comport": "COM15", "run_mode": "2*4"},
    }
    obj_relay.init_relay(drelay)
    obj_relay.set_relay_port(dev_type="mcube", port_index="1")

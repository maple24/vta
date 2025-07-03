# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

import os
import serial
from contextlib import contextmanager
from functools import wraps
from loguru import logger
from typing import Union

ROOT = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-3])


def safe_relay_operation(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"[{func.__name__}] Exception: {e}")
    return wrapper

@contextmanager
def open_serial_port(port: str, baudrate: int, timeout: float, **kwargs) -> serial.Serial:
    ser = serial.Serial(port, baudrate=baudrate, timeout=timeout, **kwargs)
    try:
        yield ser
    finally:
        if ser.is_open:
            ser.close()

class RelayHelper:
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self) -> None:
        # Initialize relay controller attributes with type hints.
        self.dev_enabled: bool = False
        self.cleware_executor: str = ""
        self.xinke_comport: str = ""
        self.multiplexer_comport: str = ""
        self.cleware_id: str = ""

    def init_relay(self, drelay: dict) -> None:
        # Initialize relay devices based on configuration using dict.get for clarity.
        self.dev_enabled = drelay.get("relay_enabled", False)
        device_count = 0
        if not self.dev_enabled:
            logger.warning("[Relay] No relay enabled for this execution!")
            return

        if drelay.get("xinke", {}).get("enabled", False):
            device_count += 1
            self.xinke_comport = drelay["xinke"]["comport"].upper()
            logger.info("[Relay.Xinke] Xinke controller initialized")

        if drelay.get("multiplexer", {}).get("enabled", False):
            device_count += 1
            self.multiplexer_comport = drelay["multiplexer"]["comport"].upper()
            logger.info("[Relay.Multiplexer] Multiplexer controller initialized")

        if drelay.get("cleware", {}).get("enabled", False):
            device_count += 1
            self.cleware_executor = os.path.join(
                ROOT, "vta", "bin", "cleware", "USBswitchCmd.exe"
            )
            logger.info(f"[Relay.Cleware] Cleware executor found at {self.cleware_executor}")
            if not os.path.exists(self.cleware_executor):
                logger.error("[Relay.Cleware] Cleware executor not found!")
                exit(1)
            self.cleware_id = drelay["cleware"].get("dev_id", "")
            logger.info("[Relay.Cleware] Cleware controller initialized")

        if device_count == 0:
            logger.warning("No valid relay device set!")

    @safe_relay_operation
    def __set_xinke_port(self, port_index: Union[int, str], state_code: Union[int, str], xinke_type: str = "KBC2105") -> None:
        """
        Set the Xinke relay port.
        :param port_index: Relay port index to control.
        :param state_code: Relay state ("1"/"0" or "ALLON"/"ALLOFF").
        :param xinke_type: Type of Xinke device.
        """
        func_code = {"OFF": 0x11, "ON": 0x12, "ALLOFF": 0x14, "ALLON": 0x13}
        send_head = 0x55 if xinke_type == "KBC2104" else 0x33
        addr_code = 0x01
        pre_data = [0x00, 0x00, 0x00]
        state_str = str(state_code).strip().upper()
        if state_str not in ["1", "0", "ALLOFF", "ALLON"]:
            logger.error(f"[XinkeRelay] INVALID state code: '{state_str}'!")
            return

        cmd_key = "ALLON" if state_str in ["ALLON", "ALLOFF"] else ("ON" if state_str == "1" else "OFF")
        next_data = 0x00 if state_str in ["ALLON", "ALLOFF"] else int(str(port_index), 16)

        cmd_list = [send_head, addr_code, func_code[cmd_key]] + pre_data + [next_data]
        checksum = sum(cmd_list[0:7]) % 256
        cmd_list.append(checksum)

        with open_serial_port(self.xinke_comport, baudrate=9600, timeout=0.5, bytesize=8, parity="N", stopbits=1) as ser:
            if not ser.is_open:
                logger.error(f"[SetXinke] Failed to open serial port {self.xinke_comport}!")
                return
            ser.write(bytearray(cmd_list))
            ser.flush()
            logger.success(f"[SetXinke] Successfully set port {port_index} with state {state_str}")

    @safe_relay_operation
    def __set_multiplexer_port(self, port_index: Union[int, str]) -> None:
        """
        Set the Multiplexer relay port.
        :param port_index: Relay port index (as defined in multiplexer_map).
        """
        multiplexer_map = {
            "11": [0x01, 0x01], "12": [0x01, 0x02], "13": [0x01, 0x03], "14": [0x01, 0x04],
            "21": [0x02, 0x01], "22": [0x02, 0x02], "23": [0x02, 0x03], "24": [0x02, 0x04],
            "30": [0x03, 0x00], "31": [0x03, 0x01],
            "40": [0x04, 0x00], "41": [0x04, 0x01],
            "50": [0x05, 0x00],
            "f0": [0x0F, 0x00], "f1": [0x0F, 0x01], "f2": [0x0F, 0x02], "f3": [0x0F, 0x03], "f4": [0x0F, 0x04],
        }
        port_str = str(port_index)
        if port_str not in multiplexer_map:
            logger.error(f"[Multiplexer] Invalid port index: {port_str} not in definition!")
            return

        cmd_head = [0x24]
        cmd_tail = [0x24, 0x0D, 0x0A]
        cmd_payload = multiplexer_map[port_str]
        cmd_list = cmd_head + cmd_payload + cmd_tail

        timeout_val = 10 if port_str == "f1" else 2
        with open_serial_port(self.multiplexer_comport, baudrate=9600, timeout=timeout_val, bytesize=8, parity="N", stopbits=1) as ser:
            if not ser.is_open:
                logger.error(f"[Multiplexer] Failed to open serial port {self.multiplexer_comport}!")
                return
            ser.write(bytearray(cmd_list))
            ser.flush()
            logger.success(f"[Multiplexer] Command sent for port {port_str}")

    @safe_relay_operation
    def _set_cleware_port(self, port_index: int, state_code: Union[int, str]) -> None:
        """
        Set the Cleware relay port.
        :param port_index: Relay port number (1 to 8).
        :param state_code: Port state ("0" or "1").
        """
        if not self.cleware_id:
            logger.error("[Cleware] Invalid Cleware ID!")
            return

        state_str = str(state_code).strip()
        if state_str not in ["0", "1"]:
            logger.error(f"[Cleware] Invalid state code: '{state_str}'!")
            return

        cmd = f"cmd.exe /c {self.cleware_executor} -n {self.cleware_id} {state_str} -# {port_index - 1} -d"
        os.system(cmd)
        logger.info(f"[Cleware] Set Cleware ID={self.cleware_id}, port={port_index}, state={state_str}")

    def set_relay_port(self, dev_type: str, **kwargs) -> None:
        """
        Generic method for relay control.
        :param dev_type: Relay device type ("xinke", "multiplexer", "cleware").
        :param kwargs: Specific parameters for the relay device.
        """
        dev_type = dev_type.lower()
        if dev_type == "xinke":
            return self.__set_xinke_port(**kwargs)
        elif dev_type == "multiplexer":
            return self.__set_multiplexer_port(**kwargs)
        elif dev_type == "cleware":
            return self._set_cleware_port(**kwargs)
        else:
            logger.error("Invalid device type specified for relay control!")


if __name__ == "__main__":
    obj_relay = RelayHelper()
    drelay = {
        "relay_enabled": True,
        "multiplexer": {"enabled": False, "comport": "COM13"},
        "cleware": {"enabled": False, "dev_id": "710452"},
        "xinke": {"enabled": True, "comport": "COM5"},
    }
    obj_relay.init_relay(drelay)
    obj_relay.set_relay_port(dev_type="xinke", port_index="1", state_code="1")
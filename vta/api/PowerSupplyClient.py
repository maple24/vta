import serial
from loguru import logger
from contextlib import contextmanager
from typing import Dict, Any, Generator, Optional


class PowerSupplyClient:
    ROBOT_LIBRARY_SCOPE: str = "GLOBAL"

    def __init__(self) -> None:
        self.obj_pps: Optional[serial.Serial] = None
        self.pps_enabled: bool = False

    def init_pps(self, dPPS: Dict[str, Any]) -> None:
        self.pps_enabled = dPPS["pps_enabled"]
        if not self.pps_enabled:
            logger.warning("[PPS] PPS disabled, skip initiating")
        logger.info("[PPS] Start initiating PPS ...")
        self.pps_port_name: str = dPPS["pps_comport"]
        self.pps_baudrate: int = int(dPPS["pps_baudrate"])
        self.pps_ctrl_channel: int = int(dPPS["pps_channel_used"])

    def _open_connection(self) -> None:
        self.obj_pps = serial.Serial(self.pps_port_name, self.pps_baudrate, timeout=2)
        if self.obj_pps.isOpen():
            self.obj_pps.close()
        self.obj_pps.open()

    def _close_connection(self) -> None:
        if self.obj_pps and self.obj_pps.isOpen():
            self.obj_pps.close()

    def _read_value(self) -> float:
        val: bytes = self.obj_pps.readline()
        decoded: str = val.decode("utf-8").strip()
        return -1.0 if decoded == "" else float(decoded)

    def _set_volt_scpi(self, volt: float, channel: int) -> None:
        self._open_connection()
        self.send_command(":INST:NSEL {};:VOLT {}".format(channel, volt))
        self._close_connection()

    def send_command(self, cmd: str) -> None:
        if not cmd.endswith("\n"):
            cmd += "\n"
        self.obj_pps.write(cmd.encode("utf-8"))
        self.obj_pps.flush()

    @contextmanager
    def _serial_connection(self) -> Generator[None, None, None]:
        if not self.pps_enabled:
            raise RuntimeError("PPS is disabled.")
        self._open_connection()
        try:
            yield
        finally:
            self._close_connection()

    def set_volt(self, volt: float, channel: int = -1) -> None:
        channel = self.pps_ctrl_channel if channel == -1 else channel
        try:
            with self._serial_connection():
                self.send_command(":INST:NSEL {};:VOLT {}".format(channel, volt))
                logger.info("Set PPS channel {} voltage to {}V", channel, volt)
        except Exception as e:
            logger.error("Error setting voltage: {}", e)

    def get_volt(self, channel: int = -1) -> float:
        volt: float = -1.0
        channel = self.pps_ctrl_channel if channel == -1 else channel
        try:
            with self._serial_connection():
                self.send_command(":INST:NSEL {};:MEAS:VOLT?".format(channel))
                data: float = self._read_value()
                volt = -1.0 if data is None else float(data)
                logger.info("Get PPS channel {} voltage {}V", channel, volt)
        except Exception as e:
            logger.error("Error getting voltage: {}", e)
        finally:
            return volt

    def get_current(self, channel: int = -1) -> float:
        current: float = -1.0
        channel = self.pps_ctrl_channel if channel == -1 else channel
        try:
            with self._serial_connection():
                self.send_command(":INST:NSEL {};:MEAS:CURR?".format(channel))
                data: float = self._read_value()
                current = -1.0 if data is None else float(data)
                logger.info("Get PPS channel {} current {}A", channel, current)
        except Exception as e:
            logger.error("Error getting current: {}", e)
        finally:
            return current


if __name__ == "__main__":
    dPPS: Dict[str, Any] = {
        "pps_enabled": True,
        "pps_comport": "COM16",
        "pps_baudrate": 9600,
        "pps_channel_used": 1,
    }
    mpps = PowerSupplyClient()
    mpps.init_pps(dPPS=dPPS)
    mpps.get_volt()
    mpps.get_current()
    mpps.set_volt(12.0)

import re
import sys
import os
from typing import Optional, List
from loguru import logger
import time
import csv
import random

sys.path.append(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-4]))

from vat.library.PuttyHelper import PuttyHelper
from vat.library.CANoeHelper import CANoeHelper
from vat.library.GenericHelper import GenericHelper


class Vehicle:
    def __init__(self, dputty: dict, proto: str = "", canoe: bool = False) -> None:
        self.mputty = PuttyHelper()
        self.mcanoe = CANoeHelper()
        self.mcanoe.init_canoe(canoe)
        self.mputty.connect(dputty)
        self.proto = proto

    @staticmethod
    def get_proto_id(file: str, signal: str) -> Optional[str]:
        if not os.path.exists(file):
            logger.error("Proto file not found!")
            sys.exit(1)
        pattern = f"{signal}\s+=\s+(.*);"
        with open(file, "r") as f:
            lines = f.readlines()
        for line in lines:
            match = re.search(pattern, line)
            if match:
                return match.groups()[0]
        return None

    @staticmethod
    def csv2dict(file: str) -> List[dict]:
        rows = []
        with open(file) as f:
            reader = csv.DictReader(f, delimiter=",")
            for row in reader:
                rows.append(row)
        return rows

    def write(self, id: str, msg: str, sig: str) -> None:
        value = random.choice(["0", "1"])
        logger.info(
            f"Write signal. ID: {id} | Msg: {msg} | Sig: {sig} | Value: {value}"
        )
        # send signal from qnx
        res, _ = self.mputty.wait_for_trace(
            pattern="(vehicle_proxy_send_message success)",
            cmd=f"/shared/vehicle_test {id} {value}",
        )
        if not res:
            logger.error(f"Fail to send signal! ID: {id} | Value: {value}")
            sys.exit(1)
        logger.success("Succeed to send signal!")
        self.mputty.send_command("\x03")
        time.sleep(0.5)

        # read from canoe
        val = self.mcanoe.get_signal(msg, sig, bus_type="FlexRay")
        if float(val) != float(value):
            logger.error(
                f"Signal value does not match! Get: {val} | Send: {value} | Msg: {msg} | Sig: {sig}"
            )
            sys.exit(1)
        logger.success("Signal value is matched!")

    def read(self, ub: str, msg: str, sig: str) -> None:
        self.mputty.enable_monitor()
        # send signal from canoe
        value = self.mcanoe.get_signal(msg, sig, bus_type="FlexRay")
        if float(value) == 0:
            value = "1"
        else:
            value = "0"
        logger.info(f"Send signal. UB: {ub} | Msg: {msg} | Sig: {sig} | Value: {value}")
        self.mcanoe.set_signal(msg, ub, "1", bus_type="FlexRay")
        self.mcanoe.set_signal(msg, sig, value, bus_type="FlexRay")

        # read from qnx
        time.sleep(0.5)
        traces = self.mputty.get_trace_container()
        res, _ = GenericHelper.match_string(
            pattern="(signal message send)", data=traces
        )
        if not res:
            logger.error(
                f"Fail to receive signal! Msg: {msg} | Sig: {sig} | Value: {value}"
            )
            sys.exit(1)
        logger.success(
            f"Succeed to receive signal! Msg: {msg} | Sig: {sig} | Value: {value}"
        )
        self.mputty.disable_monitor()

    def run(self, row: dict) -> None:
        ACCESS = row.get("ACCESS")
        GROUP = row.get("SigGroup")
        MSG = row.get("Msg")

        if ACCESS == "READ":
            SIG = row.get("Rx")
            if GROUP:
                ub = GROUP + "_UB"
            else:
                ub = SIG + "_UB"
            self.read(ub, MSG, SIG)
        elif ACCESS == "WRITE":
            ID = Vehicle.get_proto_id(self.proto, row.get("SigID"))
            SIG = row.get("Tx")
            self.write(ID, MSG, SIG)
        else:
            logger.error("Error access type!")
            sys.exit(1)


if __name__ == "__main__":
    proto = 'com.platform.vehicle.proto'

    dputty = {
        "putty_enabled": True,
        "putty_comport": "COM11",
        "putty_baudrate": 115200,
        "putty_username": "root",
        "putty_password": "6679836772",
    }
    mv = Vehicle(dputty, canoe=True, proto=os.path.join(os.path.dirname(__file__), proto))
    # mv.read(
    #     ub="DstEstimdToEmptyForDrvgElec_UB",
    #     msg="VDDMBackBoneSignalIPdu16",
    #     sig="DstEstimdToEmptyForDrvgElec",
    # )

    # mv.write(
    #     id='16159',
    #     msg='IHUBackBoneSignalIPdu08',
    #     sig='HmiDefrstElecReqFrntElecReq',
    # )
    row = {
        "SigID": "DRIVEINFO_DSTESTIMDTOEMPTYFORDRVGELEC",
        "Msg": "VDDMBackBoneSignalIPdu16",
        "SigGroup": "",
        "ACCESS": "READ",
        "Rx": "DstEstimdToEmptyForDrvgElec",
        "Tx": "",
    }
    row = {
        "SigID": "DRIVEINFO_AUDWARNACTV",
        "Msg": "DIMBackBoneSignalIPdu08",
        "SigGroup": "",
        "ACCESS": "WRITE",
        "Rx": "",
        "Tx": "AudWarnActv",
    }
    mv.run(row)

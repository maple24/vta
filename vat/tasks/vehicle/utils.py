import re
import sys
import os
from typing import Optional
from loguru import logger
import time
sys.path.append(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-4]))

from vat.library.PuttyHelper import PuttyHelper
from vat.library.CANoeHelper import CANoeHelper
from vat.library.GenericHelper import GenericHelper


class Vehicle:
    
    def __init__(self, dputty: dict, canoe: bool = False) -> None:
        self.mputty = PuttyHelper()
        self.mcanoe = CANoeHelper()
        self.mcanoe.init_canoe(True)
        self.mputty.connect(dPutty=dputty)
    
    @staticmethod
    def get_proto_id(file: str, signal: str) -> Optional[str]:
        pattern = f'{signal}\s+=\s+(.*);'
        with open(file, 'r') as f:
            lines = f.readlines()
        for line in lines:
            match = re.search(pattern, line)
            if match:
                return match.groups()[0]
        return None

    @staticmethod
    def parse_excel(file: str):
        ...

    def write(self, id: str, value: str, msg, sig) -> None:
        # send signal from qnx
        res, _ = self.mputty.wait_for_trace(pattern='(vehicle_proxy_send_message success)', cmd=f'./shared/vehicle_test {id} {value}')
        if not res:
            logger.error(f"Fail to send signal! ID: {id} | Value: {value}")
            sys.exit(1)
        logger.success("Success to send signal!")
        self.mputty.send_command('\x03')
        
        # read from canoe
        val = self.mcanoe.get_signal(msg, sig, bus_type='FlexRay')
        if val != value:
            logger.error(f"Signal value does not match! Get: {val} | Send: {value} | Msg: {msg} | Sig: {sig}")
            sys.exit(1)
        logger.success("Signal value is matched!")

            
    def read(self, ub: str, msg: str, sig: str, value: str) -> None:
        self.mputty.enable_monitor()
        # send signal from canoe
        self.mcanoe.set_signal(ub, sig, 1, bus_index='FlexRay')
        self.mcanoe.set_signal(msg, sig, value, bus_index='FlexRay')
        
        # read from qnx
        time.sleep(0.5)
        traces = self.mputty.get_trace_container()
        res, _ = GenericHelper.match_string(pattern='(signal message send)', data=traces)
        if not res:
            logger.error(f"Fail to receive signal! Msg: {msg} | Sig: {sig} | Value: {value}")
            sys.exit(1)
        logger.info(f"Success to receive signal! Msg: {msg} | Sig: {sig} | Value: {value}")
        self.mputty.disable_monitor()
        

if __name__ == '__main__':
    # file = 'com.platform.vehicle.proto'
    # signal_name = 'HVAC_HMIFRAGRAMODREQ'
    
    # print(Vehicle.get_proto_id(os.path.join(os.path.dirname(__file__), file), 'HVAC_HMIFRAGRAMODREQ'))
    dputty = {
        "putty_enabled": True,
        "putty_comport": "COM4",
        "putty_baudrate": 115200,
        "putty_username": "root",
        "putty_password": "6679836772",
    }
    mv = Vehicle(dputty, True)
    mv.read(
        ub='DstEstimdToEmptyForDrvgElec_UB', 
        msg='VDDMBackBoneSignalIPdu16',
        sig='DstEstimdToEmptyForDrvgElec',
        value='1')

    mv.write(
        id='27444',
        msg='VDDMBackBoneSignalIPdu16',
        sig='DstEstimdToEmptyForDrvgElec',
        value='0'
    )
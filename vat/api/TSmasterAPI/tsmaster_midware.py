"""A midware for TSMaster tool Flexray API

This is a draft version, just for simple demo
Flexray API of TSMaster is still under development by now

Only support channel id: 0, channel mask: 1
"""
__all__ = ["MidwareException", "TsmasterMidware"]
__author__ = "usy2wx"

import time
from os.path import basename
from ctypes import c_bool, c_int8, c_uint8, c_int, c_uint, c_size_t
from xml.etree.ElementTree import ParseError

from libTOSUNv2 import (
    TLIBFlexray,
    TLibFlexray_controller_config,
    TLibTrigger_def,
    initialize_lib_tsmaster,
    tsapp_connect,
    tsflexray_set_controller_frametrigger,
    tsflexray_start_net,
    tsflexray_stop_net,
    tsfifo_clear_flexray_receive_buffers,
    tsfifo_receive_flexray_msgs,
    tsflexray_transmit_sync,
    tsapp_disconnect_AHandle,
)
from lib_flexray_xml import PersistentFlexrayDatabase, FlexrayDatabaseException


FRAME_MAX_DATA_LENGTH = 254  # Unit: bytes
FRAME_DEFAULT_DATA_LENGTH = 32  # Unit: bytes
TS_TIMEOUT_MS = c_int(1000)  # Unit: ms
RECV_BUFFER_SIZE = 256


def _logger(*value: object) -> None:
    print(f"[{basename(__file__)}] ", end="")
    print(*value)


class MidwareException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TsmasterMidwareBase:
    """Basic class of Tsmaster midware

    start, stop or send Flexray message
    """

    def __init__(self, database: str):
        """__init__

        :param str database: Flexray database XML file path
        """
        try:
            self.db = PersistentFlexrayDatabase(database)
        except (FileNotFoundError, ParseError, FlexrayDatabaseException) as error:
            raise MidwareException(f"Failed to initialize flexray database: {error}")
        _logger("Succeeded to initialize FlexrayDatabase")

        # handler of TSMaster low layer API
        self.tsapp_handler = c_size_t(0)

        print("**************")
        print(self.tsapp_handler)

    def do_init(self):
        """Initialization of TSMaster API

        A handler for manipulate TSMaster behavior

        :raises MidwareException: When failed to connect TSMaster
        """
        initialize_lib_tsmaster(c_bool(True), c_bool(True))

        if tsapp_connect(b"", self.tsapp_handler) != 0:
            raise MidwareException("Failed to connect tsmaster")
        _logger("Succeeded to connect TSMaster")

        fr_config = TLibFlexray_controller_config(
            is_open_a=True, is_open_b=False, enable100_b=False, is_show_nullframe=False
        )

        ret = tsflexray_set_controller_frametrigger(
            self.tsapp_handler,
            c_uint(0),
            fr_config,
            (c_int * 3)(32),
            c_int(1),
            TLibTrigger_def(slot_id=1, cycle_code=1),
            c_int(1),
            TS_TIMEOUT_MS,
        )

        if ret != 0:
            _logger(
                f"Warning: return code of tsflexray_set_controller_frametrigger: {ret}"
            )
        _logger("Succeeded to initialize Flexray controller of TSMaster")

    def do_deinit(self):
        """Release handler of TSMaster"""
        ret = tsapp_disconnect_AHandle(self.tsapp_handler)
        _logger(f"Invoked tsapp_disconnect_AHandle() with return value: {ret}")

    def start(self):
        """Click "Start" button of TSMaster"""
        time.sleep(0.1)
        ret = tsflexray_start_net(self.tsapp_handler, c_int(0), TS_TIMEOUT_MS)
        _logger(f"Invoked tsflexray_start_net() with return value: {ret}")
        time.sleep(0.1)

    def stop(self):
        """Click "Stop" button of TSMaster"""
        ret = tsflexray_stop_net(self.tsapp_handler, c_int(0), TS_TIMEOUT_MS)
        _logger(f"Invoked tsflexray_stop_net() with return value: {ret}")
        time.sleep(0.1)

    def get_tx_frame_data(
        self, slot_id: int, base_cycle: int, cycle_repetition: int
    ) -> list[int]:
        """Get current frame TX raw data from flexray bus

        :param int slot_id: Specific slot id
        :param int base_cycle: Specific base cycle
        :return list[int]: Actual raw data, chunked according to ActualPayloadLength
        """
        tsfifo_clear_flexray_receive_buffers(self.tsapp_handler, c_int(0))
        time.sleep(0.005 * 64)  # 5ms * 64 cycle
        recv_buffer = (TLIBFlexray * RECV_BUFFER_SIZE)()
        tsfifo_receive_flexray_msgs(
            self.tsapp_handler,
            recv_buffer,
            c_int(RECV_BUFFER_SIZE),
            c_int(0),
            c_int8(1),
        )

        for frame in recv_buffer:
            if frame.FDir == 0:
                # RX, ignore
                continue

            if frame.FSlotId != slot_id:
                continue

            if frame.FCycleNumber % cycle_repetition == base_cycle:
                valid_data = frame.FData[: frame.FActualPayloadLength]
                return valid_data
        else:
            _logger(
                f"No TX frame, slot: {slot_id}, base: {base_cycle}, rep: {cycle_repetition}"
            )
            return []

    def change_signal(self, signal_name: str, signal_value: int) -> int:
        """Change the specific bits on Flexray bus

        Capture current TX frame of slot, modify frame data by bits operation
        Send it to Flexray bus

        Potential Issue:
            Bit order is always use "HIGH-LOW-BYTE-ORDER"

        :param str signal_name: Standard signal name
        :param int signal_value: New value to change
        :return int: Return value from TOSUN low layer API, -1 if failed
        """
        return self.change_single_frame_signals({signal_name: signal_value})

    def change_single_channel_signals(self, signal_name_value_pairs: dict[str, int]):
        """Change signals in one channel

        It's *Undefined Behavior* if duplicated signal name

        Know Issue: can't send VDDM signal

        :param dict[str, int] signal_name_value_pairs: signal name, value pairs
        """
        #
        # {
        #     (slot_id: 0, base_cycle: 0, base_repetition: 1): {
        #         signal_name: value,
        #         signal_name: value
        #     },
        #     (slot_id: 1, base_cycle: 4, base_repetition: 1): {
        #         signal_name: value
        #     }
        #     ...
        # }
        signal_name_value_groups: dict[tuple[int, int, int], dict[str, int]] = {}
        for signal_name, signal_value in signal_name_value_pairs.items():
            signal_info_po = self.db.get_signal_info_po_by_name(signal_name)
            if signal_info_po is None:
                _logger(f"Failed to get signal info PO by name: {signal_name}")
                _logger(f"Value of {signal_name} will not be updated")
                continue

            frame_triggering_tuple = (
                signal_info_po.slot_id,
                signal_info_po.base_cycle,
                signal_info_po.cycle_repetition,
            )
            if frame_triggering_tuple not in signal_name_value_groups:
                signal_name_value_groups[frame_triggering_tuple] = {}
            signal_name_value_groups[frame_triggering_tuple][signal_name] = signal_value

        for signal_name_value_pairs in signal_name_value_groups.values():
            self.change_single_frame_signals(signal_name_value_pairs)

    def change_single_frame_signals(
        self, signal_name_value_pairs: dict[str, int]
    ) -> int:
        """Change signals in one frame

        Know Issue: can't send VDDM signal

        :param dict[str, int] signal_name_value_pairs: signal name, value pairs
        :return int: Return value from TOSUN low layer API, -1 if failed
        """
        if not signal_name_value_pairs:
            return 0

        # Get one signal name, then get the slot id, base_cycle
        # Code here is ugly
        slot_id = -1
        base_cycle = -1
        cycle_repetition = -1
        for signal_name in signal_name_value_pairs.keys():
            signal_info_po = self.db.get_signal_info_po_by_name(signal_name)
            if signal_info_po is None:
                continue

            slot_id = signal_info_po.slot_id
            base_cycle = signal_info_po.base_cycle
            cycle_repetition = signal_info_po.cycle_repetition
            break
        else:
            _logger("Failed to get slot id, abort")
            return -1

        # Capture current TX frame sent by TSMaster
        tx_frame_data: list[int] = []
        for _ in range(3):
            tx_frame_data = self.get_tx_frame_data(
                slot_id=slot_id,
                base_cycle=base_cycle,
                cycle_repetition=cycle_repetition,
            )
            if tx_frame_data:
                break
            time.sleep(1)
        else:
            _logger("Warning: Failed to get current TX frame")
            tx_frame_data = [0] * FRAME_DEFAULT_DATA_LENGTH

        if len(tx_frame_data) > FRAME_MAX_DATA_LENGTH:
            _logger(f"Error: Current TX frame too long, slot id: {slot_id}, abort")
            return -1

        # fill in tx_frame_data according to signal value one by one
        frame_data_to_send = [x for x in tx_frame_data]  # Copy tx_frame_data
        for signal_name, signal_value in signal_name_value_pairs.items():
            signal_info_po = self.db.get_signal_info_po_by_name(signal_name)
            if signal_info_po is None:
                _logger(f"Failed to get signal info PO by name: {signal_name}")
                _logger(f"Value of {signal_name} will not be updated")
                continue

            _logger(f"Debug: {signal_info_po}")
            if (
                signal_info_po.slot_id != slot_id
                or signal_info_po.base_cycle != base_cycle
            ):
                _logger("Error: signal slot ID or base cycle mismatch")
                return -1

            tmp_frame_data = TsmasterMidwareBase._fill_in_frame_data(
                frame_data=frame_data_to_send,
                bit_position=signal_info_po.bit_position,
                bit_length=signal_info_po.bit_length,
                signal_value=signal_value,
            )

            _logger(f"Info: [{signal_name}] -> {signal_value}")
            frame_data_to_send = tmp_frame_data

        if frame_data_to_send == tx_frame_data:
            _logger("Info: data to change is same with current TX frame, nothing to do")
            return 0

        return self._send_frame_to_bus(
            slot_id=slot_id, base_cycle=base_cycle, frame_data=frame_data_to_send
        )

    @staticmethod
    def _fill_in_frame_data(
        frame_data: list[int], bit_position: int, bit_length: int, signal_value: int
    ) -> list[int]:
        #
        # Assume that: position = 15, length = 4, value = 0x0d
        #
        # bit sequence of flexray frame:
        #             7  6  5  4  3  2  1  0   15 14 13 12 11 10  9  8
        # bit sequence for programming
        #             0  1  2  3  4  5  6  7    8  9 10 11 12 13 14 15
        # bit offset:
        #             0  1  2  3  4  5  6  7    0  1  2  3  4  5  6  7
        # byte offset:
        #             0                         1
        #
        # left shift cnt: 4 (bits)
        #                                       |<-         1  1  0  1
        #                                       1  1  0  1
        # erase_mask:
        #             1  1  1  1  1  1  1  1    0  0  0  0  1  1  1  1
        # data_mask:
        #             0  0  0  0  0  0  0  0    1  1  0  1  0  0  0  0

        # [0x01, 0x02] -> 00000001 00000010
        frame_data_binary = 0
        for i in frame_data:
            frame_data_binary |= i
            frame_data_binary <<= 8
        # 1 more left shift in last loop, undo it
        frame_data_binary >>= 8

        byte_offset = bit_position // 8
        bit_offset = 7 - (bit_position % 8)
        if (byte_offset * 8) + bit_offset + bit_length > len(frame_data) * 8:
            # Do nothing but return the original frame data
            _logger("Error: out range of frame")
            return frame_data

        left_shift_cnt = (len(frame_data) - byte_offset) * 8 - bit_offset - bit_length
        erase_mask = ~((2**bit_length - 1) << left_shift_cnt)
        data_mask = (signal_value & (2**bit_length - 1)) << left_shift_cnt
        new_value = frame_data_binary & erase_mask | data_mask

        # 00000001 11010010 -> [0x01, 0xD2]
        new_fame_data: list[int] = []
        for i in range(len(frame_data)):
            new_fame_data.insert(0, new_value & 0xFF)
            new_value >>= 8

        return new_fame_data

    def _send_frame_to_bus(
        self, slot_id: int, base_cycle: int, frame_data: list[int]
    ) -> int:
        frame = TLIBFlexray(
            FChannelMask=1,
            FDir=1,
            FSlotId=slot_id,
            FCycleNumber=base_cycle,
            FData=(c_uint8 * FRAME_MAX_DATA_LENGTH)(),
        )
        frame.FActualPayloadLength = len(frame_data)
        for i, v in enumerate(frame_data):
            frame.FData[i] = c_uint8(v)

        return tsflexray_transmit_sync(
            AHandle=self.tsapp_handler, AData=frame, ATimeoutMs=TS_TIMEOUT_MS
        )


class TsmasterMidware(TsmasterMidwareBase):
    """handler high level function of TSMaster

    :raises MidwareException: When failed to connect TSMaster
    """

    def __init__(self, database: str):
        """__init__

        :param str database: Flexray database XML file path
        """
        super().__init__(database)

    def set_usage_mode(self, usage_mode: int):
        """Change Usage Mode with UB enabled

        0: Abandon
        1: Inactive
        2: Convenience
        11: Active
        13: Driving

        :param int usage_mode: The real value indicates usage mode
        """
        self.change_single_frame_signals(
            {"VehModMngtGlbSafe1UsgModSts": usage_mode, "VehModMngtGlbSafe1_UB": 1}
        )

    def set_usage_mode_abandon(self):
        self.set_usage_mode(0)

    def set_usage_mode_inactive(self):
        self.set_usage_mode(1)

    def set_usage_mode_driving(self):
        self.set_usage_mode(13)

    def change_signal_with_sbox_syntax(self, command: str) -> int:
        """Change the signal on Flexray Bus, compatible for SBox syntax

        user_CEMBackBoneSignalIpdu02,VehModMngtGlbSafe1_UB,1
        CEMBackBoneSignalIpdu02,VehModMngtGlbSafe1_UB,1

        :param str command: SBOX command
        :return int: Return value from TOSUN low layer API, -1 if failed
        """
        if command.startswith("user_"):
            # Compatible for SBox syntax
            command = command[5:]

        tokens = command.split(",")
        if len(tokens) != 3:
            _logger("Invalid command")
            return -1

        _, signal_name, signal_value = [s.strip() for s in tokens]
        signal_value = int(signal_value)

        return self.change_signal(signal_name, signal_value)


def demo():
    """Simple Demo of how to use midware"""
    tsmaster_midware = TsmasterMidware("ZSDB122200_CX1E_SMP_BackboneFR_220628.xml")
    tsmaster_midware.do_init()
    tsmaster_midware.start()
    tsmaster_midware.set_usage_mode_abandon()
    time.sleep(3)
    tsmaster_midware.stop()
    tsmaster_midware.do_deinit()
    time.sleep(20)
    tsmaster_midware.do_init()
    tsmaster_midware.start()
    tsmaster_midware.change_signal(signal_name="VehModMngtGlbSafe1_UB", signal_value=1)
    tsmaster_midware.change_signal(
        signal_name="VehModMngtGlbSafe1CarModSts1", signal_value=0
    )
    tsmaster_midware.change_signal(
        signal_name="VehModMngtGlbSafe1UsgModSts", signal_value=11
    )
    tsmaster_midware = TsmasterMidware("ZSDB122200_CX1E_SMP_BackboneFR_220628.xml")
    tsmaster_midware.do_init()
    tsmaster_midware.start()
    return
    # for _ in range(1):
    #     tsmaster_midware.set_usage_mode_driving()
    #     time.sleep(10)
    #     tsmaster_midware.set_usage_mode_inactive()
    #     time.sleep(10)
    #     tsmaster_midware.set_usage_mode_abandon()
    #     time.sleep(10)

    # tsmaster_midware.change_signal_with_sbox_syntax(
    #     'user_CEMBackBoneSignalIpdu02,VehModMngtGlbSafe1UsgModSts,11')

    # tsmaster_midware.change_signal(signal_name='VehModMngtGlbSafe1_UB',
    #                                signal_value=1)

    # # It should be ensure that all signals are in same frame,
    # # with same slot id, base cycle and cycle repetition
    # tsmaster_midware.change_single_frame_signals({
    #     'LockgCenSts_UB': 1,
    #     'LockgCenStsTrigSrc': 2,
    #     'LockgCenStsLockSt': 1
    # })

    # tsmaster_midware.change_single_frame_signals({
    #     'AmbTRaw_UB': 1,
    #     'AmbTRawAmbTVal': 700
    # })

    # # It should be sure that all signals are sent by channel 0, mask 1
    # tsmaster_midware.change_single_channel_signals({
    #     'LockgCenSts_UB': 1,
    #     'LockgCenStsTrigSrc': 2,
    #     'LockgCenStsLockSt': 3,
    #     'AmbTRaw_UB': 1,
    #     'AmbTRawAmbTVal': 10
    # })

    # XXX: stop and deinit is not necessary
    #
    # But stop(), deinit() should be invoked if you want to stop Flexray bus
    #   when there is any message in "Transmit" window
    #
    # tsmaster_midware.stop()
    # tsmaster_midware.do_deinit()


if __name__ == "__main__":
    demo()

#!/usr/bin/env python
"""
@Time   :2022/105/24 11:16
@Author :SEVEN
@File   :TScanAPI.py
@Comment:使用python64 libTSCANApiOnLinux.dll libTSH.dll (x64);
使用python32 libTSCANApiOnLinux.dll libTSH.dll libLog.dll binlog.dll(x32)
------------------------------------------------

usy2wx:
remove CAN, LIN module, fix type hint & syntax warnings
"""
from ctypes import (
    c_int,
    c_int8,
    c_uint,
    c_uint8,
    c_uint16,
    c_uint32,
    c_uint64,
    c_size_t,
    c_char,
    c_bool,
    windll,
    string_at,
    byref,
    POINTER,
    Array,
    Structure,
)
import os

# _curr_path = os.path.split(os.path.realpath(__file__))[0]
_curr_path = os.path.dirname(__file__)
_lib_path = os.path.join(_curr_path, "windows/x64/libTSCAN.dll")
dll = windll.LoadLibrary(_lib_path)


class TLIBFlexray(Structure):
    _pack_ = 1
    _fields_ = [
        ("FIdxChn", c_uint8),
        ("FChannelMask", c_uint8),
        ("FDir", c_uint8),
        ("FPayloadLength", c_uint8),
        ("FActualPayloadLength", c_uint8),
        ("FCycleNumber", c_uint8),
        ("FCCType", c_uint8),
        ("FReserved0", c_uint8),
        ("FHeaderCRCA", c_uint16),
        ("FHeaderCRCB", c_uint16),
        ("FFrameStateInfo", c_uint16),
        ("FSlotId", c_uint16),
        ("FFrameFlags", c_uint32),
        ("FFrameCRC", c_uint32),
        ("FReserved1", c_uint64),
        ("FReserved2", c_uint64),
        ("FTimeUs", c_uint64),
        ("FData", c_uint8 * 254),
    ]


class TLibFlexray_controller_config(Structure):
    _pack_ = 1
    _fields_ = [
        ("NETWORK_MANAGEMENT_VECTOR_LENGTH", c_uint8),
        ("PAYLOAD_LENGTH_STATIC", c_uint8),
        ("FReserved", c_uint16),
        ("LATEST_TX", c_uint16),
        ("T_S_S_TRANSMITTER", c_uint16),
        ("CAS_RX_LOW_MAX", c_uint8),
        ("SPEED", c_uint8),
        ("WAKE_UP_SYMBOL_RX_WINDOW", c_uint16),
        ("WAKE_UP_PATTERN", c_uint8),
        ("WAKE_UP_SYMBOL_RX_IDLE", c_uint8),
        ("WAKE_UP_SYMBOL_RX_LOW", c_uint8),
        ("WAKE_UP_SYMBOL_TX_IDLE", c_uint8),
        ("WAKE_UP_SYMBOL_TX_LOW", c_uint8),
        ("channelAConnectedNode", c_uint8),
        ("channelBConnectedNode", c_uint8),
        ("channelASymbolTransmitted", c_uint8),
        ("channelBSymbolTransmitted", c_uint8),
        ("ALLOW_HALT_DUE_TO_CLOCK", c_uint8),
        ("SINGLE_SLOT_ENABLED", c_uint8),
        ("wake_up_idx", c_uint8),
        ("ALLOW_PASSIVE_TO_ACTIVE", c_uint8),
        ("COLD_START_ATTEMPTS", c_uint8),
        ("synchFrameTransmitted", c_uint8),
        ("startupFrameTransmitted", c_uint8),
        ("LISTEN_TIMEOUT", c_uint32),
        ("LISTEN_NOISE", c_uint8),
        ("MAX_WITHOUT_CLOCK_CORRECTION_PASSIVE", c_uint8),
        ("MAX_WITHOUT_CLOCK_CORRECTION_FATAL", c_uint8),
        ("REVERS0", c_uint8),
        ("MICRO_PER_CYCLE", c_uint32),
        ("Macro_Per_Cycle", c_uint16),
        ("SYNC_NODE_MAX", c_uint8),
        ("REVERS1", c_uint8),
        ("MICRO_INITIAL_OFFSET_A", c_uint8),
        ("MICRO_INITIAL_OFFSET_B", c_uint8),
        ("MACRO_INITIAL_OFFSET_A", c_uint8),
        ("MACRO_INITIAL_OFFSET_B", c_uint8),
        ("N_I_T", c_uint16),
        ("OFFSET_CORRECTION_START", c_uint16),
        ("DELAY_COMPENSATION_A", c_uint8),
        ("DELAY_COMPENSATION_B", c_uint8),
        ("CLUSTER_DRIFT_DAMPING", c_uint8),
        ("DECODING_CORRECTION", c_uint8),
        ("ACCEPTED_STARTUP_RANGE", c_uint16),
        ("MAX_DRIFT", c_uint16),
        ("STATIC_SLOT", c_uint16),
        ("NUMBER_OF_STATIC_SLOTS", c_uint16),
        ("MINISLOT", c_uint8),
        ("REVERS2", c_uint8),
        ("NUMBER_OF_MINISLOTS", c_uint16),
        ("DYNAMIC_SLOT_IDLE_PHASE", c_uint8),
        ("ACTION_POINT_OFFSET", c_uint8),
        ("MINISLOT_ACTION_POINT_OFFSET", c_uint8),
        ("REVERS3", c_uint8),
        ("OFFSET_CORRECTION_OUT", c_uint16),
        ("RATE_CORRECTION_OUT", c_uint16),
        ("EXTERN_OFFSET_CORRECTION", c_uint8),
        ("EXTERN_RATE_CORRECTION", c_uint8),
        ("REVERS4", c_uint8),
        ("config_byte", c_uint8),  # bit0: 1：启用cha上终端电阻 0：不启用
        # bit1: 1：启用chb上终端电阻 0：不启用
        # bit2: 1：启用接收FIFO     0：不启用
        # bit4: 1：cha桥接使能    0：不使能
        # bit5: 1：chb桥接使能    0：不使能
        # bit6: 1:not ignore NULL Frame  0: ignore NULL Frame
    ]

    def __init__(
        self,
        is_open_a: bool = True,
        is_open_b: bool = True,
        wakeup_chn: int = 0,
        enable100_a: bool = True,
        enable100_b: bool = True,
        is_show_nullframe: bool = True,
    ):
        """
        is_open :是否打开通道
        wakeup_chn：唤醒通道 0：通道A ,1:通道B
        enable100: 使能通道 100欧终端电阻
        is_show_nullframe：是否显示空针
        """
        self.NETWORK_MANAGEMENT_VECTOR_LENGTH = 8
        self.PAYLOAD_LENGTH_STATIC = 16
        self.LATEST_TX = 124
        self.T_S_S_TRANSMITTER = 9
        self.CAS_RX_LOW_MAX = 87
        self.SPEED = 0
        self.WAKE_UP_SYMBOL_RX_WINDOW = 301
        self.WAKE_UP_PATTERN = 43
        self.WAKE_UP_SYMBOL_RX_IDLE = 59
        self.WAKE_UP_SYMBOL_RX_LOW = 55
        self.WAKE_UP_SYMBOL_TX_IDLE = 180
        self.WAKE_UP_SYMBOL_TX_LOW = 60
        self.channelAConnectedNode = 0
        if is_open_a:
            self.channelAConnectedNode = 1  # 是否启用通道A,0不启动，1启动
        self.channelBConnectedNode = 0  # 是否启用通道B,0不启动，1启动
        if is_open_b:
            self.channelAConnectedNode = 1
        self.channelASymbolTransmitted = 1  # 是否启用通道A的符号传输功能,0不启动，1启动
        self.channelBSymbolTransmitted = 1  # 是否启用通道B的符号传输功能,0不启动，1启动
        self.ALLOW_HALT_DUE_TO_CLOCK = 1
        self.SINGLE_SLOT_ENABLED = 0  # FALSE_0, TRUE_1
        self.wake_up_idx = wakeup_chn  # 唤醒通道选择， 0_通道A， 1 通道B
        self.ALLOW_PASSIVE_TO_ACTIVE = 2
        self.COLD_START_ATTEMPTS = 10
        self.synchFrameTransmitted = 1  # 本节点是否需要发送同步报文
        self.startupFrameTransmitted = 1  # 本节点是否需要发送启动报文
        self.LISTEN_TIMEOUT = 401202
        self.LISTEN_NOISE = 2  # 2_16
        self.MAX_WITHOUT_CLOCK_CORRECTION_PASSIVE = 10
        self.MAX_WITHOUT_CLOCK_CORRECTION_FATAL = 14
        self.MICRO_PER_CYCLE = 200000
        self.Macro_Per_Cycle = 5000
        self.SYNC_NODE_MAX = 8
        self.MICRO_INITIAL_OFFSET_A = 31
        self.MICRO_INITIAL_OFFSET_B = 31
        self.MACRO_INITIAL_OFFSET_A = 11
        self.MACRO_INITIAL_OFFSET_B = 11
        self.N_I_T = 44
        self.OFFSET_CORRECTION_START = 4981
        self.DELAY_COMPENSATION_A = 1
        self.DELAY_COMPENSATION_B = 1
        self.CLUSTER_DRIFT_DAMPING = 2
        self.DECODING_CORRECTION = 48
        self.ACCEPTED_STARTUP_RANGE = 212
        self.MAX_DRIFT = 601
        self.STATIC_SLOT = 61
        self.NUMBER_OF_STATIC_SLOTS = 60
        self.MINISLOT = 10
        self.NUMBER_OF_MINISLOTS = 129
        self.DYNAMIC_SLOT_IDLE_PHASE = 0
        self.ACTION_POINT_OFFSET = 9
        self.MINISLOT_ACTION_POINT_OFFSET = 3
        self.OFFSET_CORRECTION_OUT = 378
        self.RATE_CORRECTION_OUT = 601
        self.EXTERN_OFFSET_CORRECTION = 0
        self.EXTERN_RATE_CORRECTION = 0
        # if
        self.config_byte = (
            0xC
            | (0x1 if enable100_a else 0x00)
            | (0x2 if enable100_b else 0x00)
            | (0x40 if is_show_nullframe else 0x00)
        )


class TLibTrigger_def(Structure):
    _pack_ = 1
    _fields_ = [
        ("frame_idx", c_uint8),
        ("slot_id", c_uint8),
        ("cycle_code", c_uint8),
        ("config_byte", c_uint8),  # bit0: 是否使能通道A
        # bit1: 是否使能通道B
        # bit2: 是否网络管理报文
        # bit3: 传输模式，0 表示连续传输，1表示单次触发
        # bit4: 是否为冷启动报文，只有缓冲区0可以置1
        # bit5: 是否为同步报文，只有缓冲区0 / 1 可以置1
        # bit6:
        # bit7: 帧类型：0 - 静态，1 - 动态
    ]

    def __init__(
        self,
        frame_idx: int = 0,
        slot_id: int = 1,
        cycle_code: int = 1,
        config_byte: int = 0x31,
    ):
        self.frame_idx = frame_idx
        self.slot_id = slot_id
        self.cycle_code = cycle_code
        self.config_byte = config_byte


# 初始化函数（是否使能fifo,是否激活极速模式）
def initialize_lib_tsmaster(AEnableFIFO: c_bool, AEnableTurbe: c_bool):
    dll.initialize_lib_tscan(AEnableFIFO, AEnableTurbe, True)


# 连接硬件(ADeviceSerial为null为任意硬仄1 7,ADeviceSerial == ""为连接任意设备，不为空时连接指定序列叄1 7 设备)
def tsapp_connect(ADeviceSerial: bytes, AHandle: c_size_t):
    r = dll.tscan_connect(ADeviceSerial, byref(AHandle))
    return r


def tscan_scan_devices(ADeviceCount: c_uint32):
    r = dll.tscan_scan_devices(byref(ADeviceCount))
    return r


def tsflexray_set_controller_frametrigger(
    AHandle: c_size_t,
    ANodeIndex: c_uint,
    AControllerConfig: TLibFlexray_controller_config,
    AFrameLengthArray: Array[c_int],
    AFrameNum: c_int,
    AFrameTrigger: TLibTrigger_def,
    AFrameTriggerNum: c_int,
    ATimeoutMs: c_int,
):
    r = dll.tsflexray_set_controller_frametrigger(
        AHandle,
        ANodeIndex,
        byref(AControllerConfig),
        AFrameLengthArray,
        AFrameNum,
        byref(AFrameTrigger),
        AFrameTriggerNum,
        ATimeoutMs,
    )
    return r


def tsflexray_start_net(AHandle: c_size_t, ANodeIndex: c_int, ATimeoutMs: c_int):
    r = dll.tsflexray_start_net(AHandle, ANodeIndex, ATimeoutMs)
    return r


def tsflexray_stop_net(AHandle: c_size_t, ANodeIndex: c_int, ATimeoutMs: c_int):
    r = dll.tsflexray_stop_net(AHandle, ANodeIndex, ATimeoutMs)
    return r


def tsfifo_clear_flexray_receive_buffers(AHandle: c_size_t, chn: c_int):
    r = dll.tsfifo_clear_flexray_receive_buffers(AHandle, chn)
    return r


def tsflexray_transmit_async(AHandle: c_size_t, AData: TLIBFlexray):
    r = dll.tsflexray_transmit_async(AHandle, byref(AData))
    return r


def tsflexray_transmit_sync(AHandle: c_size_t, AData: TLIBFlexray, ATimeoutMs: c_int):
    r = dll.tsflexray_transmit_sync(AHandle, byref(AData), ATimeoutMs)
    return r


def tsfifo_read_flexray_buffer_frame_count(
    AHandle: c_size_t, AIdxChn: c_int, ACount: c_int
):
    r = dll.tsfifo_read_flexray_buffer_frame_count(AHandle, AIdxChn, byref(ACount))
    return r


def tsfifo_read_flexray_tx_buffer_frame_coun(
    AHandle: c_size_t, AIdxChn: c_int, ACount: c_int
):
    r = dll.tsfifo_read_flexray_tx_buffer_frame_coun(AHandle, AIdxChn, byref(ACount))
    return r


def tsfifo_read_flexray_rx_buffer_frame_coun(
    AHandle: c_size_t, AIdxChn: c_int, ACount: c_int
):
    r = dll.tsfifo_read_flexray_rx_buffer_frame_coun(AHandle, AIdxChn, byref(ACount))
    return r


def tsfifo_receive_flexray_msgs(
    AHandle: c_size_t,
    ADataBuffers: Array[TLIBFlexray],
    ADataBufferSize: c_int,
    chn: c_int,
    ARxTx: c_int8,
):
    r = dll.tsfifo_receive_flexray_msgs(
        AHandle, ADataBuffers, byref(ADataBufferSize), chn, ARxTx
    )
    return r


def tscan_get_device_info(ADeviceCount: c_uint64):
    AFManufacturer = POINTER(POINTER(c_char))()

    AFProduct = POINTER(POINTER(c_char))()
    AFSerial = POINTER(POINTER(c_char))()
    r = dll.tscan_get_device_info(
        ADeviceCount, byref(AFManufacturer), byref(AFProduct), byref(AFSerial)
    )
    if r == 0:
        FManufacturer = string_at(AFManufacturer).decode("utf8")
        FProduct = string_at(AFProduct).decode("utf8")
        FSerial = string_at(AFSerial).decode("utf8")
    else:
        print("查找失败")
        return 0, 0, 0
    return FManufacturer, FProduct, FSerial


# 断开指定硬件连接
def tsapp_disconnect_AHandle(AHandle: c_size_t):
    r = dll.tscan_disconnect_by_handle(AHandle)
    return r


# 断开所有硬件连接
def tsapp_disconnect_all():
    r = dll.tscan_disconnect_all_devices()
    return r

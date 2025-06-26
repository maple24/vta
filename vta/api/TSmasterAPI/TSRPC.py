import ctypes
from ctypes import c_double, byref, c_size_t, c_bool, c_char_p, c_int32, POINTER, create_string_buffer
import os
import inspect
from loguru import logger
from vta.api.TSmasterAPI.consts import TSMASTER_ERROR_CODES


class TSMasterRPC:
    """
    TSMasterRPC封装类, 提供TSMaster.dll的功能调用
    """

    def __init__(self, app_name, dev_mode="can"):
        self._app_name = app_name
        self._dev_mode = dev_mode
        self._app_handle = c_size_t()
        self.dll = None  # DLL句柄
        try:
            self._load_dll()
            self._connect_and_start()
        except Exception as e:
            raise RuntimeError(f"Initialization failed: {e}")

    def _load_dll(self):
        """加载DLL文件并设置函数原型"""
        dll_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "TSMaster.dll")
        try:
            self.dll = ctypes.CDLL(dll_path)
        except OSError as e:
            raise RuntimeError(f"Failed to load DLL: {e}")

        # 函数原型定义
        self.dll.initialize_lib_tsmaster.argtypes = [c_char_p]
        self.dll.rpc_tsmaster_create_client.argtypes = [c_char_p, POINTER(c_size_t)]
        self.dll.rpc_tsmaster_activate_client.argtypes = [c_size_t, c_bool]
        self.dll.rpc_tsmaster_cmd_start_simulation.argtypes = [c_size_t]
        self.dll.rpc_tsmaster_is_simulation_running.argtypes = [c_size_t, POINTER(c_bool)]
        self.dll.rpc_tsmaster_cmd_get_can_signal.argtypes = [c_size_t, c_char_p, POINTER(c_double)]
        self.dll.rpc_tsmaster_cmd_set_can_signal.argtypes = [c_size_t, c_char_p, c_double]
        self.dll.rpc_tsmaster_cmd_read_system_var.argtypes = [c_size_t, c_char_p, POINTER(c_double)]
        self.dll.rpc_tsmaster_cmd_write_system_var.argtypes = [c_size_t, c_char_p, c_char_p]
        self.dll.rpc_tsmaster_call_system_api.argtypes = [c_size_t, c_char_p, c_int32, c_int32, POINTER(c_char_p)]
        self.dll.rpc_tsmaster_call_library_api.argtypes = [c_size_t, c_char_p, c_int32, c_int32, POINTER(c_char_p)]

    def _handle_error(self, ret_code, action=""):
        """通用错误处理方法"""
        if ret_code != 0:
            error_msg = TSMASTER_ERROR_CODES.get(ret_code, ("Unknown", "Unknown error"))
            content = f"{action} failed: {error_msg}"
        else:
            content = f"{action} success"
        logger.info(content)

    def _connect_and_start(self):
        """连接TSMaster并启动仿真"""
        self.dll.initialize_lib_tsmaster(self._app_name.encode())

        # 创建客户端
        ret_code = self.dll.rpc_tsmaster_create_client(self._app_name.encode(), byref(self._app_handle))
        self._handle_error(ret_code, "Create RPC Client")

        # 激活客户端
        ret_code = self.dll.rpc_tsmaster_activate_client(self._app_handle, True)
        self._handle_error(ret_code, "Activate RPC Client")

        # 启动仿真
        ret_code = self.dll.rpc_tsmaster_cmd_start_simulation(self._app_handle)
        self._handle_error(ret_code, "Start Simulation")

        # 检查仿真状态
        is_running = c_bool()
        ret_code = self.dll.rpc_tsmaster_is_simulation_running(self._app_handle, byref(is_running))
        if is_running.value:
            logger.success("Simulation is running.")
        else:
            logger.warning("Simulation is not running.")

    def _get_value(self, cmd, path: str) -> float:
        """通用获取值方法"""
        value = c_double(0)
        ret_code = cmd(self._app_handle, path.encode(), byref(value))
        self._handle_error(ret_code, f"{inspect.currentframe().f_code.co_name}, {path=}")
        return round(value.value, 3)

    def _set_value(self, cmd, path: str, value):
        """通用设置值方法"""
        ret_code = cmd(self._app_handle, path.encode(), value)
        self._handle_error(ret_code, f"{inspect.currentframe().f_code.co_name}, {path=}, {value=}")
        return ret_code

    def get_signal_value(self, sig_path: str) -> float:
        """获取CAN信号值"""
        return self._get_value(self.dll.rpc_tsmaster_cmd_get_can_signal, sig_path)

    def set_signal_value(self, sig_path: str, sig_value: float):
        """设置CAN信号值"""
        return self._set_value(self.dll.rpc_tsmaster_cmd_set_can_signal, sig_path, sig_value)

    def get_system_value(self, system_path: str) -> float:
        """获取系统变量值"""
        return self._get_value(self.dll.rpc_tsmaster_cmd_read_system_var, system_path)

    def set_system_value(self, system_path: str, system_value: str):
        """设置系统变量值"""
        return self.dll.rpc_tsmaster_cmd_write_system_var(self._app_handle, system_path.encode(), system_value.encode())

    def rpc_tsmaster_call_system_api(self, AAPIName: str, AArgs: list):
        """调用服务器端系统函数"""
        AArgCapacity = 1024
        AArgCount = len(AArgs)

        args_buffers = [create_string_buffer(AArgCapacity) for _ in range(AArgCount)]
        for i, arg in enumerate(AArgs):
            if len(arg) >= AArgCapacity:
                raise ValueError(f"参数 {i + 1} ({arg}) 超出最大长度 {AArgCapacity}")
            args_buffers[i].value = arg.encode()

        p_args = (c_char_p * AArgCount)(*map(ctypes.addressof, args_buffers))

        ret = self.dll.rpc_tsmaster_call_system_api(
            self._app_handle, AAPIName.encode(), AArgCount, AArgCapacity, p_args
        )
        self._handle_error(ret, f"{inspect.currentframe().f_code.co_name}, {AAPIName=}, {AArgs=}")
        return ret

    def rpc_tsmaster_call_library_api(self, AAPIName: str, AArgs: list):
        """调用库函数"""
        AArgCapacity = 1024
        AArgCount = len(AArgs)

        args_buffers = [create_string_buffer(AArgCapacity) for _ in range(AArgCount)]
        for i, arg in enumerate(AArgs):
            if len(arg) >= AArgCapacity:
                raise ValueError(f"参数 {i + 1} ({arg}) 超出最大长度 {AArgCapacity}")
            args_buffers[i].value = arg.encode()

        p_args = (c_char_p * AArgCount)(*map(ctypes.addressof, args_buffers))

        ret = self.dll.rpc_tsmaster_call_library_api(
            self._app_handle, AAPIName.encode(), AArgCount, AArgCapacity, p_args
        )
        self._handle_error(ret, f"{inspect.currentframe().f_code.co_name}, {AAPIName=}, {AArgs=}")
        return ret

    def log_text(self, text: str, log_level: int = 5):
        """记录日志"""
        apiName = "app.log_text"
        args = [f">>>External script debug : {text}", f"{log_level}"]
        return self.rpc_tsmaster_call_system_api(apiName, args)


# 示例使用
if __name__ == "__main__":
    try:
        app_name = "TSMaster"
        rpc = TSMasterRPC(app_name)

        # 示例调用
        # run simulation
        # app function
        apiName = "com.can_rbs_activate_node_by_name"
        # copy database path
        args = ["0", "True", "D01D01PMessageListICCANFD_V21_20", "FLZCU_IC", "False"]
        val = rpc.rpc_tsmaster_call_system_api(apiName, args)

    except Exception as e:
        logger.error(f"Error: {e}")

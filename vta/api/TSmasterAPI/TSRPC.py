import ctypes
from ctypes import c_double, byref, c_size_t, c_bool, c_char_p, c_int32, POINTER, create_string_buffer
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import List, Optional, Union, Any, Dict
from loguru import logger
from vta.api.TSmasterAPI.consts import TSMASTER_ERROR_CODES


class DeviceMode(Enum):
    """Enumeration for device modes."""
    CAN = "can"
    LIN = "lin"
    FLEXRAY = "flexray"
    ETHERNET = "ethernet"


class LogLevel(Enum):
    """Enumeration for log levels."""
    CRITICAL = 1
    ERROR = 2
    WARNING = 3
    INFO = 4
    DEBUG = 5


@dataclass
class TSMasterConfig:
    """Configuration for TSMaster connection."""
    app_name: str = "TSMaster"
    dev_mode: DeviceMode = DeviceMode.CAN
    dll_path: Optional[str] = None
    auto_start_simulation: bool = True
    
    def __post_init__(self):
        if isinstance(self.dev_mode, str):
            self.dev_mode = DeviceMode(self.dev_mode)


class TSMasterError(Exception):
    """Custom exception for TSMaster errors."""
    def __init__(self, error_code: int, action: str = ""):
        self.error_code = error_code
        self.action = action
        error_info = TSMASTER_ERROR_CODES.get(error_code, ("Unknown", "Unknown error"))
        super().__init__(f"{action} failed: {error_info}")


def handle_tsmaster_error(action: str = ""):
    """Decorator for handling TSMaster API errors."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
                if isinstance(result, int) and result != 0:
                    error_msg = TSMASTER_ERROR_CODES.get(result, ("Unknown", "Unknown error"))
                    logger.error(f"{action or func.__name__} failed: {error_msg}")
                    raise TSMasterError(result, action or func.__name__)
                else:
                    logger.debug(f"{action or func.__name__} success")
                return result
            except Exception as e:
                if not isinstance(e, TSMasterError):
                    logger.exception(f"Unexpected error in {func.__name__}: {e}")
                raise
        return wrapper
    return decorator


def require_dll_loaded(func):
    """Decorator to ensure DLL is loaded before method execution."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.dll:
            raise RuntimeError("DLL not loaded")
        return func(self, *args, **kwargs)
    return wrapper


def require_simulation_running(func):
    """Decorator to ensure simulation is running before method execution."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.is_simulation_running():
            logger.warning("Simulation is not running, attempting to start...")
            self.start_simulation()
        return func(self, *args, **kwargs)
    return wrapper


class TSMasterInterface(ABC):
    """Abstract base class for TSMaster interfaces."""
    
    @abstractmethod
    def connect(self) -> None:
        """Establish connection to TSMaster."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from TSMaster."""
        pass
    
    @abstractmethod
    def get_signal_value(self, sig_path: str) -> float:
        """Get signal value."""
        pass
    
    @abstractmethod
    def set_signal_value(self, sig_path: str, sig_value: float) -> None:
        """Set signal value."""
        pass


class DLLManager:
    """Utility class for DLL operations."""
    
    @staticmethod
    def get_dll_path(custom_path: Optional[str] = None) -> str:
        """Get the DLL path."""
        if custom_path and os.path.exists(custom_path):
            return custom_path
        
        default_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 
            "TSMaster.dll"
        )
        
        if not os.path.exists(default_path):
            raise FileNotFoundError(f"TSMaster.dll not found at {default_path}")
        
        return default_path
    
    @staticmethod
    def setup_function_prototypes(dll) -> None:
        """Set up function prototypes for the DLL."""
        prototypes = {
            'initialize_lib_tsmaster': [c_char_p],
            'rpc_tsmaster_create_client': [c_char_p, POINTER(c_size_t)],
            'rpc_tsmaster_activate_client': [c_size_t, c_bool],
            'rpc_tsmaster_cmd_start_simulation': [c_size_t],
            'rpc_tsmaster_is_simulation_running': [c_size_t, POINTER(c_bool)],
            'rpc_tsmaster_cmd_get_can_signal': [c_size_t, c_char_p, POINTER(c_double)],
            'rpc_tsmaster_cmd_set_can_signal': [c_size_t, c_char_p, c_double],
            'rpc_tsmaster_cmd_read_system_var': [c_size_t, c_char_p, POINTER(c_double)],
            'rpc_tsmaster_cmd_write_system_var': [c_size_t, c_char_p, c_char_p],
            'rpc_tsmaster_call_system_api': [c_size_t, c_char_p, c_int32, c_int32, POINTER(c_char_p)],
            'rpc_tsmaster_call_library_api': [c_size_t, c_char_p, c_int32, c_int32, POINTER(c_char_p)],
            'rpc_tsmaster_destroy_client': [c_size_t]
        }
        
        for func_name, argtypes in prototypes.items():
            if hasattr(dll, func_name):
                getattr(dll, func_name).argtypes = argtypes


class TSMasterRPC(TSMasterInterface):
    """
    TSMasterRPC封装类, 提供TSMaster.dll的功能调用
    """

    def __init__(self, config: Union[TSMasterConfig, str, Dict[str, Any]] = None):
        # Handle different config types
        if isinstance(config, str):
            self.config = TSMasterConfig(app_name=config)
        elif isinstance(config, dict):
            self.config = TSMasterConfig(**config)
        elif isinstance(config, TSMasterConfig):
            self.config = config
        else:
            self.config = TSMasterConfig()
        
        self._app_handle = c_size_t()
        self.dll = None
        self._is_connected = False
        
        try:
            self.connect()
        except Exception as e:
            raise RuntimeError(f"Initialization failed: {e}")

    def connect(self) -> None:
        """Establish connection to TSMaster."""
        if self._is_connected:
            logger.warning("Already connected to TSMaster")
            return
            
        self._load_dll()
        self._create_and_activate_client()
        
        if self.config.auto_start_simulation:
            self.start_simulation()
        
        self._is_connected = True
        logger.success("Successfully connected to TSMaster")

    def disconnect(self) -> None:
        """Disconnect from TSMaster."""
        if not self._is_connected:
            return
            
        try:
            if self.dll and hasattr(self.dll, "rpc_tsmaster_destroy_client"):
                self.dll.rpc_tsmaster_destroy_client(self._app_handle)
                logger.info("TSMaster client destroyed")
        except Exception as e:
            logger.warning(f"Error during disconnection: {e}")
        finally:
            self._is_connected = False

    def _load_dll(self) -> None:
        """加载DLL文件并设置函数原型"""
        dll_path = DLLManager.get_dll_path(self.config.dll_path)
        
        try:
            self.dll = ctypes.CDLL(dll_path)
            DLLManager.setup_function_prototypes(self.dll)
            logger.debug(f"DLL loaded from: {dll_path}")
        except OSError as e:
            raise RuntimeError(f"Failed to load DLL from {dll_path}: {e}")

    @handle_tsmaster_error("Initialize TSMaster library")
    def _initialize_library(self) -> int:
        """Initialize TSMaster library."""
        return self.dll.initialize_lib_tsmaster(self.config.app_name.encode())

    @handle_tsmaster_error("Create RPC client")
    def _create_client(self) -> int:
        """Create TSMaster RPC client."""
        return self.dll.rpc_tsmaster_create_client(
            self.config.app_name.encode(), 
            byref(self._app_handle)
        )

    @handle_tsmaster_error("Activate RPC client")
    def _activate_client(self) -> int:
        """Activate TSMaster RPC client."""
        return self.dll.rpc_tsmaster_activate_client(self._app_handle, True)

    def _create_and_activate_client(self) -> None:
        """Create and activate TSMaster client."""
        self._initialize_library()
        self._create_client()
        self._activate_client()

    @require_dll_loaded
    @handle_tsmaster_error("Start simulation")
    def start_simulation(self) -> int:
        """启动仿真"""
        return self.dll.rpc_tsmaster_cmd_start_simulation(self._app_handle)

    @require_dll_loaded
    def is_simulation_running(self) -> bool:
        """检查仿真是否运行"""
        is_running = c_bool()
        ret_code = self.dll.rpc_tsmaster_is_simulation_running(
            self._app_handle, 
            byref(is_running)
        )
        
        if ret_code != 0:
            logger.warning(f"Failed to check simulation status: {ret_code}")
            return False
            
        return is_running.value

    @require_dll_loaded
    @require_simulation_running
    def get_signal_value(self, sig_path: str) -> float:
        """获取CAN信号值"""
        value = c_double(0)
        ret_code = self.dll.rpc_tsmaster_cmd_get_can_signal(
            self._app_handle, 
            sig_path.encode(), 
            byref(value)
        )
        
        if ret_code != 0:
            error_msg = TSMASTER_ERROR_CODES.get(ret_code, ("Unknown", "Unknown error"))
            logger.error(f"Failed to get signal {sig_path}: {error_msg}")
            raise TSMasterError(ret_code, f"Get signal {sig_path}")
        
        result = round(value.value, 3)
        logger.debug(f"Got signal {sig_path} = {result}")
        return result

    @require_dll_loaded
    @require_simulation_running
    def set_signal_value(self, sig_path: str, sig_value: float) -> None:
        """设置CAN信号值"""
        ret_code = self.dll.rpc_tsmaster_cmd_set_can_signal(
            self._app_handle, 
            sig_path.encode(), 
            sig_value
        )
        
        if ret_code != 0:
            error_msg = TSMASTER_ERROR_CODES.get(ret_code, ("Unknown", "Unknown error"))
            logger.error(f"Failed to set signal {sig_path} to {sig_value}: {error_msg}")
            raise TSMasterError(ret_code, f"Set signal {sig_path}")
        
        logger.debug(f"Set signal {sig_path} = {sig_value}")

    @require_dll_loaded
    def get_system_value(self, system_path: str) -> float:
        """获取系统变量值"""
        value = c_double(0)
        ret_code = self.dll.rpc_tsmaster_cmd_read_system_var(
            self._app_handle, 
            system_path.encode(), 
            byref(value)
        )
        
        if ret_code != 0:
            error_msg = TSMASTER_ERROR_CODES.get(ret_code, ("Unknown", "Unknown error"))
            logger.error(f"Failed to get system variable {system_path}: {error_msg}")
            raise TSMasterError(ret_code, f"Get system variable {system_path}")
        
        result = round(value.value, 3)
        logger.debug(f"Got system variable {system_path} = {result}")
        return result

    @require_dll_loaded
    def set_system_value(self, system_path: str, system_value: str) -> None:
        """设置系统变量值"""
        ret_code = self.dll.rpc_tsmaster_cmd_write_system_var(
            self._app_handle, 
            system_path.encode(), 
            system_value.encode()
        )
        
        if ret_code != 0:
            error_msg = TSMASTER_ERROR_CODES.get(ret_code, ("Unknown", "Unknown error"))
            logger.error(f"Failed to set system variable {system_path} to {system_value}: {error_msg}")
            raise TSMasterError(ret_code, f"Set system variable {system_path}")
        
        logger.debug(f"Set system variable {system_path} = {system_value}")

    @require_dll_loaded
    def call_system_api(self, api_name: str, args: List[str]) -> int:
        """调用服务器端系统函数"""
        return self._call_api(self.dll.rpc_tsmaster_call_system_api, api_name, args)

    @require_dll_loaded
    def call_library_api(self, api_name: str, args: List[str]) -> int:
        """调用库函数"""
        return self._call_api(self.dll.rpc_tsmaster_call_library_api, api_name, args)

    def _call_api(self, api_func, api_name: str, args: List[str]) -> int:
        """通用API调用方法"""
        arg_capacity = 1024
        arg_count = len(args)

        # Validate arguments
        for i, arg in enumerate(args):
            if len(arg) >= arg_capacity:
                raise ValueError(f"参数 {i + 1} ({arg}) 超出最大长度 {arg_capacity}")

        # Create buffers and set values
        args_buffers = [create_string_buffer(arg_capacity) for _ in range(arg_count)]
        for i, arg in enumerate(args):
            args_buffers[i].value = arg.encode()

        # Create pointer array
        p_args = (c_char_p * arg_count)(*map(ctypes.addressof, args_buffers))

        # Call API
        ret_code = api_func(
            self._app_handle, 
            api_name.encode(), 
            arg_count, 
            arg_capacity, 
            p_args
        )

        if ret_code != 0:
            error_msg = TSMASTER_ERROR_CODES.get(ret_code, ("Unknown", "Unknown error"))
            logger.error(f"API call {api_name} failed: {error_msg}")
        else:
            logger.debug(f"API call {api_name} success with args: {args}")

        return ret_code

    def log_text(self, text: str, log_level: LogLevel = LogLevel.DEBUG) -> int:
        """记录日志"""
        if isinstance(log_level, LogLevel):
            level_value = log_level.value
        else:
            level_value = log_level
            
        api_name = "app.log_text"
        args = [f">>>External script debug : {text}", str(level_value)]
        return self.call_system_api(api_name, args)

    @property
    def is_connected(self) -> bool:
        """Check if connected to TSMaster."""
        return self._is_connected

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def __del__(self):
        """析构方法, 释放DLL资源"""
        self.disconnect()


# 示例使用
if __name__ == "__main__":
    # Example 1: Basic usage with default config
    print("=== Example 1: Basic Usage ===")
    try:
        with TSMasterRPC() as rpc:
            signal_path = "0/ZCU_CANFD1/ZCUD/ZcudZCUCANFD1Fr10/VehModMngtGlbSafe1UsgModSts"
            
            current_value = rpc.get_signal_value(signal_path)
            print(f"Current signal value: {current_value}")
            
            # Set signal value
            rpc.set_signal_value(signal_path, 13.0)  # driving mode
            
            # Verify the change
            new_value = rpc.get_signal_value(signal_path)
            print(f"New signal value: {new_value}")
            
    except Exception as e:
        print(f"Error: {e}")

    # Example 2: Using TSMasterConfig
    print("\n=== Example 2: Custom Configuration ===")
    config = TSMasterConfig(
        app_name="MyTSMaster",
        dev_mode=DeviceMode.CAN,
        auto_start_simulation=True
    )
    
    try:
        rpc = TSMasterRPC(config)
        print(f"Connected: {rpc.is_connected}")
        print(f"Simulation running: {rpc.is_simulation_running()}")
        
        # Log example
        rpc.log_text("Test message from Python", LogLevel.INFO)
        
    except Exception as e:
        print(f"Configuration error: {e}")
    finally:
        if 'rpc' in locals():
            rpc.disconnect()

    # Example 3: Vehicle mode switching helper
    print("\n=== Example 3: Vehicle Mode Helper ===")
    
    class VehicleModeHelper:
        def __init__(self, rpc: TSMasterRPC):
            self.rpc = rpc
            self.signal_path = "0/ZCU_CANFD1/ZCUD/ZcudZCUCANFD1Fr10/VehModMngtGlbSafe1UsgModSts"
            self.mode_map = {
                "abandon": 0,
                "inactive": 1,
                "active": 11,
                "driving": 13,
            }
        
        def set_mode(self, mode: str) -> bool:
            if mode not in self.mode_map:
                logger.error(f"Invalid mode: {mode}")
                return False
            
            try:
                value = self.mode_map[mode]
                self.rpc.set_signal_value(self.signal_path, float(value))
                logger.info(f"Set vehicle mode to {mode} (value: {value})")
                return True
            except Exception as e:
                logger.error(f"Failed to set mode {mode}: {e}")
                return False
        
        def get_current_mode(self) -> str:
            try:
                value = int(self.rpc.get_signal_value(self.signal_path))
                for mode, val in self.mode_map.items():
                    if val == value:
                        return mode
                return f"unknown({value})"
            except Exception as e:
                logger.error(f"Failed to get current mode: {e}")
                return "error"
    
    try:
        with TSMasterRPC("TSMaster") as rpc:
            vehicle = VehicleModeHelper(rpc)
            
            current_mode = vehicle.get_current_mode()
            print(f"Current vehicle mode: {current_mode}")
            
            # Switch modes
            for mode in ["inactive", "driving", "inactive"]:
                if vehicle.set_mode(mode):
                    print(f"Successfully switched to {mode}")
                else:
                    print(f"Failed to switch to {mode}")
                    
    except Exception as e:
        print(f"Vehicle mode example error: {e}")

    print("\n=== All Examples Completed ===")
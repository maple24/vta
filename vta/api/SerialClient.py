# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

import queue
import re
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Optional, Tuple, List, Dict, Any, Callable, Union
from contextlib import contextmanager

import serial
from loguru import logger


class ConnectionState(Enum):
    """Enumeration for connection states."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class SerialConfig:
    """Configuration for serial connection."""

    enabled: bool = True
    comport: str = ""
    baudrate: int = 115200
    username: str = "root"
    password: str = ""
    timeout: float = 3.0

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "SerialConfig":
        """Create config from dictionary."""
        return cls(
            enabled=config.get("putty_enabled", True),
            comport=config.get("putty_comport", ""),
            baudrate=int(config.get("putty_baudrate", 115200)),
            username=config.get("putty_username", "root"),
            password=config.get("putty_password", ""),
            timeout=float(config.get("putty_timeout", 3.0)),
        )


class SerialConnectionError(Exception):
    """Custom exception for serial connection errors."""

    pass


class LoginError(Exception):
    """Custom exception for login errors."""

    pass


def require_connection(func: Callable) -> Callable:
    """Decorator to ensure connection is active before method execution."""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.is_connected:
            raise SerialConnectionError("Not connected to serial port")
        return func(self, *args, **kwargs)

    return wrapper


def with_queue_management(queue_attr: str, event_attr: str, clear_before: bool = True):
    """Decorator for automatic queue and event management."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            queue_obj = getattr(self, queue_attr)
            event_obj = getattr(self, event_attr)

            if clear_before:
                self._clear_queue(queue_obj)
            event_obj.set()

            try:
                return func(self, *args, **kwargs)
            finally:
                event_obj.clear()

        return wrapper

    return decorator


def safe_serial_operation(func: Callable) -> Callable:
    """Decorator for safe serial operations with error handling."""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except (serial.SerialException, OSError) as e:
            logger.error(f"Serial operation failed in {func.__name__}: {e}")
            raise SerialConnectionError(f"Serial operation failed: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error in {func.__name__}: {e}")
            raise

    return wrapper


class SerialInterface(ABC):
    """Abstract base class for serial interfaces."""

    @abstractmethod
    def connect(self, config: Union[Dict[str, Any], SerialConfig]) -> None:
        """Establish connection."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection."""
        pass

    @abstractmethod
    def send_command(self, command: str) -> None:
        """Send command."""
        pass


class QueueManager:
    """Utility class for queue operations."""

    @staticmethod
    def extract_lines(target_queue: queue.Queue[Tuple[float, str]]) -> List[str]:
        """Extract trace lines from a queue."""
        traces = []
        while not target_queue.empty():
            try:
                _, line = target_queue.get_nowait()
                traces.append(line)
                target_queue.task_done()
            except queue.Empty:
                break
        return traces

    @staticmethod
    def clear_queue(target_queue: queue.Queue) -> None:
        """Clear a queue."""
        while not target_queue.empty():
            try:
                target_queue.get_nowait()
                target_queue.task_done()
            except queue.Empty:
                break


class SerialClient(SerialInterface):
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self):
        self._connection: Optional[serial.Serial] = None
        self._wait_queue: queue.Queue[Tuple[float, str]] = queue.Queue()
        self._monitor_queue: queue.Queue[Tuple[float, str]] = queue.Queue()
        self._wait_event = threading.Event()
        self._monitor_event = threading.Event()
        self._reader_event = threading.Event()
        self._reader_thread: Optional[threading.Thread] = None
        self._config: Optional[SerialConfig] = None
        self._state = ConnectionState.DISCONNECTED
        self._lock = threading.RLock()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    @property
    def is_connected(self) -> bool:
        """Check if the serial connection is active."""
        with self._lock:
            return self._state == ConnectionState.CONNECTED and self._connection and self._connection.is_open

    @property
    def state(self) -> ConnectionState:
        """Get current connection state."""
        return self._state

    def _serial_reader(self) -> None:
        """Continuously read data from serial buffer."""
        logger.info("Serial reader thread started")
        try:
            while self._reader_event.is_set():
                if not self._connection or not self._connection.is_open:
                    break

                try:
                    line = self._connection.readline().decode("utf-8", "ignore").strip()
                    if line:
                        logger.trace("[PuttyRx] - {message}", message=line)
                        timestamp = time.time()

                        if self._monitor_event.is_set():
                            self._monitor_queue.put((timestamp, line))
                        if self._wait_event.is_set():
                            self._wait_queue.put((timestamp, line))
                except (serial.SerialException, OSError) as e:
                    logger.error(f"Serial read error: {e}")
                    self._state = ConnectionState.ERROR
                    break
        except Exception as e:
            logger.exception(f"Unexpected error in serial reader: {e}")
            self._state = ConnectionState.ERROR
        finally:
            logger.info("Serial reader thread terminated")

    def _check_login_status(self) -> bool:
        """Check if already logged in to the console."""
        try:
            # Check for login error first
            if self._wait_for_pattern("(Login incorrect)", "\n", 5, False)[0]:
                logger.error("Login error detected")
                return False

            # Check if login prompt appears
            if self._wait_for_pattern("(login:.*)|(Login incorrect)", "\n", 5, False)[0]:
                logger.info("Login required")
                return False

            logger.info("Already logged in")
            return True
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False

    def connect(self, config: Union[Dict[str, Any], SerialConfig]) -> None:
        """
        Establish serial connection with the given configuration.

        Args:
            config: Dictionary or SerialConfig object containing connection parameters
        """
        if isinstance(config, dict):
            self._config = SerialConfig.from_dict(config)
        else:
            self._config = config

        if not self._config.enabled:
            logger.warning("Putty disabled in configuration")
            return

        with self._lock:
            if self._state == ConnectionState.CONNECTED:
                logger.warning("Already connected")
                return

            self._state = ConnectionState.CONNECTING
            logger.info("Establishing PuTTY connection...")

            try:
                if not self._config.comport:
                    raise SerialConnectionError("No COM port specified")

                self._connection = serial.Serial(
                    port=self._config.comport, baudrate=self._config.baudrate, timeout=self._config.timeout
                )

                self._reader_event.set()
                self._reader_thread = threading.Thread(target=self._serial_reader, daemon=True, name="PuttySerial")
                self._reader_thread.start()

                self._state = ConnectionState.CONNECTED
                logger.success(f"Connected to {self._config.comport} at {self._config.baudrate} baud")

            except Exception as e:
                self._state = ConnectionState.ERROR
                logger.exception("Failed to establish serial connection")
                raise SerialConnectionError(f"Connection failed: {e}")

    def disconnect(self) -> None:
        """Close the serial connection and cleanup resources."""
        with self._lock:
            if self._state == ConnectionState.DISCONNECTED:
                return

            logger.info("Disconnecting from serial port...")
            self._state = ConnectionState.DISCONNECTED

            # Stop reader thread
            self._reader_event.clear()
            self._wait_event.clear()
            self._monitor_event.clear()

            # Wait for thread to finish
            if self._reader_thread and self._reader_thread.is_alive():
                self._reader_thread.join(timeout=2.0)

            # Close connection
            if self._connection:
                self._connection.close()
                self._connection = None

            logger.info("Serial connection closed")

    @require_connection
    @safe_serial_operation
    def send_command(self, command: str) -> None:
        """
        Send command to the serial interface.

        Args:
            command: Command string to send
        """
        command = command.rstrip()
        self._connection.write(f"{command}\n".encode())
        self._connection.flush()
        logger.info("[PuttyTx] - {message}", message=command)

    @require_connection
    def execute_command(self, command: str, wait_time: float = 1.0, auto_login: bool = True) -> List[str]:
        """
        Execute command and return captured output.

        Args:
            command: Command to execute
            wait_time: Time to wait for output
            auto_login: Whether to auto-login if needed

        Returns:
            List of output lines
        """
        if auto_login:
            self.login()

        # Clear queue and enable monitoring before sending command
        QueueManager.clear_queue(self._wait_queue)
        self._wait_event.set()

        try:
            self.send_command(command)
            if wait_time > 0:
                time.sleep(wait_time)

            return QueueManager.extract_lines(self._wait_queue)
        finally:
            self._wait_event.clear()

    def _wait_for_pattern(
        self, pattern: str, command: str = "", timeout: float = 10.0, auto_login: bool = True
    ) -> Tuple[bool, Optional[Tuple]]:
        """Internal method to wait for a specific pattern."""
        if not self.is_connected:
            raise SerialConnectionError("Not connected to serial port")

        if auto_login:
            self.login()

        self._wait_event.set()
        start_time = time.time()

        try:
            if command:
                self.send_command(command)

            while True:
                if time.time() - start_time > timeout:
                    logger.warning(f"Timeout waiting for pattern: {pattern}")
                    return False, None

                try:
                    timestamp, line = self._wait_queue.get(timeout=0.1)
                    self._wait_queue.task_done()

                    match = re.search(pattern, line)
                    if match:
                        elapsed = round(timestamp - start_time, 2)
                        logger.success(f"Pattern matched: {match.groups()}, elapsed: {elapsed}s")
                        return True, match.groups()

                except queue.Empty:
                    continue

        finally:
            self._wait_event.clear()
            QueueManager.clear_queue(self._wait_queue)

    def wait_for_trace(
        self, pattern: str, command: str = "", timeout: float = 10.0, auto_login: bool = True
    ) -> Tuple[bool, Optional[List]]:
        """
        Wait for a specific trace pattern.

        Args:
            pattern: Regular expression pattern to match
            command: Optional command to send first
            timeout: Maximum time to wait
            auto_login: Whether to auto-login if needed

        Returns:
            Tuple of (success, matched_groups)
        """
        success, groups = self._wait_for_pattern(pattern, command, timeout, auto_login)
        return success, list(groups) if groups else None

    def login(self) -> None:
        """Login to the console with username/password."""
        if not self._config:
            raise SerialConnectionError("No configuration available")

        if self._check_login_status():
            return

        max_retries = 5
        for attempt in range(1, max_retries + 1):
            logger.info(f"Login attempt {attempt}/{max_retries}")

            try:
                # Send username
                success, _ = self._wait_for_pattern(
                    "(Password:.*)|(Logging in with home .*)", self._config.username, 5, False
                )
                if not success:
                    continue

                # Send password
                success, _ = self._wait_for_pattern("(#)|(Logging in with home .*)", self._config.password, 5, False)
                if success:
                    logger.success("Login successful")
                    return

            except Exception as e:
                logger.error(f"Login attempt {attempt} failed: {e}")

        raise LoginError("Failed to login after maximum retries")

    @contextmanager
    def monitor_traces(self):
        """Context manager for trace monitoring."""
        self.enable_monitor()
        try:
            yield self
        finally:
            self.disable_monitor()

    def enable_monitor(self) -> None:
        """Enable trace monitoring."""
        QueueManager.clear_queue(self._monitor_queue)
        self._monitor_event.set()
        logger.info("Trace monitoring enabled")

    def disable_monitor(self) -> None:
        """Disable trace monitoring."""
        self._monitor_event.clear()
        logger.info("Trace monitoring disabled")

    def get_monitored_traces(self) -> List[str]:
        """Get all monitored traces."""
        if not self._monitor_event.is_set():
            logger.warning("Trace monitoring is not enabled")
            return []

        return QueueManager.extract_lines(self._monitor_queue)

    def _clear_queue(self, target_queue: queue.Queue) -> None:
        """Clear a queue (delegated to QueueManager)."""
        QueueManager.clear_queue(target_queue)


if __name__ == "__main__":
    """
    Comprehensive examples demonstrating PuttyHelper usage.
    """

    # # Example 1: Basic connection and command execution
    # print("=== Example 1: Basic Usage ===")
    # putty = PuttyHelper()

    # # Using dictionary config (legacy support)
    # config_dict = {
    #     "putty_enabled": True,
    #     "putty_comport": "COM4",
    #     "putty_baudrate": 921600,
    #     "putty_username": "zeekr",
    #     "putty_password": "Aa123123",
    #     "putty_timeout": 3.0
    # }

    # try:
    #     putty.connect(config_dict)
    #     print(f"Connection state: {putty.state}")

    #     # Simple command execution
    #     output = putty.execute_command("ls -la", wait_time=2.0)
    #     print(f"Command output: {output}")

    # except (SerialConnectionError, LoginError) as e:
    #     print(f"Connection failed: {e}")
    # finally:
    #     putty.disconnect()

    # Example 2: Using SerialConfig dataclass
    print("\n=== Example 2: SerialConfig Usage ===")
    config = SerialConfig(
        enabled=True, comport="COM4", baudrate=921600, username="zeekr", password="Aa123123", timeout=5.0
    )

    # with PuttyHelper() as putty:
    #     try:
    #         putty.connect(config)

    #         # Execute multiple commands
    #         commands = ["uname -a", "ps aux", "df -h"]
    #         for cmd in commands:
    #             result = putty.execute_command(cmd, wait_time=1.0)
    #             print(f"'{cmd}' output: {len(result)} lines")

    #     except Exception as e:
    #         print(f"Error: {e}")

    # # Example 3: Pattern matching and trace monitoring
    # print("\n=== Example 3: Pattern Matching ===")
    # with PuttyHelper() as putty:
    #     try:
    #         putty.connect(config)

    #         # Wait for specific pattern
    #         success, groups = putty.wait_for_trace(
    #             pattern=r"Result:\s*(.*)",
    #             command="bosch_swdl -b normal",
    #             timeout=30.0
    #         )

    #         if success and groups:
    #             print(f"Pattern matched! Result: {groups[0]}")
    #         else:
    #             print("Pattern not found within timeout")

    #         # Multiple pattern matching examples
    #         patterns = [
    #             (r"(\d+)\s+processes", "ps aux"),
    #             (r"Filesystem\s+(\S+)", "df -h"),
    #             (r"Linux\s+(\S+)", "uname -a")
    #         ]

    #         for pattern, cmd in patterns:
    #             success, groups = putty.wait_for_trace(pattern, cmd, timeout=10.0)
    #             if success:
    #                 print(f"Found: {groups}")

    #     except Exception as e:
    #         print(f"Pattern matching error: {e}")

    # Example 4: Trace monitoring with context manager
    print("\n=== Example 4: Trace Monitoring ===")
    with SerialClient() as putty:
        try:
            putty.connect(config)

            # Monitor traces during command execution
            with putty.monitor_traces():
                putty.send_command("dmesg | tail -10")
                time.sleep(2)

                # Get all monitored traces
                traces = putty.get_monitored_traces()
                print(f"Monitored {len(traces)} trace lines")
                for i, trace in enumerate(traces[:5]):  # Show first 5
                    print(f"  {i + 1}: {trace}")

        except Exception as e:
            print(f"Monitoring error: {e}")

    # # Example 5: Manual trace monitoring
    # print("\n=== Example 5: Manual Monitoring ===")
    # with PuttyHelper() as putty:
    #     try:
    #         putty.connect(config)

    #         # Enable monitoring manually
    #         putty.enable_monitor()

    #         # Execute commands while monitoring
    #         putty.send_command("cat /proc/cpuinfo | grep processor")
    #         time.sleep(1)
    #         putty.send_command("free -m")
    #         time.sleep(1)

    #         # Get traces and disable monitoring
    #         traces = putty.get_monitored_traces()
    #         putty.disable_monitor()

    #         print(f"Captured {len(traces)} lines during monitoring")

    #     except Exception as e:
    #         print(f"Manual monitoring error: {e}")

    # # Example 6: Error handling and state management
    # print("\n=== Example 6: Error Handling ===")
    # putty = PuttyHelper()

    # # Try connecting to invalid port
    # invalid_config = SerialConfig(
    #     enabled=True,
    #     comport="COM999",  # Invalid port
    #     baudrate=115200,
    #     username="test",
    #     password="test"
    # )

    # try:
    #     putty.connect(invalid_config)
    # except SerialConnectionError as e:
    #     print(f"Expected connection error: {e}")
    #     print(f"Current state: {putty.state}")

    # # Try operations without connection
    # try:
    #     putty.send_command("test")
    # except SerialConnectionError as e:
    #     print(f"Expected operation error: {e}")

    # # Example 7: Configuration from dictionary vs dataclass
    # print("\n=== Example 7: Configuration Comparison ===")

    # # From dictionary
    # dict_config = {
    #     "putty_enabled": True,
    #     "putty_comport": "COM4",
    #     "putty_baudrate": 921600,
    #     "putty_username": "admin",
    #     "putty_password": "secret"
    # }

    # config_from_dict = SerialConfig.from_dict(dict_config)
    # print(f"From dict: {config_from_dict}")

    # # Direct dataclass creation
    # direct_config = SerialConfig(
    #     enabled=True,
    #     comport="COM4",
    #     baudrate=921600,
    #     username="admin",
    #     password="secret"
    # )
    # print(f"Direct: {direct_config}")
    # print(f"Configs equal: {config_from_dict == direct_config}")

    # # Example 8: Advanced pattern matching scenarios
    # print("\n=== Example 8: Advanced Patterns ===")
    # with PuttyHelper() as putty:
    #     try:
    #         putty.connect(config)

    #         # Complex patterns with multiple groups
    #         patterns_advanced = [
    #             (r"(\w+)\s+(\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)", "top -bn1 | head -5"),
    #             (r"total\s+(\d+)", "wc -l /etc/passwd"),
    #             (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", "ip addr show")
    #         ]

    #         for pattern, cmd in patterns_advanced:
    #             success, groups = putty.wait_for_trace(pattern, cmd, timeout=15.0)
    #             if success:
    #                 print(f"Pattern: {pattern}")
    #                 print(f"Groups: {groups}")
    #             else:
    #                 print(f"No match for: {pattern}")

    #     except Exception as e:
    #         print(f"Advanced pattern error: {e}")

    # # Example 9: Performance timing
    # print("\n=== Example 9: Performance Timing ===")
    # with PuttyHelper() as putty:
    #     try:
    #         putty.connect(config)

    #         # Time command execution
    #         start_time = time.time()
    #         output = putty.execute_command("sleep 2 && echo 'Done'", wait_time=3.0)
    #         elapsed = time.time() - start_time

    #         print(f"Command took {elapsed:.2f} seconds")
    #         print(f"Output: {output}")

    #         # Time pattern matching
    #         start_time = time.time()
    #         success, groups = putty.wait_for_trace(
    #             r"Done",
    #             "echo 'Processing...' && sleep 1 && echo 'Done'",
    #             timeout=5.0
    #         )
    #         elapsed = time.time() - start_time

    #         print(f"Pattern matching took {elapsed:.2f} seconds")
    #         print(f"Success: {success}, Groups: {groups}")

    #     except Exception as e:
    #         print(f"Performance test error: {e}")

    # print("\n=== All Examples Completed ===")

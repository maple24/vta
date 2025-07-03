# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
Enhanced ADB Client for Android Debug Bridge operations.

This module provides a comprehensive and user-friendly interface for ADB operations
including device management, UI interactions, and system operations.
"""

import subprocess
import re
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
from loguru import logger

from .base import (
    BaseClient, ClientConfig, VTAError, ConnectionError, 
    OperationError, ValidationError, TimeoutError,
    retry_on_failure, validate_connection, log_operation
)


@dataclass
class TouchEvent:
    """Represents a touch event with coordinates and optional metadata."""
    x: int
    y: int
    pressure: float = 1.0
    duration: int = 100


@dataclass
class SwipeGesture:
    """Represents a swipe gesture with start/end points and timing."""
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    duration: int = 500
    steps: int = 10


class ADBClient(BaseClient):
    """
    Enhanced Android Debug Bridge client with comprehensive device control capabilities.
    
    Features:
    - Device connection management
    - UI automation (tap, swipe, long press, multi-touch)
    - App management (install, uninstall, launch)
    - System information retrieval
    - File operations
    - Screenshot and screen recording
    - Performance monitoring
    
    Example:
        ```python
        # Basic usage
        adb = ADBClient(ClientConfig(device_id="emulator-5554"))
        adb.tap(100, 200)
        
        # With context manager
        with ADBClient(ClientConfig(device_id="192.168.1.100:5555")) as adb:
            adb.install_app("/path/to/app.apk")
            adb.launch_app("com.example.app")
        ```
    """
    
    def __init__(self, config: Optional[ClientConfig] = None):
        """
        Initialize ADB client.
        
        Args:
            config: Client configuration including device_id and adb_path
        """
        super().__init__(config)
        
        self.adb_path = self.config.extra_config.get("adb_path", "adb")
        self.device_id = self.config.device_id
        
        # Validate ADB executable
        self._validate_adb_executable()
        
        # Device info cache
        self._device_info_cache = {}
    
    def _validate_adb_executable(self):
        """Validate that ADB executable is available."""
        try:
            result = subprocess.run(
                [self.adb_path, "version"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode != 0:
                raise VTAError(f"ADB executable not working: {result.stderr}")
                
            logger.info(f"ADB version: {result.stdout.strip()}")
            
        except subprocess.TimeoutExpired:
            raise TimeoutError("ADB version check timed out")
        except FileNotFoundError:
            raise VTAError(f"ADB executable not found at: {self.adb_path}")
    
    def connect(self) -> bool:
        """
        Connect to the specified device.
        
        Returns:
            bool: True if connection successful
            
        Raises:
            ConnectionError: If connection fails
        """
        if not self.device_id:
            # Try to get default device
            devices = self.list_devices()
            if not devices:
                raise ConnectionError("No ADB devices found")
            
            if len(devices) == 1:
                self.device_id = devices[0]["id"]
                logger.info(f"Auto-selected device: {self.device_id}")
            else:
                raise ConnectionError(f"Multiple devices found, please specify device_id: {[d['id'] for d in devices]}")
        
        # Test connection
        try:
            result = self._execute_adb_command("shell echo 'test'")
            if result and "test" in result:
                self._connected = True
                logger.info(f"Successfully connected to device: {self.device_id}")
                
                # Cache device info
                self._device_info_cache = self.get_device_info()
                return True
            else:
                raise ConnectionError(f"Failed to connect to device: {self.device_id}")
                
        except Exception as e:
            raise ConnectionError(f"Connection failed: {e}")
    
    def disconnect(self) -> bool:
        """
        Disconnect from the device.
        
        Returns:
            bool: True if disconnection successful
        """
        self._connected = False
        self._device_info_cache.clear()
        logger.info(f"Disconnected from device: {self.device_id}")
        return True
    
    def is_connected(self) -> bool:
        """
        Check if connected to a device.
        
        Returns:
            bool: True if connected
        """
        if not self._connected or not self.device_id:
            return False
        
        try:
            result = self._execute_adb_command("shell echo 'ping'", timeout=5)
            return result and "ping" in result
        except Exception:
            self._connected = False
            return False
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def _execute_adb_command(self, command: str, timeout: Optional[float] = None) -> Optional[str]:
        """
        Execute an ADB command.
        
        Args:
            command: ADB command to execute (without 'adb' prefix)
            timeout: Command timeout in seconds
            
        Returns:
            Command output as string, None if failed
            
        Raises:
            OperationError: If command execution fails
            TimeoutError: If command times out
        """
        timeout = timeout or self.config.timeout
        
        try:
            # Build full command
            if self.device_id:
                full_command = [self.adb_path, "-s", self.device_id] + command.split()
            else:
                full_command = [self.adb_path] + command.split()
            
            logger.debug(f"Executing ADB command: {' '.join(full_command)}")
            
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() or result.stdout.strip()
                raise OperationError(f"ADB command failed: {error_msg}")
            
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"ADB command timed out after {timeout}s: {command}")
        except Exception as e:
            raise OperationError(f"Failed to execute ADB command '{command}': {e}")
    
    # Device Information Methods
    def list_devices(self) -> List[Dict[str, str]]:
        """
        List all connected ADB devices.
        
        Returns:
            List of device dictionaries with id and status
        """
        try:
            result = subprocess.run(
                [self.adb_path, "devices"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            devices = []
            for line in result.stdout.split('\n')[1:]:  # Skip header
                line = line.strip()
                if line and not line.startswith('*'):
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        devices.append({
                            "id": parts[0],
                            "status": parts[1]
                        })
            
            return devices
            
        except Exception as e:
            logger.error(f"Failed to list devices: {e}")
            return []
    
    @validate_connection
    def get_device_info(self) -> Dict[str, Any]:
        """
        Get comprehensive device information.
        
        Returns:
            Dictionary with device properties and system info
        """
        info = {}
        
        try:
            # Basic device properties
            properties = [
                ("brand", "ro.product.brand"),
                ("model", "ro.product.model"),
                ("manufacturer", "ro.product.manufacturer"),
                ("android_version", "ro.build.version.release"),
                ("sdk_version", "ro.build.version.sdk"),
                ("serial", "ro.serialno"),
                ("device_name", "ro.product.device")
            ]
            
            for prop_name, prop_key in properties:
                result = self._execute_adb_command(f"shell getprop {prop_key}")
                if result:
                    info[prop_name] = result.strip()
            
            # Screen dimensions
            screen_size = self.get_screen_size()
            if screen_size:
                info["screen_width"], info["screen_height"] = screen_size
            
            # Battery info
            battery_info = self.get_battery_info()
            if battery_info:
                info["battery"] = battery_info
            
            # Storage info
            storage_info = self.get_storage_info()
            if storage_info:
                info["storage"] = storage_info
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get device info: {e}")
            return {}
    
    @validate_connection
    def get_screen_size(self) -> Optional[Tuple[int, int]]:
        """
        Get device screen dimensions.
        
        Returns:
            Tuple of (width, height) or None if failed
        """
        try:
            result = self._execute_adb_command("shell wm size")
            if result:
                # Parse output like "Physical size: 1080x1920"
                match = re.search(r'(\d+)x(\d+)', result)
                if match:
                    width, height = int(match.group(1)), int(match.group(2))
                    logger.debug(f"Screen size: {width}x{height}")
                    return width, height
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get screen size: {e}")
            return None
    
    # UI Interaction Methods
    @validate_connection
    @log_operation
    def tap(self, x: int, y: int, duration: int = 100) -> bool:
        """
        Perform a tap gesture at specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate  
            duration: Tap duration in milliseconds
            
        Returns:
            bool: True if successful
            
        Raises:
            ValidationError: If coordinates are invalid
        """
        self.validate_input(x=x, y=y, duration=duration)
        
        try:
            self._execute_adb_command(f"shell input tap {x} {y}")
            logger.info(f"Tapped at ({x}, {y})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to tap at ({x}, {y}): {e}")
            return False
    
    @validate_connection  
    @log_operation
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, 
              duration: int = 500) -> bool:
        """
        Perform a swipe gesture.
        
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            duration: Swipe duration in milliseconds
            
        Returns:
            bool: True if successful
        """
        self.validate_input(
            start_x=start_x, start_y=start_y,
            end_x=end_x, end_y=end_y, duration=duration
        )
        
        try:
            self._execute_adb_command(
                f"shell input swipe {start_x} {start_y} {end_x} {end_y} {duration}"
            )
            logger.info(f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to swipe: {e}")
            return False
    
    @validate_connection
    @log_operation  
    def long_press(self, x: int, y: int, duration: int = 2000) -> bool:
        """
        Perform a long press gesture.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Long press duration in milliseconds
            
        Returns:
            bool: True if successful
        """
        self.validate_input(x=x, y=y, duration=duration)
        
        try:
            # Long press is implemented as a swipe with same start/end coordinates
            self._execute_adb_command(f"shell input swipe {x} {y} {x} {y} {duration}")
            logger.info(f"Long pressed at ({x}, {y}) for {duration}ms")
            return True
            
        except Exception as e:
            logger.error(f"Failed to long press at ({x}, {y}): {e}")
            return False
    
    def validate_input(self, **kwargs) -> bool:
        """
        Validate input parameters for ADB operations.
        
        Raises:
            ValidationError: If validation fails
        """
        if not super().validate_input(**kwargs):
            return False
        
        # Validate coordinates against screen size if available
        if "x" in kwargs or "y" in kwargs:
            screen_size = self.get_screen_size()
            if screen_size:
                width, height = screen_size
                
                if "x" in kwargs and not (0 <= kwargs["x"] <= width):
                    raise ValidationError(f"X coordinate {kwargs['x']} out of screen bounds (0-{width})")
                
                if "y" in kwargs and not (0 <= kwargs["y"] <= height):
                    raise ValidationError(f"Y coordinate {kwargs['y']} out of screen bounds (0-{height})")
        
        # Validate duration
        if "duration" in kwargs and kwargs["duration"] < 0:
            raise ValidationError("Duration must be non-negative")
        
        return True

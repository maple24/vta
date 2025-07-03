# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
Hardware Control Client for relay, power supply, and other hardware operations.

This module provides a unified interface for various hardware control operations
including relay control, power supply management, and hardware automation.
"""

import os
import time
from typing import Optional, Dict, Any, List
from loguru import logger

try:
    import serial
except ImportError:
    logger.warning("pyserial not installed. Serial operations may not be available.")
    serial = None

from .base import (
    BaseClient, ClientConfig, VTAError, ConnectionError,
    OperationError, ValidationError,
    validate_connection, log_operation
)


class HardwareClient(BaseClient):
    """
    Unified hardware control client for relay, power supply, and hardware automation.
    
    Features:
    - Relay control (Cleware and other USB relay modules)
    - Power supply management
    - Serial communication with hardware devices
    - Hardware status monitoring
    - Safety interlocks and validation
    
    Example:
        ```python
        # Basic relay control
        hw = HardwareClient(ClientConfig(extra_config={"device_type": "relay"}))
        hw.set_relay_state(1, True)  # Turn on relay 1
        
        # Power supply control
        hw = HardwareClient(ClientConfig(extra_config={"device_type": "power_supply"}))
        hw.set_voltage(12.0)
        hw.set_current_limit(2.0)
        ```
    """
    
    def __init__(self, config: Optional[ClientConfig] = None):
        """
        Initialize Hardware client.
        
        Args:
            config: Client configuration including device_type and connection params
        """
        super().__init__(config)
        
        self.device_type = self.config.extra_config.get("device_type", "relay")
        self.serial_port = self.config.extra_config.get("serial_port", "COM1")
        self.baud_rate = self.config.extra_config.get("baud_rate", 9600)
        
        self._serial_connection = None
        self._cleware_executor = None
        self._device_enabled = False
        
        # Initialize based on device type
        self._initialize_device()
    
    def _initialize_device(self):
        """Initialize the specific hardware device based on type."""
        try:
            if self.device_type == "relay":
                self._initialize_relay()
            elif self.device_type == "power_supply":
                self._initialize_power_supply()
            elif self.device_type == "serial":
                self._initialize_serial()
            else:
                logger.warning(f"Unknown device type: {self.device_type}")
        except Exception as e:
            logger.error(f"Failed to initialize {self.device_type} device: {e}")
    
    def _initialize_relay(self):
        """Initialize relay control."""
        try:
            # Try to initialize Cleware USB relay
            self._initialize_cleware()
        except Exception as e:
            logger.warning(f"Cleware initialization failed: {e}")
            # Fallback to serial relay control
            self._initialize_serial()
    
    def _initialize_cleware(self):
        """Initialize Cleware USB relay control."""
        try:
            # Import Cleware library if available
            cleware_path = self.config.extra_config.get("cleware_path", "vta/bin/cleware")
            if os.path.exists(cleware_path):
                self._cleware_executor = cleware_path
                logger.info("Cleware relay controller initialized")
            else:
                raise FileNotFoundError("Cleware executables not found")
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Cleware: {e}")
    
    def _initialize_power_supply(self):
        """Initialize power supply control."""
        if serial is None:
            raise VTAError("pyserial is required for power supply control")
        
        # Power supply specific initialization
        self._initialize_serial()
    
    def _initialize_serial(self):
        """Initialize serial communication."""
        if serial is None:
            raise VTAError("pyserial is required for serial communication")
        
        try:
            self._serial_connection = serial.Serial(
                port=self.serial_port,
                baudrate=self.baud_rate,
                timeout=self.config.timeout
            )
            logger.info(f"Serial connection initialized on {self.serial_port}")
        except Exception as e:
            raise ConnectionError(f"Failed to initialize serial connection: {e}")
    
    def connect(self) -> bool:
        """
        Connect to the hardware device.
        
        Returns:
            bool: True if connection successful
        """
        try:
            if self.device_type == "relay" and self._cleware_executor:
                # Test Cleware connection
                result = self._execute_cleware_command("list")
                if result is not None:
                    self._connected = True
                    self._device_enabled = True
                    logger.info("Connected to Cleware relay")
                    return True
            
            elif self._serial_connection:
                if not self._serial_connection.is_open:
                    self._serial_connection.open()
                
                # Test serial connection
                if self._test_serial_communication():
                    self._connected = True
                    self._device_enabled = True
                    logger.info(f"Connected to {self.device_type} via serial")
                    return True
            
            return False
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {self.device_type}: {e}")
    
    def disconnect(self) -> bool:
        """
        Disconnect from the hardware device.
        
        Returns:
            bool: True if disconnection successful
        """
        try:
            if self._serial_connection and self._serial_connection.is_open:
                self._serial_connection.close()
            
            self._connected = False
            self._device_enabled = False
            logger.info(f"Disconnected from {self.device_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
            return False
    
    def is_connected(self) -> bool:
        """
        Check if connected to the hardware device.
        
        Returns:
            bool: True if connected
        """
        if not self._connected:
            return False
        
        try:
            if self._serial_connection:
                return self._serial_connection.is_open
            elif self._cleware_executor:
                # Test with a quick command
                result = self._execute_cleware_command("list")
                return result is not None
            
            return False
            
        except Exception:
            self._connected = False
            return False
    
    # Relay Control Methods
    @validate_connection
    @log_operation
    def set_relay_state(self, relay_number: int, state: bool) -> bool:
        """
        Set the state of a specific relay.
        
        Args:
            relay_number: Relay number (1-based)
            state: True to turn on, False to turn off
            
        Returns:
            bool: True if operation successful
        """
        self.validate_input(relay_number=relay_number)
        
        try:
            if self._cleware_executor:
                return self._set_cleware_relay(relay_number, state)
            elif self._serial_connection:
                return self._set_serial_relay(relay_number, state)
            else:
                raise OperationError("No relay control method available")
                
        except Exception as e:
            raise OperationError(f"Failed to set relay {relay_number} to {state}: {e}")
    
    def _set_cleware_relay(self, relay_number: int, state: bool) -> bool:
        """Set Cleware relay state."""
        try:
            action = "on" if state else "off"
            command = f"switch {relay_number} {action}"
            result = self._execute_cleware_command(command)
            
            if result is not None:
                logger.info(f"Relay {relay_number} turned {action}")
                return True
            else:
                return False
                
        except Exception as e:
            raise OperationError(f"Cleware relay control failed: {e}")
    
    def _set_serial_relay(self, relay_number: int, state: bool) -> bool:
        """Set serial relay state."""
        try:
            # Generic serial relay protocol (customize as needed)
            command = f"REL{relay_number}:{1 if state else 0}\r\n"
            self._serial_connection.write(command.encode())
            
            # Read response
            response = self._serial_connection.readline().decode().strip()
            
            if "OK" in response or "ACK" in response:
                logger.info(f"Serial relay {relay_number} set to {state}")
                return True
            else:
                return False
                
        except Exception as e:
            raise OperationError(f"Serial relay control failed: {e}")
    
    @validate_connection
    def get_relay_state(self, relay_number: int) -> Optional[bool]:
        """
        Get the current state of a relay.
        
        Args:
            relay_number: Relay number (1-based)
            
        Returns:
            bool: True if on, False if off, None if unknown
        """
        try:
            if self._cleware_executor:
                return self._get_cleware_relay_state(relay_number)
            elif self._serial_connection:
                return self._get_serial_relay_state(relay_number)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get relay {relay_number} state: {e}")
            return None
    
    def _get_cleware_relay_state(self, relay_number: int) -> Optional[bool]:
        """Get Cleware relay state."""
        try:
            command = f"status {relay_number}"
            result = self._execute_cleware_command(command)
            
            if result and "on" in result.lower():
                return True
            elif result and "off" in result.lower():
                return False
            else:
                return None
                
        except Exception:
            return None
    
    def _get_serial_relay_state(self, relay_number: int) -> Optional[bool]:
        """Get serial relay state."""
        try:
            command = f"REL{relay_number}?\r\n"
            self._serial_connection.write(command.encode())
            
            response = self._serial_connection.readline().decode().strip()
            
            if "1" in response or "ON" in response.upper():
                return True
            elif "0" in response or "OFF" in response.upper():
                return False
            else:
                return None
                
        except Exception:
            return None
    
    @validate_connection
    @log_operation
    def set_all_relays(self, state: bool) -> bool:
        """
        Set all relays to the same state.
        
        Args:
            state: True to turn all on, False to turn all off
            
        Returns:
            bool: True if operation successful
        """
        try:
            # Get number of available relays
            relay_count = self.get_relay_count()
            
            success = True
            for i in range(1, relay_count + 1):
                if not self.set_relay_state(i, state):
                    success = False
            
            return success
            
        except Exception as e:
            raise OperationError(f"Failed to set all relays: {e}")
    
    def get_relay_count(self) -> int:
        """
        Get the number of available relays.
        
        Returns:
            int: Number of relays
        """
        # Default to 8 relays, can be configured
        return self.config.extra_config.get("relay_count", 8)
    
    # Power Supply Methods (if device_type is power_supply)
    @validate_connection
    @log_operation
    def set_voltage(self, voltage: float) -> bool:
        """
        Set output voltage for power supply.
        
        Args:
            voltage: Voltage to set
            
        Returns:
            bool: True if successful
        """
        if self.device_type != "power_supply":
            raise ValidationError("Power supply operations require device_type='power_supply'")
        
        try:
            command = f"VOLT {voltage:.2f}\r\n"
            return self._send_power_supply_command(command)
            
        except Exception as e:
            raise OperationError(f"Failed to set voltage: {e}")
    
    @validate_connection
    @log_operation
    def set_current_limit(self, current: float) -> bool:
        """
        Set current limit for power supply.
        
        Args:
            current: Current limit to set
            
        Returns:
            bool: True if successful
        """
        if self.device_type != "power_supply":
            raise ValidationError("Power supply operations require device_type='power_supply'")
        
        try:
            command = f"CURR {current:.3f}\r\n"
            return self._send_power_supply_command(command)
            
        except Exception as e:
            raise OperationError(f"Failed to set current limit: {e}")
    
    def _send_power_supply_command(self, command: str) -> bool:
        """Send command to power supply."""
        try:
            if not self._serial_connection:
                return False
            
            self._serial_connection.write(command.encode())
            response = self._serial_connection.readline().decode().strip()
            
            return "OK" in response or "ACK" in response
            
        except Exception:
            return False
    
    # Utility Methods
    def _execute_cleware_command(self, command: str) -> Optional[str]:
        """Execute a Cleware command."""
        try:
            if not self._cleware_executor:
                return None
            
            import subprocess
            
            cmd = f"{self._cleware_executor}/USBswitchCmd.exe {command}"
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"Cleware command failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Cleware command execution failed: {e}")
            return None
    
    def _test_serial_communication(self) -> bool:
        """Test serial communication."""
        try:
            if not self._serial_connection:
                return False
            
            # Send a test command
            test_command = "*IDN?\r\n"
            self._serial_connection.write(test_command.encode())
            
            # Try to read response
            response = self._serial_connection.readline().decode().strip()
            
            return len(response) > 0
            
        except Exception:
            return False
    
    def validate_input(self, **kwargs) -> bool:
        """
        Validate input parameters for hardware operations.
        
        Raises:
            ValidationError: If validation fails
        """
        if not super().validate_input(**kwargs):
            return False
        
        # Validate relay number
        if "relay_number" in kwargs:
            relay_num = kwargs["relay_number"]
            max_relays = self.get_relay_count()
            if not (1 <= relay_num <= max_relays):
                raise ValidationError(f"Relay number {relay_num} out of range (1-{max_relays})")
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive hardware status.
        
        Returns:
            Status dictionary
        """
        status = super().get_status()
        
        try:
            status.update({
                "device_type": self.device_type,
                "device_enabled": self._device_enabled,
                "serial_port": getattr(self._serial_connection, 'port', None) if self._serial_connection else None,
                "cleware_available": self._cleware_executor is not None
            })
            
            # Add relay states if it's a relay device
            if self.device_type == "relay" and self.is_connected():
                relay_states = {}
                for i in range(1, self.get_relay_count() + 1):
                    try:
                        state = self.get_relay_state(i)
                        relay_states[f"relay_{i}"] = state
                    except Exception:
                        relay_states[f"relay_{i}"] = "unknown"
                
                status["relay_states"] = relay_states
                
        except Exception as e:
            status["status_error"] = str(e)
        
        return status

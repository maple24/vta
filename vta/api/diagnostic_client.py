# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
Enhanced Diagnostic Client for Socket and Serial communications.

This module provides a comprehensive interface for diagnostic operations
using socket and serial communications for DLT logs and other diagnostic protocols.
"""

import socket
import time
import threading
import struct
from typing import Optional, Dict, Any, List, Union, Callable
from dataclasses import dataclass
from loguru import logger

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    logger.warning("pyserial not installed. Serial operations may not be available.")
    SERIAL_AVAILABLE = False
    serial = None

from .base import (
    BaseClient, ClientConfig, VTAError, ConnectionError,
    OperationError, ValidationError, TimeoutError,
    validate_connection, log_operation
)


@dataclass
class DLTMessage:
    """Represents a DLT (Diagnostic Log and Trace) message."""
    timestamp: float
    app_id: str
    context_id: str
    message_type: str
    log_level: str
    payload: str
    raw_data: bytes


@dataclass
class SerialConfig:
    """Configuration for serial communication."""
    port: str
    baudrate: int = 115200
    bytesize: int = 8
    parity: str = 'N'
    stopbits: int = 1
    timeout: float = 1.0
    xonxoff: bool = False
    rtscts: bool = False
    dsrdtr: bool = False


class DiagnosticClient(BaseClient):
    """
    Enhanced diagnostic client for socket and serial communications.
    
    Features:
    - Socket-based DLT message reception
    - Serial port communication for diagnostics
    - Real-time message parsing and filtering
    - Message logging and analysis
    - Multi-threaded message reception
    
    Example:
        ```python
        # Socket-based DLT reception
        config = ClientConfig(extra_config={
            "mode": "socket",
            "socket_host": "192.168.1.100",
            "socket_port": 3490
        })
        diag = DiagnosticClient(config)
        diag.start_dlt_reception()
        
        # Serial communication
        config = ClientConfig(extra_config={
            "mode": "serial",
            "serial_port": "COM1",
            "baudrate": 115200
        })
        diag = DiagnosticClient(config)
        diag.send_command("AT+VERSION")
        ```
    """
    
    def __init__(self, config: Optional[ClientConfig] = None):
        """
        Initialize Diagnostic client.
        
        Args:
            config: Client configuration including mode and connection details
        """
        super().__init__(config)
        
        self.mode = self.config.extra_config.get("mode", "socket")
        self._socket = None
        self._serial = None
        self._reception_thread = None
        self._reception_active = False
        self._message_handlers = []
        self._received_messages = []
        
        # Socket configuration
        self.socket_host = self.config.extra_config.get("socket_host", "localhost")
        self.socket_port = self.config.extra_config.get("socket_port", 3490)
        
        # Serial configuration
        if SERIAL_AVAILABLE:
            self.serial_config = SerialConfig(
                port=self.config.extra_config.get("serial_port", "COM1"),
                baudrate=self.config.extra_config.get("baudrate", 115200),
                timeout=self.config.extra_config.get("serial_timeout", 1.0)
            )
        else:
            self.serial_config = None
    
    def connect(self) -> bool:
        """
        Establish connection based on configured mode.
        
        Returns:
            bool: True if connection successful
            
        Raises:
            ConnectionError: If connection fails
        """
        try:
            if self.mode == "socket":
                return self._connect_socket()
            elif self.mode == "serial":
                return self._connect_serial()
            else:
                raise ValidationError(f"Unsupported mode: {self.mode}")
                
        except Exception as e:
            raise ConnectionError(f"Failed to connect in {self.mode} mode: {e}")
    
    def disconnect(self) -> bool:
        """
        Close connection and cleanup resources.
        
        Returns:
            bool: True if disconnection successful
        """
        try:
            # Stop reception if active
            if self._reception_active:
                self.stop_dlt_reception()
            
            # Close socket connection
            if self._socket:
                self._socket.close()
                self._socket = None
            
            # Close serial connection
            if self._serial and SERIAL_AVAILABLE:
                self._serial.close()
                self._serial = None
            
            self._connected = False
            logger.info(f"Disconnected from {self.mode} mode")
            return True
            
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
            return False
    
    def is_connected(self) -> bool:
        """
        Check if connected.
        
        Returns:
            bool: True if connected
        """
        if not self._connected:
            return False
        
        try:
            if self.mode == "socket" and self._socket:
                return True
            elif self.mode == "serial" and self._serial:
                return self._serial.is_open if SERIAL_AVAILABLE else False
            else:
                return False
        except Exception:
            self._connected = False
            return False
    
    def _connect_socket(self) -> bool:
        """Connect via socket for DLT reception."""
        try:
            logger.info(f"Connecting to DLT socket at {self.socket_host}:{self.socket_port}")
            
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.config.timeout)
            self._socket.connect((self.socket_host, self.socket_port))
            
            self._connected = True
            logger.info("Successfully connected to DLT socket")
            return True
            
        except socket.timeout:
            raise TimeoutError("Socket connection timed out")
        except socket.error as e:
            raise ConnectionError(f"Socket connection failed: {e}")
    
    def _connect_serial(self) -> bool:
        """Connect via serial port."""
        if not SERIAL_AVAILABLE:
            raise VTAError("pyserial not installed. Install with: pip install pyserial")
        
        if not self.serial_config:
            raise ValidationError("Serial configuration not available")
        
        try:
            logger.info(f"Connecting to serial port {self.serial_config.port}")
            
            self._serial = serial.Serial(
                port=self.serial_config.port,
                baudrate=self.serial_config.baudrate,
                bytesize=self.serial_config.bytesize,
                parity=self.serial_config.parity,
                stopbits=self.serial_config.stopbits,
                timeout=self.serial_config.timeout,
                xonxoff=self.serial_config.xonxoff,
                rtscts=self.serial_config.rtscts,
                dsrdtr=self.serial_config.dsrdtr
            )
            
            self._connected = True
            logger.info(f"Successfully connected to serial port {self.serial_config.port}")
            return True
            
        except Exception as e:
            raise ConnectionError(f"Serial connection failed: {e}")
    
    # Socket-based DLT Operations
    @validate_connection
    @log_operation
    def start_dlt_reception(self, message_handler: Optional[Callable[[DLTMessage], None]] = None) -> bool:
        """
        Start DLT message reception in a background thread.
        
        Args:
            message_handler: Optional callback for processing received messages
            
        Returns:
            bool: True if reception started successfully
        """
        if self.mode != "socket":
            raise ValidationError("DLT reception requires socket mode")
        
        if self._reception_active:
            logger.warning("DLT reception already active")
            return True
        
        try:
            if message_handler:
                self.add_message_handler(message_handler)
            
            self._reception_active = True
            self._reception_thread = threading.Thread(
                target=self._dlt_reception_loop,
                daemon=True
            )
            self._reception_thread.start()
            
            logger.info("DLT reception started")
            return True
            
        except Exception as e:
            self._reception_active = False
            raise OperationError(f"Failed to start DLT reception: {e}")
    
    @validate_connection
    @log_operation
    def stop_dlt_reception(self) -> bool:
        """
        Stop DLT message reception.
        
        Returns:
            bool: True if reception stopped successfully
        """
        if not self._reception_active:
            return True
        
        try:
            self._reception_active = False
            
            if self._reception_thread and self._reception_thread.is_alive():
                self._reception_thread.join(timeout=5.0)
            
            logger.info("DLT reception stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping DLT reception: {e}")
            return False
    
    def _dlt_reception_loop(self):
        """Main loop for receiving DLT messages."""
        buffer = b""
        
        while self._reception_active and self._socket:
            try:
                # Set socket to non-blocking for graceful shutdown
                self._socket.settimeout(1.0)
                
                data = self._socket.recv(4096)
                if not data:
                    logger.warning("Socket closed by remote host")
                    break
                
                buffer += data
                
                # Parse DLT messages from buffer
                while len(buffer) >= 4:  # Minimum DLT header size
                    message, consumed = self._parse_dlt_message(buffer)
                    if message:
                        self._handle_dlt_message(message)
                        buffer = buffer[consumed:]
                    else:
                        break
                        
            except socket.timeout:
                continue  # Check if reception should continue
            except socket.error as e:
                logger.error(f"Socket error in reception loop: {e}")
                break
            except Exception as e:
                logger.error(f"Unexpected error in reception loop: {e}")
                break
        
        self._reception_active = False
    
    def _parse_dlt_message(self, buffer: bytes) -> tuple[Optional[DLTMessage], int]:
        """
        Parse a DLT message from buffer.
        
        Args:
            buffer: Raw bytes buffer
            
        Returns:
            Tuple of (DLTMessage or None, bytes consumed)
        """
        try:
            if len(buffer) < 4:
                return None, 0
            
            # DLT header pattern (simplified)
            # This is a basic implementation - real DLT parsing is more complex
            header_pattern = struct.unpack(">HH", buffer[:4])
            message_length = header_pattern[1]
            
            if len(buffer) < message_length:
                return None, 0
            
            # Extract message data
            message_data = buffer[:message_length]
            
            # Parse basic DLT fields (simplified)
            message = DLTMessage(
                timestamp=time.time(),
                app_id="APP",  # Would be parsed from actual DLT header
                context_id="CTX",  # Would be parsed from actual DLT header
                message_type="LOG",
                log_level="INFO",
                payload=message_data[4:].decode('utf-8', errors='ignore'),
                raw_data=message_data
            )
            
            return message, message_length
            
        except Exception as e:
            logger.error(f"Error parsing DLT message: {e}")
            return None, 1  # Skip one byte and try again
    
    def _handle_dlt_message(self, message: DLTMessage):
        """Handle a received DLT message."""
        # Store message
        self._received_messages.append(message)
        
        # Keep only recent messages to prevent memory issues
        if len(self._received_messages) > 10000:
            self._received_messages = self._received_messages[-5000:]
        
        # Call registered handlers
        for handler in self._message_handlers:
            try:
                handler(message)
            except Exception as e:
                logger.error(f"Error in message handler: {e}")
    
    def add_message_handler(self, handler: Callable[[DLTMessage], None]):
        """Add a message handler for DLT messages."""
        self._message_handlers.append(handler)
    
    def remove_message_handler(self, handler: Callable[[DLTMessage], None]):
        """Remove a message handler."""
        if handler in self._message_handlers:
            self._message_handlers.remove(handler)
    
    def get_recent_messages(self, count: int = 100) -> List[DLTMessage]:
        """Get recent DLT messages."""
        return self._received_messages[-count:]
    
    def filter_messages(self, app_id: Optional[str] = None, 
                       context_id: Optional[str] = None,
                       log_level: Optional[str] = None,
                       since: Optional[float] = None) -> List[DLTMessage]:
        """Filter received messages by criteria."""
        filtered = self._received_messages
        
        if app_id:
            filtered = [m for m in filtered if m.app_id == app_id]
        
        if context_id:
            filtered = [m for m in filtered if m.context_id == context_id]
        
        if log_level:
            filtered = [m for m in filtered if m.log_level == log_level]
        
        if since:
            filtered = [m for m in filtered if m.timestamp >= since]
        
        return filtered
    
    # Serial Operations
    @validate_connection
    @log_operation
    def send_command(self, command: str, expect_response: bool = True,
                    timeout: Optional[float] = None) -> Optional[str]:
        """
        Send a command via serial port.
        
        Args:
            command: Command string to send
            expect_response: Whether to wait for a response
            timeout: Response timeout
            
        Returns:
            Response string if expect_response is True
        """
        if self.mode != "serial":
            raise ValidationError("Serial commands require serial mode")
        
        if not self._serial:
            raise ConnectionError("Serial port not connected")
        
        timeout = timeout or self.config.timeout
        
        try:
            # Send command
            command_bytes = (command + '\r\n').encode('utf-8')
            self._serial.write(command_bytes)
            self._serial.flush()
            
            logger.debug(f"Sent serial command: {command}")
            
            if not expect_response:
                return None
            
            # Read response
            start_time = time.time()
            response = b""
            
            while time.time() - start_time < timeout:
                if self._serial.in_waiting > 0:
                    data = self._serial.read(self._serial.in_waiting)
                    response += data
                    
                    # Check for common terminators
                    if b'\n' in response or b'\r' in response:
                        break
                
                time.sleep(0.01)  # Small delay to prevent busy waiting
            
            response_str = response.decode('utf-8', errors='ignore').strip()
            logger.debug(f"Received serial response: {response_str}")
            
            return response_str
            
        except Exception as e:
            raise OperationError(f"Serial command failed: {e}")
    
    @validate_connection
    @log_operation
    def send_raw_data(self, data: Union[str, bytes]) -> bool:
        """
        Send raw data via serial port.
        
        Args:
            data: Data to send (string or bytes)
            
        Returns:
            bool: True if data sent successfully
        """
        if self.mode != "serial":
            raise ValidationError("Raw data sending requires serial mode")
        
        if not self._serial:
            raise ConnectionError("Serial port not connected")
        
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            self._serial.write(data)
            self._serial.flush()
            
            logger.debug(f"Sent raw data: {len(data)} bytes")
            return True
            
        except Exception as e:
            raise OperationError(f"Failed to send raw data: {e}")
    
    @validate_connection
    def read_available_data(self, timeout: Optional[float] = None) -> bytes:
        """
        Read all available data from serial port.
        
        Args:
            timeout: Read timeout
            
        Returns:
            Available data as bytes
        """
        if self.mode != "serial":
            raise ValidationError("Data reading requires serial mode")
        
        if not self._serial:
            raise ConnectionError("Serial port not connected")
        
        timeout = timeout or 1.0
        
        try:
            old_timeout = self._serial.timeout
            self._serial.timeout = timeout
            
            data = b""
            while True:
                chunk = self._serial.read(1024)
                if not chunk:
                    break
                data += chunk
            
            self._serial.timeout = old_timeout
            return data
            
        except Exception as e:
            raise OperationError(f"Failed to read data: {e}")
    
    # Utility Methods
    def get_connection_info(self) -> Dict[str, Any]:
        """Get information about the current connection."""
        info = {
            "mode": self.mode,
            "connected": self.is_connected(),
            "reception_active": self._reception_active
        }
        
        if self.mode == "socket":
            info.update({
                "socket_host": self.socket_host,
                "socket_port": self.socket_port
            })
        elif self.mode == "serial" and self.serial_config:
            info.update({
                "serial_port": self.serial_config.port,
                "baudrate": self.serial_config.baudrate
            })
        
        return info
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get reception statistics."""
        return {
            "total_messages": len(self._received_messages),
            "active_handlers": len(self._message_handlers),
            "reception_active": self._reception_active,
            "connection_mode": self.mode
        }

# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
Enhanced Agent Client for Agent Manager communication.

This module provides a comprehensive interface for communicating with
Agent Manager servers with enhanced error handling and user-friendly APIs.
"""

import socket
import json
import time
from typing import Optional, Dict, Any, Union
from loguru import logger

from .base import (
    BaseClient, ClientConfig, VTAError, ConnectionError,
    OperationError, TimeoutError,
    retry_on_failure, validate_connection, log_operation
)


class AgentClient(BaseClient):
    """
    Enhanced Agent Manager client for agent communication.
    
    Features:
    - Socket-based communication with Agent Manager
    - Automatic retry and error handling
    - JSON message serialization/deserialization
    - Connection health monitoring
    - Timeout management
    
    Example:
        ```python
        # Basic usage
        agent = AgentClient(ClientConfig(host="localhost", port=6666))
        response = agent.send_command({"action": "get_status"})
        
        # With context manager
        with AgentClient(ClientConfig(host="192.168.1.100", port=6666)) as agent:
            result = agent.execute_script("test_script.py")
        ```
    """
    
    def __init__(self, config: Optional[ClientConfig] = None):
        """
        Initialize Agent client.
        
        Args:
            config: Client configuration including host and port
        """
        super().__init__(config)
        
        self.host = self.config.host
        self.port = self.config.port or 6666
        self._socket = None
    
    def connect(self) -> bool:
        """
        Connect to the Agent Manager server.
        
        Returns:
            bool: True if connection successful
            
        Raises:
            ConnectionError: If connection fails
        """
        try:
            logger.info(f"Connecting to Agent Manager at {self.host}:{self.port}")
            
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.config.timeout)
            self._socket.connect((self.host, self.port))
            
            # Test connection with a ping
            test_response = self._send_message({"action": "ping"}, need_response=True)
            if test_response:
                self._connected = True
                logger.info(f"Successfully connected to Agent Manager at {self.host}:{self.port}")
                return True
            else:
                raise ConnectionError("Agent Manager did not respond to ping")
                
        except socket.timeout:
            raise TimeoutError(f"Connection to {self.host}:{self.port} timed out")
        except socket.error as e:
            raise ConnectionError(f"Failed to connect to {self.host}:{self.port}: {e}")
        except Exception as e:
            raise ConnectionError(f"Unexpected error connecting to Agent Manager: {e}")
    
    def disconnect(self) -> bool:
        """
        Disconnect from the Agent Manager server.
        
        Returns:
            bool: True if disconnection successful
        """
        if self._socket:
            try:
                self._socket.close()
            except Exception as e:
                logger.error(f"Error closing socket: {e}")
            finally:
                self._socket = None
        
        self._connected = False
        logger.info(f"Disconnected from Agent Manager at {self.host}:{self.port}")
        return True
    
    def is_connected(self) -> bool:
        """
        Check if connected to Agent Manager.
        
        Returns:
            bool: True if connected and responsive
        """
        if not self._connected or not self._socket:
            return False
        
        try:
            # Test with a quick ping
            response = self._send_message({"action": "ping"}, timeout=5, need_response=True)
            return response is not None
        except Exception:
            self._connected = False
            return False
    
    @validate_connection
    @retry_on_failure(max_retries=3, delay=1.0, exceptions=(socket.error, TimeoutError))
    def _send_message(self, message: Dict[str, Any], timeout: Optional[float] = None,
                     need_response: bool = True) -> Optional[Dict[str, Any]]:
        """
        Send a message to the Agent Manager.
        
        Args:
            message: Message to send as dictionary
            timeout: Message timeout in seconds
            need_response: Whether to wait for a response
            
        Returns:
            Response dictionary or None if no response needed
            
        Raises:
            OperationError: If message sending fails
            TimeoutError: If operation times out
        """
        timeout = timeout or self.config.timeout
        
        try:
            # Serialize message to JSON
            message_json = json.dumps(message)
            message_bytes = message_json.encode('utf-8')
            
            logger.debug(f"Sending message: {message_json}")
            
            # Send message
            self._socket.sendall(message_bytes)
            
            if not need_response:
                return None
            
            # Wait for response
            start_time = time.time()
            response_data = b""
            
            while True:
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"Response timeout after {timeout}s")
                
                try:
                    self._socket.settimeout(1.0)  # Short timeout for non-blocking
                    chunk = self._socket.recv(4096)
                    if not chunk:
                        break
                    
                    response_data += chunk
                    
                    # Try to parse complete JSON response
                    try:
                        response_text = response_data.decode('utf-8')
                        response = json.loads(response_text)
                        logger.debug(f"Received response: {response}")
                        return response
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # Continue receiving if JSON is incomplete
                        continue
                        
                except socket.timeout:
                    # Continue waiting for data
                    continue
                except socket.error as e:
                    raise OperationError(f"Socket error while receiving response: {e}")
            
            # If we get here, connection was closed without complete response
            if response_data:
                try:
                    response_text = response_data.decode('utf-8')
                    response = json.loads(response_text)
                    return response
                except (json.JSONDecodeError, UnicodeDecodeError):
                    raise OperationError(f"Received malformed response: {response_data}")
            else:
                raise OperationError("Connection closed without response")
                
        except (socket.timeout, TimeoutError):
            raise TimeoutError(f"Message sending timed out after {timeout}s")
        except socket.error as e:
            raise OperationError(f"Socket error while sending message: {e}")
        except Exception as e:
            raise OperationError(f"Unexpected error sending message: {e}")
    
    @log_operation
    def send_command(self, command: Union[str, Dict[str, Any]], 
                    timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Send a command to the Agent Manager.
        
        Args:
            command: Command string or dictionary
            timeout: Command timeout
            
        Returns:
            Response dictionary
        """
        if isinstance(command, str):
            message = {"action": "execute", "command": command}
        else:
            message = command
        
        return self._send_message(message, timeout=timeout, need_response=True)
    
    @log_operation
    def execute_script(self, script_path: str, args: Optional[Dict] = None,
                      timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Execute a script on the agent.
        
        Args:
            script_path: Path to the script to execute
            args: Script arguments
            timeout: Execution timeout
            
        Returns:
            Execution result dictionary
        """
        message = {
            "action": "execute_script",
            "script_path": script_path,
            "args": args or {}
        }
        
        return self._send_message(message, timeout=timeout, need_response=True)
    
    @log_operation
    def get_agent_status(self) -> Optional[Dict[str, Any]]:
        """
        Get current status of the agent.
        
        Returns:
            Status dictionary
        """
        message = {"action": "get_status"}
        return self._send_message(message, need_response=True)
    
    @log_operation
    def start_agent_task(self, task_name: str, parameters: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Start a task on the agent.
        
        Args:
            task_name: Name of the task to start
            parameters: Task parameters
            
        Returns:
            Task start result
        """
        message = {
            "action": "start_task",
            "task_name": task_name,
            "parameters": parameters or {}
        }
        
        return self._send_message(message, need_response=True)
    
    @log_operation
    def stop_agent_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Stop a running task on the agent.
        
        Args:
            task_id: ID of the task to stop
            
        Returns:
            Task stop result
        """
        message = {
            "action": "stop_task",
            "task_id": task_id
        }
        
        return self._send_message(message, need_response=True)
    
    def send_notification(self, message: str, level: str = "info"):
        """
        Send a notification to the agent (fire and forget).
        
        Args:
            message: Notification message
            level: Notification level (info, warning, error)
        """
        notification = {
            "action": "notification",
            "message": message,
            "level": level,
            "timestamp": time.time()
        }
        
        try:
            self._send_message(notification, need_response=False)
        except Exception as e:
            logger.warning(f"Failed to send notification: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the agent connection.
        
        Returns:
            Health status dictionary
        """
        try:
            start_time = time.time()
            response = self._send_message({"action": "ping"}, timeout=5, need_response=True)
            response_time = time.time() - start_time
            
            if response:
                return {
                    "status": "healthy",
                    "response_time": response_time,
                    "agent_response": response,
                    "timestamp": time.time()
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": "No response from agent",
                    "timestamp": time.time()
                }
                
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e),
                "timestamp": time.time()
            }

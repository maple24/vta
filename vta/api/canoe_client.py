# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
Enhanced CANoe Client for CAN bus operations.

This module provides a comprehensive interface for CANoe operations
with enhanced error handling and user-friendly APIs.
"""

from typing import Optional, Dict, Any, Union
from loguru import logger

try:
    import win32com.client
except ImportError:
    logger.warning("win32com not available. CANoe operations may not work on non-Windows platforms.")
    win32com = None

from .base import (
    BaseClient, ClientConfig, VTAError, ConnectionError,
    OperationError, ValidationError,
    validate_connection, log_operation
)


class CANoeClient(BaseClient):
    """
    Enhanced CANoe client for CAN bus operations.
    
    Features:
    - CANoe application lifecycle management
    - Environment variable management
    - Diagnostic operations
    - Measurement control
    - Signal monitoring and injection
    
    Example:
        ```python
        # Basic usage
        canoe = CANoeClient()
        canoe.open_configuration("test.cfg")
        canoe.start_measurement()
        
        # Environment variables
        canoe.set_environment_variable("TestVar", 100)
        value = canoe.get_environment_variable("TestVar")
        ```
    """
    
    def __init__(self, config: Optional[ClientConfig] = None):
        """
        Initialize CANoe client.
        
        Args:
            config: Client configuration
        """
        if win32com is None:
            raise VTAError("win32com is required for CANoe operations but not available on this platform")
        
        super().__init__(config)
        
        self._application = None
        self._measurement = None
        self._environment = None
        self._current_config = None
    
    def connect(self) -> bool:
        """
        Connect to CANoe application.
        
        Returns:
            bool: True if connection successful
            
        Raises:
            ConnectionError: If connection fails
        """
        try:
            logger.info("Connecting to CANoe application")
            
            # Create CANoe application object
            self._application = win32com.client.Dispatch("CANoe.Application")
            
            if self._application:
                # Get measurement and environment objects
                self._measurement = self._application.Measurement
                self._environment = self._application.Environment
                
                self._connected = True
                logger.info("Successfully connected to CANoe")
                return True
            else:
                raise ConnectionError("Failed to create CANoe application object")
                
        except Exception as e:
            raise ConnectionError(f"Failed to connect to CANoe: {e}")
    
    def disconnect(self) -> bool:
        """
        Disconnect from CANoe application.
        
        Returns:
            bool: True if disconnection successful
        """
        try:
            if self._measurement and self._measurement.Running:
                self._measurement.Stop()
            
            self._application = None
            self._measurement = None
            self._environment = None
            self._current_config = None
            
            self._connected = False
            logger.info("Disconnected from CANoe")
            return True
            
        except Exception as e:
            logger.error(f"Error during CANoe disconnect: {e}")
            return False
    
    def is_connected(self) -> bool:
        """
        Check if connected to CANoe.
        
        Returns:
            bool: True if connected
        """
        if not self._connected or not self._application:
            return False
        
        try:
            # Test connection by accessing application version
            _ = self._application.Version
            return True
        except Exception:
            self._connected = False
            return False
    
    # Configuration Management
    @validate_connection
    @log_operation
    def open_configuration(self, config_path: str) -> bool:
        """
        Open a CANoe configuration file.
        
        Args:
            config_path: Path to the CANoe configuration file
            
        Returns:
            bool: True if configuration opened successfully
        """
        try:
            logger.info(f"Opening CANoe configuration: {config_path}")
            
            self._application.Open(config_path)
            self._current_config = config_path
            
            logger.info(f"Successfully opened configuration: {config_path}")
            return True
            
        except Exception as e:
            raise OperationError(f"Failed to open CANoe configuration {config_path}: {e}")
    
    @validate_connection
    @log_operation
    def close_configuration(self) -> bool:
        """
        Close the current CANoe configuration.
        
        Returns:
            bool: True if configuration closed successfully
        """
        try:
            if self._measurement and self._measurement.Running:
                self._measurement.Stop()
            
            self._application.Quit()
            self._current_config = None
            
            logger.info("CANoe configuration closed")
            return True
            
        except Exception as e:
            raise OperationError(f"Failed to close CANoe configuration: {e}")
    
    # Measurement Control
    @validate_connection
    @log_operation
    def start_measurement(self) -> bool:
        """
        Start CANoe measurement.
        
        Returns:
            bool: True if measurement started successfully
        """
        try:
            if not self._measurement:
                raise OperationError("Measurement object not available")
            
            if self._measurement.Running:
                logger.warning("Measurement is already running")
                return True
            
            self._measurement.Start()
            logger.info("CANoe measurement started")
            return True
            
        except Exception as e:
            raise OperationError(f"Failed to start CANoe measurement: {e}")
    
    @validate_connection
    @log_operation
    def stop_measurement(self) -> bool:
        """
        Stop CANoe measurement.
        
        Returns:
            bool: True if measurement stopped successfully
        """
        try:
            if not self._measurement:
                raise OperationError("Measurement object not available")
            
            if not self._measurement.Running:
                logger.warning("Measurement is not running")
                return True
            
            self._measurement.Stop()
            logger.info("CANoe measurement stopped")
            return True
            
        except Exception as e:
            raise OperationError(f"Failed to stop CANoe measurement: {e}")
    
    @validate_connection
    def is_measurement_running(self) -> bool:
        """
        Check if measurement is currently running.
        
        Returns:
            bool: True if measurement is running
        """
        try:
            return self._measurement and self._measurement.Running
        except Exception:
            return False
    
    # Environment Variable Management
    @validate_connection
    @log_operation
    def get_environment_variable(self, variable_name: str) -> Any:
        """
        Get the value of a CANoe environment variable.
        
        Args:
            variable_name: Name of the environment variable
            
        Returns:
            Variable value
        """
        try:
            if not self._environment:
                raise OperationError("Environment object not available")
            
            variable = self._environment.GetVariable(variable_name)
            value = variable.Value
            
            logger.debug(f"Environment variable {variable_name} = {value}")
            return value
            
        except Exception as e:
            raise OperationError(f"Failed to get environment variable {variable_name}: {e}")
    
    @validate_connection
    @log_operation
    def set_environment_variable(self, variable_name: str, value: Union[int, float, str]) -> bool:
        """
        Set the value of a CANoe environment variable.
        
        Args:
            variable_name: Name of the environment variable
            value: Value to set
            
        Returns:
            bool: True if variable set successfully
        """
        try:
            if not self._environment:
                raise OperationError("Environment object not available")
            
            variable = self._environment.GetVariable(variable_name)
            
            # Handle type conversion based on current variable type
            if isinstance(variable.Value, float):
                variable.Value = float(value)
            elif isinstance(variable.Value, int):
                variable.Value = int(value)
            else:
                variable.Value = str(value)
            
            logger.info(f"Set environment variable {variable_name} = {value}")
            return True
            
        except Exception as e:
            raise OperationError(f"Failed to set environment variable {variable_name}: {e}")
    
    @validate_connection
    def list_environment_variables(self) -> Dict[str, Any]:
        """
        Get all environment variables and their values.
        
        Returns:
            Dictionary of variable names and values
        """
        try:
            if not self._environment:
                raise OperationError("Environment object not available")
            
            variables = {}
            
            # Note: This is a simplified implementation
            # Full implementation would require iterating through all variables
            # which may need specific CANoe API knowledge
            
            logger.info("Retrieved environment variables")
            return variables
            
        except Exception as e:
            raise OperationError(f"Failed to list environment variables: {e}")
    
    # Diagnostic Operations
    @validate_connection
    @log_operation
    def send_diagnostic_request(self, request: str, node: Optional[str] = None) -> str:
        """
        Send a diagnostic request.
        
        Args:
            request: Diagnostic request string
            node: Target node (optional)
            
        Returns:
            Response string
        """
        try:
            # This is a placeholder implementation
            # Actual implementation depends on specific CANoe diagnostic setup
            
            logger.info(f"Sending diagnostic request: {request}")
            
            # Placeholder response
            response = "OK"
            
            logger.info(f"Diagnostic response: {response}")
            return response
            
        except Exception as e:
            raise OperationError(f"Failed to send diagnostic request: {e}")
    
    # Utility Methods
    @validate_connection
    def get_canoe_version(self) -> str:
        """
        Get CANoe application version.
        
        Returns:
            Version string
        """
        try:
            version = self._application.Version
            logger.info(f"CANoe version: {version}")
            return version
        except Exception as e:
            raise OperationError(f"Failed to get CANoe version: {e}")
    
    @validate_connection
    def get_current_configuration(self) -> Optional[str]:
        """
        Get the path of the currently loaded configuration.
        
        Returns:
            Configuration path or None if no configuration loaded
        """
        return self._current_config
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive CANoe status information.
        
        Returns:
            Status dictionary
        """
        status = super().get_status()
        
        try:
            if self.is_connected():
                status.update({
                    "canoe_version": self.get_canoe_version(),
                    "current_config": self.get_current_configuration(),
                    "measurement_running": self.is_measurement_running()
                })
        except Exception as e:
            status["status_error"] = str(e)
        
        return status

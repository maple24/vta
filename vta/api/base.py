# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
Base classes and interfaces for VTA API clients.

This module provides:
- Base client class with common functionality
- Configuration management
- Custom exception classes
- Common utilities and decorators
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union, Callable
from functools import wraps
import time
from loguru import logger


# Custom Exceptions
class VTAError(Exception):
    """Base exception for VTA API operations."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = time.time()


class ConnectionError(VTAError):
    """Raised when connection to a service or device fails."""
    pass


class OperationError(VTAError):
    """Raised when an operation fails during execution."""
    pass


class ValidationError(VTAError):
    """Raised when input validation fails."""
    pass


class TimeoutError(VTAError):
    """Raised when an operation times out."""
    pass


# Configuration Classes
@dataclass
class ClientConfig:
    """Base configuration for API clients."""
    
    timeout: float = 30.0
    retry_count: int = 3
    retry_delay: float = 1.0
    log_level: str = "INFO"
    validate_inputs: bool = True
    auto_connect: bool = True
    connection_pool_size: int = 5
    
    # Device-specific configurations
    device_id: Optional[str] = None
    host: str = "localhost"
    port: int = 0
    
    # Additional configuration
    extra_config: Dict[str, Any] = field(default_factory=dict)


# Decorators
def retry_on_failure(max_retries: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """Decorator to retry a function call on failure."""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}")
            
            raise last_exception
        
        return wrapper
    return decorator


def validate_connection(func: Callable) -> Callable:
    """Decorator to ensure client is connected before executing operations."""
    
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, '_connected') or not self._connected:
            raise ConnectionError(f"Client {self.__class__.__name__} is not connected")
        return func(self, *args, **kwargs)
    
    return wrapper


def log_operation(func: Callable) -> Callable:
    """Decorator to log operation start and completion."""
    
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        operation_name = func.__name__
        logger.info(f"Starting operation: {operation_name}")
        
        start_time = time.time()
        try:
            result = func(self, *args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"Operation {operation_name} completed successfully in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Operation {operation_name} failed after {duration:.2f}s: {e}")
            raise
    
    return wrapper


# Base Client Class
class BaseClient(ABC):
    """
    Abstract base class for all VTA API clients.
    
    Provides common functionality including:
    - Connection management
    - Configuration handling
    - Error handling and retry logic
    - Logging and monitoring
    """
    
    def __init__(self, config: Optional[ClientConfig] = None):
        """
        Initialize the base client.
        
        Args:
            config: Client configuration. If None, default config is used.
        """
        self.config = config or ClientConfig()
        self._connected = False
        self._connection_pool = {}
        
        # Configure logging
        self._setup_logging()
        
        logger.info(f"Initializing {self.__class__.__name__} with config: {self.config}")
        
        # Auto-connect if enabled
        if self.config.auto_connect:
            self.connect()
    
    def _setup_logging(self):
        """Setup logging configuration for this client."""
        # Configure loguru based on config
        pass
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to the target service/device.
        
        Returns:
            bool: True if connection successful, False otherwise.
            
        Raises:
            ConnectionError: If connection fails after retries.
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        Close connection to the target service/device.
        
        Returns:
            bool: True if disconnection successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if client is currently connected.
        
        Returns:
            bool: True if connected, False otherwise.
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status and health information.
        
        Returns:
            Dict containing status information.
        """
        return {
            "connected": self.is_connected(),
            "config": self.config,
            "client_type": self.__class__.__name__,
            "timestamp": time.time()
        }
    
    def validate_input(self, **kwargs) -> bool:
        """
        Validate input parameters.
        
        Args:
            **kwargs: Parameters to validate.
            
        Returns:
            bool: True if validation passes.
            
        Raises:
            ValidationError: If validation fails.
        """
        if not self.config.validate_inputs:
            return True
            
        # Override in subclasses for specific validation
        return True
    
    def __enter__(self):
        """Context manager entry."""
        if not self.is_connected():
            self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    def __str__(self) -> str:
        """String representation of the client."""
        return f"{self.__class__.__name__}(connected={self.is_connected()})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the client."""
        return f"{self.__class__.__name__}(config={self.config}, connected={self.is_connected()})"

# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
Factory pattern for creating VTA API clients.

This module provides a centralized way to create and configure API clients
with consistent patterns and configuration management.
"""

from enum import Enum
from typing import Dict, Type, Optional, Any
from .base import BaseClient, ClientConfig, VTAError


class DeviceType(Enum):
    """Enumeration of supported device types."""
    ADB = "adb"
    DEVICE = "device"
    AGENT = "agent"
    CANOE = "canoe"
    NETWORK = "network"
    HARDWARE = "hardware"
    DIAGNOSTIC = "diagnostic"


class ClientType(Enum):
    """Enumeration of supported client types."""
    ADB_CLIENT = "adb_client"
    DEVICE_CLIENT = "device_client"
    AGENT_CLIENT = "agent_client"
    CANOE_CLIENT = "canoe_client"
    NETWORK_CLIENT = "network_client"
    HARDWARE_CLIENT = "hardware_client"
    DIAGNOSTIC_CLIENT = "diagnostic_client"


class APIFactory:
    """
    Factory class for creating VTA API clients.
    
    Provides a centralized way to create clients with proper configuration
    and consistent initialization patterns.
    """
    
    _client_registry: Dict[str, Type[BaseClient]] = {}
    _default_configs: Dict[str, ClientConfig] = {}
    
    @classmethod
    def register_client(cls, client_type: str, client_class: Type[BaseClient], 
                       default_config: Optional[ClientConfig] = None):
        """
        Register a client class with the factory.
        
        Args:
            client_type: String identifier for the client type
            client_class: Class that implements BaseClient
            default_config: Default configuration for this client type
        """
        cls._client_registry[client_type] = client_class
        if default_config:
            cls._default_configs[client_type] = default_config
    
    @classmethod
    def create_client(cls, client_type: ClientType, 
                     config: Optional[ClientConfig] = None,
                     **kwargs) -> BaseClient:
        """
        Create a client instance of the specified type.
        
        Args:
            client_type: Type of client to create
            config: Configuration for the client
            **kwargs: Additional configuration parameters
            
        Returns:
            Configured client instance
            
        Raises:
            VTAError: If client type is not supported or creation fails
        """
        type_str = client_type.value
        
        if type_str not in cls._client_registry:
            available_types = list(cls._client_registry.keys())
            raise VTAError(
                f"Unsupported client type: {type_str}. "
                f"Available types: {available_types}"
            )
        
        # Merge configurations
        final_config = cls._get_merged_config(type_str, config, kwargs)
        
        # Create client instance
        client_class = cls._client_registry[type_str]
        try:
            return client_class(final_config)
        except Exception as e:
            raise VTAError(
                f"Failed to create {type_str} client: {e}",
                error_code="CLIENT_CREATION_FAILED",
                details={"client_type": type_str, "config": final_config}
            )
    
    @classmethod
    def create_adb_client(cls, device_id: Optional[str] = None, 
                         adb_path: str = "adb", **kwargs):
        """
        Convenience method to create an ADB client.
        
        Args:
            device_id: ADB device ID
            adb_path: Path to ADB executable
            **kwargs: Additional configuration
            
        Returns:
            Configured ADB client
        """
        config = ClientConfig(device_id=device_id, **kwargs)
        config.extra_config["adb_path"] = adb_path
        return cls.create_client(ClientType.ADB_CLIENT, config)
    
    @classmethod
    def create_device_client(cls, device_id: Optional[str] = None, **kwargs):
        """
        Convenience method to create a Device client.
        
        Args:
            device_id: Device ID or IP address
            **kwargs: Additional configuration
            
        Returns:
            Configured Device client
        """
        config = ClientConfig(device_id=device_id, **kwargs)
        return cls.create_client(ClientType.DEVICE_CLIENT, config)
    
    @classmethod
    def create_agent_client(cls, host: str = "localhost", port: int = 6666, **kwargs):
        """
        Convenience method to create an Agent client.
        
        Args:
            host: Agent server host
            port: Agent server port
            **kwargs: Additional configuration
            
        Returns:
            Configured Agent client
        """
        config = ClientConfig(host=host, port=port, **kwargs)
        return cls.create_client(ClientType.AGENT_CLIENT, config)
    
    @classmethod
    def create_canoe_client(cls, **kwargs):
        """
        Convenience method to create a CANoe client.
        
        Args:
            **kwargs: Additional configuration
            
        Returns:
            Configured CANoe client
        """
        config = ClientConfig(**kwargs)
        return cls.create_client(ClientType.CANOE_CLIENT, config)
    
    @classmethod
    def create_network_client(cls, base_url: str, **kwargs):
        """
        Convenience method to create a Network client.
        
        Args:
            base_url: Base URL for HTTP requests
            **kwargs: Additional configuration
            
        Returns:
            Configured Network client
        """
        config = ClientConfig(**kwargs)
        config.extra_config["base_url"] = base_url
        return cls.create_client(ClientType.NETWORK_CLIENT, config)
    
    @classmethod
    def create_hardware_client(cls, device_type: str = "relay", **kwargs):
        """
        Convenience method to create a Hardware client.
        
        Args:
            device_type: Type of hardware device (relay, power_supply, serial)
            **kwargs: Additional configuration
            
        Returns:
            Configured Hardware client
        """
        config = ClientConfig(extra_config={"device_type": device_type}, **kwargs)
        return cls.create_client(ClientType.HARDWARE_CLIENT, config)
    
    @classmethod
    def create_relay_client(cls, **kwargs):
        """
        Convenience method to create a Relay client.
        
        Args:
            **kwargs: Additional configuration
            
        Returns:
            Configured Hardware client for relay control
        """
        return cls.create_hardware_client(device_type="relay", **kwargs)
    
    @classmethod
    def create_power_supply_client(cls, serial_port: str = "COM1", **kwargs):
        """
        Convenience method to create a Power Supply client.
        
        Args:
            serial_port: Serial port for power supply
            **kwargs: Additional configuration
            
        Returns:
            Configured Hardware client for power supply control
        """
        config = ClientConfig(extra_config={
            "device_type": "power_supply",
            "serial_port": serial_port
        }, **kwargs)
        return cls.create_client(ClientType.HARDWARE_CLIENT, config)
    
    @classmethod
    def create_dlt_client(cls, socket_host: str = "localhost", socket_port: int = 3490, **kwargs):
        """
        Convenience method to create a DLT client for socket-based DLT reception.
        
        Args:
            socket_host: DLT server host
            socket_port: DLT server port
            **kwargs: Additional configuration
            
        Returns:
            Configured Diagnostic client for DLT operations
        """
        config = ClientConfig(extra_config={
            "mode": "socket",
            "socket_host": socket_host,
            "socket_port": socket_port
        }, **kwargs)
        return cls.create_client(ClientType.DIAGNOSTIC_CLIENT, config)
    
    @classmethod
    def create_serial_client(cls, serial_port: str = "COM1", baudrate: int = 115200, **kwargs):
        """
        Convenience method to create a Serial diagnostic client.
        
        Args:
            serial_port: Serial port for communication
            baudrate: Serial communication baudrate
            **kwargs: Additional configuration
            
        Returns:
            Configured Diagnostic client for serial operations
        """
        config = ClientConfig(extra_config={
            "mode": "serial",
            "serial_port": serial_port,
            "baudrate": baudrate
        }, **kwargs)
        return cls.create_client(ClientType.DIAGNOSTIC_CLIENT, config)
    
    @classmethod
    def _get_merged_config(cls, client_type: str, user_config: Optional[ClientConfig], 
                          kwargs: Dict[str, Any]) -> ClientConfig:
        """
        Merge configuration from different sources.
        
        Priority order:
        1. kwargs (highest)
        2. user_config
        3. default_config (lowest)
        """
        # Start with default config
        default_config = cls._default_configs.get(client_type, ClientConfig())
        
        # Apply user config if provided
        if user_config:
            # Create new config with user overrides
            merged_config = ClientConfig(
                timeout=user_config.timeout if user_config.timeout != default_config.timeout else default_config.timeout,
                retry_count=user_config.retry_count if user_config.retry_count != default_config.retry_count else default_config.retry_count,
                retry_delay=user_config.retry_delay if user_config.retry_delay != default_config.retry_delay else default_config.retry_delay,
                log_level=user_config.log_level if user_config.log_level != default_config.log_level else default_config.log_level,
                validate_inputs=user_config.validate_inputs if user_config.validate_inputs != default_config.validate_inputs else default_config.validate_inputs,
                auto_connect=user_config.auto_connect if user_config.auto_connect != default_config.auto_connect else default_config.auto_connect,
                connection_pool_size=user_config.connection_pool_size if user_config.connection_pool_size != default_config.connection_pool_size else default_config.connection_pool_size,
                device_id=user_config.device_id or default_config.device_id,
                host=user_config.host if user_config.host != default_config.host else default_config.host,
                port=user_config.port if user_config.port != default_config.port else default_config.port,
                extra_config={**default_config.extra_config, **user_config.extra_config}
            )
        else:
            merged_config = default_config
        
        # Apply kwargs overrides
        for key, value in kwargs.items():
            if hasattr(merged_config, key):
                setattr(merged_config, key, value)
            else:
                merged_config.extra_config[key] = value
        
        return merged_config
    
    @classmethod
    def get_available_clients(cls) -> Dict[str, Type[BaseClient]]:
        """
        Get all registered client types.
        
        Returns:
            Dictionary mapping client type names to client classes
        """
        return cls._client_registry.copy()
    
    @classmethod
    def get_client_info(cls, client_type: ClientType) -> Dict[str, Any]:
        """
        Get information about a specific client type.
        
        Args:
            client_type: Type of client to get info for
            
        Returns:
            Dictionary with client information
        """
        type_str = client_type.value
        if type_str not in cls._client_registry:
            raise VTAError(f"Unknown client type: {type_str}")
        
        client_class = cls._client_registry[type_str]
        default_config = cls._default_configs.get(type_str)
        
        return {
            "client_type": type_str,
            "client_class": client_class.__name__,
            "module": client_class.__module__,
            "doc": client_class.__doc__,
            "default_config": default_config
        }

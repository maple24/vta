# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
Client registration and initialization for VTA API.

This module automatically registers all available clients with the factory
and sets up default configurations.
"""

from loguru import logger

from .factory import APIFactory, ClientType
from .base import ClientConfig

# Import all client classes
from .adb_client import ADBClient
from .device_client import DeviceClient
from .agent_client import AgentClient
from .canoe_client import CANoeClient
from .network_client import NetworkClient
from .hardware_client import HardwareClient
from .diagnostic_client import DiagnosticClient


def register_all_clients():
    """Register all available clients with the factory."""
    
    # ADB Client
    adb_config = ClientConfig(
        timeout=30.0,
        retry_count=3,
        retry_delay=1.0,
        auto_connect=False,  # ADB requires device_id
        extra_config={"adb_path": "adb"}
    )
    APIFactory.register_client(ClientType.ADB_CLIENT.value, ADBClient, adb_config)
    
    # Device Client  
    device_config = ClientConfig(
        timeout=30.0,
        retry_count=3,
        retry_delay=1.0,
        auto_connect=False,  # Device requires device_id
        connection_pool_size=3
    )
    APIFactory.register_client(ClientType.DEVICE_CLIENT.value, DeviceClient, device_config)
    
    # Agent Client
    agent_config = ClientConfig(
        timeout=20.0,
        retry_count=3,
        retry_delay=1.0,
        host="localhost",
        port=6666,
        auto_connect=True
    )
    APIFactory.register_client(ClientType.AGENT_CLIENT.value, AgentClient, agent_config)
    
    # CANoe Client
    canoe_config = ClientConfig(
        timeout=30.0,
        retry_count=2,
        retry_delay=2.0,
        auto_connect=True
    )
    APIFactory.register_client(ClientType.CANOE_CLIENT.value, CANoeClient, canoe_config)
    
    # Network Client
    network_config = ClientConfig(
        timeout=30.0,
        retry_count=3,
        retry_delay=1.0,
        auto_connect=False,  # Network requires base_url
        connection_pool_size=10
    )
    APIFactory.register_client(ClientType.NETWORK_CLIENT.value, NetworkClient, network_config)
    
    # Hardware Client
    hardware_config = ClientConfig(
        timeout=15.0,
        retry_count=2,
        retry_delay=1.0,
        auto_connect=True,
        extra_config={
            "device_type": "relay",
            "relay_count": 8,
            "serial_port": "COM1",
            "baud_rate": 9600
        }
    )
    APIFactory.register_client(ClientType.HARDWARE_CLIENT.value, HardwareClient, hardware_config)
    
    # Diagnostic Client - Socket mode (DLT)
    diagnostic_socket_config = ClientConfig(
        timeout=20.0,
        retry_count=2,
        retry_delay=1.0,
        auto_connect=False,  # Requires socket_host/port
        extra_config={
            "mode": "socket",
            "socket_host": "localhost",
            "socket_port": 3490
        }
    )
    APIFactory.register_client(ClientType.DIAGNOSTIC_CLIENT.value, DiagnosticClient, diagnostic_socket_config)
    
    logger.info("All VTA API clients registered successfully")


# Auto-register clients when module is imported
register_all_clients()

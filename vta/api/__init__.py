# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
VTA API Module

This module provides a unified interface for various test automation APIs including:
- Android Debug Bridge (ADB) operations
- Device automation through UI Automator
- Agent communication
- CAN bus operations via CANoe
- Network utilities
- Hardware control (PPS, Relay, etc.)

Example usage:
    from vta.api import APIFactory, DeviceType
    
    # Create ADB client
    adb = APIFactory.create_client(DeviceType.ADB, device_id="emulator-5554")
    adb.click(100, 200)
    
    # Create Device client
    device = APIFactory.create_client(DeviceType.DEVICE, device_id="192.168.1.100")
    device.install_app("path/to/app.apk")
"""

from .base import BaseClient, ClientConfig, VTAError, ConnectionError, OperationError
from .factory import APIFactory, DeviceType, ClientType
from .adb_client import ADBClient
from .device_client import DeviceClient
from .agent_client import AgentClient
from .canoe_client import CANoeClient
from .network_client import NetworkClient
from .hardware_client import HardwareClient
from .diagnostic_client import DiagnosticClient

# Auto-register all clients
from . import _registration  # This will trigger registration

__version__ = "1.0.0"
__all__ = [
    # Core classes
    "BaseClient",
    "ClientConfig", 
    "VTAError",
    "ConnectionError",
    "OperationError",
    
    # Factory
    "APIFactory",
    "DeviceType",
    "ClientType",
    
    # Client implementations
    "ADBClient",
    "DeviceClient", 
    "AgentClient",
    "CANoeClient",
    "NetworkClient",
    "HardwareClient",
    "DiagnosticClient",
]

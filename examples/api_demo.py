#!/usr/bin/env python3
# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
VTA API Usage Examples

This script demonstrates how to use the refactored VTA API with various clients.
Run this script to see the new API in action.
"""

import sys
import time
from pathlib import Path

# Add the VTA module to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

from vta.api import (
    APIFactory, ClientType, ClientConfig,
    ADBClient, DeviceClient, AgentClient, NetworkClient
)
from vta.api.base import VTAError, ConnectionError, OperationError


def demonstrate_adb_client():
    """Demonstrate ADB client usage."""
    print("\n=== ADB Client Demo ===")
    
    try:
        # Create ADB client with configuration
        config = ClientConfig(
            device_id="emulator-5554",  # Change to your device ID
            timeout=10.0,
            auto_connect=False  # Manual connection for demo
        )
        
        print(f"Creating ADB client for device: {config.device_id}")
        adb = ADBClient(config)
        
        # Check available devices
        devices = adb.list_devices()
        print(f"Available devices: {[d['id'] for d in devices]}")
        
        if not devices:
            print("No ADB devices found. Please connect a device or start an emulator.")
            return
        
        # Use the first available device if our target is not found
        if not any(d['id'] == config.device_id for d in devices):
            adb.device_id = devices[0]['id']
            print(f"Using available device: {adb.device_id}")
        
        # Connect and perform operations
        if adb.connect():
            print("✓ Connected to device")
            
            # Get device information
            device_info = adb.get_device_info()
            if device_info:
                print(f"Device info: {device_info.get('brand', 'Unknown')} {device_info.get('model', 'Unknown')}")
            
            # Get screen size
            screen_size = adb.get_screen_size()
            if screen_size:
                print(f"Screen size: {screen_size[0]}x{screen_size[1]}")
                
                # Perform a tap in the center of the screen
                center_x, center_y = screen_size[0] // 2, screen_size[1] // 2
                print(f"Tapping at center: ({center_x}, {center_y})")
                adb.tap(center_x, center_y)
            
            adb.disconnect()
            print("✓ Disconnected from device")
        else:
            print("✗ Failed to connect to device")
            
    except ConnectionError as e:
        print(f"✗ Connection error: {e}")
    except OperationError as e:
        print(f"✗ Operation error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def demonstrate_device_client():
    """Demonstrate Device client usage."""
    print("\n=== Device Client Demo ===")
    
    try:
        # Note: This requires uiautomator2 to be installed
        config = ClientConfig(
            device_id="emulator-5554",  # Change to your device ID
            timeout=15.0,
            auto_connect=False
        )
        
        print(f"Creating Device client for device: {config.device_id}")
        device = DeviceClient(config)
        
        # Attempt connection
        if device.connect():
            print("✓ Connected to device via UI Automator2")
            
            # Get installed apps
            apps = device.list_installed_apps(include_system=False)
            print(f"Installed apps (first 5): {apps[:5]}")
            
            # Get app info for a common app
            if apps:
                app_info = device.get_app_info(apps[0])
                if app_info:
                    print(f"App info for {apps[0]}: {app_info.version_name}")
            
            device.disconnect()
            print("✓ Disconnected from device")
        else:
            print("✗ Failed to connect to device")
            
    except ImportError:
        print("✗ uiautomator2 not installed. Run: pip install uiautomator2")
    except ConnectionError as e:
        print(f"✗ Connection error: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")


def demonstrate_agent_client():
    """Demonstrate Agent client usage."""
    print("\n=== Agent Client Demo ===")
    
    try:
        # Create agent client
        config = ClientConfig(
            host="localhost",
            port=6666,
            timeout=5.0,
            auto_connect=False
        )
        
        print(f"Creating Agent client for {config.host}:{config.port}")
        agent = AgentClient(config)
        
        # Attempt connection
        try:
            if agent.connect():
                print("✓ Connected to Agent Manager")
                
                # Get agent status
                status = agent.get_agent_status()
                print(f"Agent status: {status}")
                
                # Send a simple command
                response = agent.send_command({"action": "ping"})
                print(f"Ping response: {response}")
                
                agent.disconnect()
                print("✓ Disconnected from Agent Manager")
            else:
                print("✗ Failed to connect to Agent Manager")
                
        except ConnectionError:
            print("✗ Agent Manager not available (this is expected if not running)")
            
    except Exception as e:
        print(f"✗ Error: {e}")


def demonstrate_network_client():
    """Demonstrate Network client usage."""
    print("\n=== Network Client Demo ===")
    
    try:
        # Create network client for a public API
        config = ClientConfig(
            timeout=10.0,
            auto_connect=False,
            extra_config={"base_url": "https://httpbin.org"}
        )
        
        print("Creating Network client for httpbin.org")
        http = NetworkClient(config)
        
        if http.connect():
            print("✓ HTTP session created")
            
            # Perform GET request
            response = http.get("/get", params={"test": "value"})
            print(f"GET response status: Success")
            print(f"Response URL: {response.get('url', 'N/A')}")
            
            # Perform POST request
            post_data = {"message": "Hello from VTA API!"}
            response = http.post("/post", json_data=post_data)
            print(f"POST response status: Success")
            
            # Health check
            health = http.health_check()
            print(f"Health check: {health['status']}")
            
            http.disconnect()
            print("✓ HTTP session closed")
        else:
            print("✗ Failed to create HTTP session")
            
    except Exception as e:
        print(f"✗ Network error: {e}")


def demonstrate_factory_pattern():
    """Demonstrate the factory pattern usage."""
    print("\n=== Factory Pattern Demo ===")
    
    try:
        # List available clients
        available_clients = APIFactory.get_available_clients()
        print(f"Available clients: {list(available_clients.keys())}")
        
        # Get client info
        for client_type in [ClientType.ADB_CLIENT, ClientType.NETWORK_CLIENT]:
            try:
                info = APIFactory.get_client_info(client_type)
                print(f"{client_type.value}: {info['client_class']}")
            except:
                print(f"{client_type.value}: Info not available")
        
        # Create clients using convenience methods
        print("\nCreating clients using convenience methods:")
        
        # ADB client
        try:
            adb = APIFactory.create_adb_client(device_id="test-device")
            print(f"✓ Created ADB client: {adb}")
        except Exception as e:
            print(f"✗ ADB client creation failed: {e}")
        
        # Network client
        try:
            http = APIFactory.create_network_client(base_url="https://example.com")
            print(f"✓ Created Network client: {http}")
        except Exception as e:
            print(f"✗ Network client creation failed: {e}")
            
    except Exception as e:
        print(f"✗ Factory demo error: {e}")


def demonstrate_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n=== Error Handling Demo ===")
    
    # Test validation error
    try:
        config = ClientConfig(device_id="invalid-device")
        adb = ADBClient(config)
        adb.tap(-100, -100)  # Invalid coordinates
    except Exception as e:
        print(f"✓ Caught validation error: {type(e).__name__}: {e}")
    
    # Test connection error
    try:
        config = ClientConfig(host="nonexistent.host", port=9999, timeout=1.0)
        agent = AgentClient(config)
        agent.connect()
    except ConnectionError as e:
        print(f"✓ Caught connection error: {e}")
    except Exception as e:
        print(f"✓ Caught error: {type(e).__name__}: {e}")
    
    # Test timeout error
    try:
        config = ClientConfig(
            extra_config={"base_url": "https://httpbin.org"},
            timeout=0.001  # Very short timeout
        )
        http = NetworkClient(config)
        http.get("/delay/5")  # This will timeout
    except Exception as e:
        print(f"✓ Caught timeout-related error: {type(e).__name__}")


def main():
    """Run all demonstration functions."""
    print("VTA API Refactoring Demo")
    print("=" * 50)
    
    # Run demonstrations
    demonstrate_factory_pattern()
    demonstrate_error_handling()
    demonstrate_adb_client()
    demonstrate_device_client()
    demonstrate_agent_client()
    demonstrate_network_client()
    
    print("\n" + "=" * 50)
    print("Demo completed! Check the output above to see the new API in action.")
    print("\nKey benefits of the refactored API:")
    print("- Consistent interface across all clients")
    print("- Comprehensive error handling")
    print("- Factory pattern for easy client creation")
    print("- Context manager support")
    print("- Full type hints and documentation")
    print("- Configurable retry and timeout mechanisms")


if __name__ == "__main__":
    main()

# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
ADB Client Usage Examples

This file demonstrates various usage patterns for the ADBClient,
which provides Android Debug Bridge functionality for device automation.
"""

import time
from vta.api.factory import APIFactory
from vta.api.base import ClientConfig


def basic_adb_operations():
    """Basic ADB operations example."""
    print("=== Basic ADB Operations ===")
    
    # Create ADB client with default settings
    adb = APIFactory.create_adb_client(
        device_id="emulator-5554",  # Or specific device serial
        adb_path="adb"  # Path to ADB executable
    )
    
    try:
        # Connect to device
        print("Connecting to ADB device...")
        adb.connect()
        
        # Check if device is connected
        if adb.is_connected():
            print("✓ ADB device connected successfully")
        
        # Execute basic shell commands
        print("\n--- Shell Commands ---")
        result = adb.execute_command("getprop ro.build.version.release")
        print(f"Android Version: {result}")
        
        result = adb.execute_command("getprop ro.product.model")
        print(f"Device Model: {result}")
        
        result = adb.execute_command("getprop ro.product.manufacturer")
        print(f"Manufacturer: {result}")
        
        # Get device properties
        print("\n--- Device Properties ---")
        props = adb.get_device_properties()
        for key, value in props.items():
            print(f"{key}: {value}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        adb.disconnect()


def app_management_example():
    """Application management operations."""
    print("\n=== Application Management ===")
    
    adb = APIFactory.create_adb_client(device_id="emulator-5554")
    
    try:
        adb.connect()
        
        # Install APK (example - uncomment when you have an APK)
        print("Installing APK...")
        # apk_path = "path/to/your/app.apk"
        # success = adb.install_apk(apk_path)
        # print(f"Installation {'successful' if success else 'failed'}")
        
        # List installed packages
        print("\n--- Installed Packages ---")
        packages = adb.get_installed_packages()
        for pkg in packages[:10]:  # Show first 10
            print(f"- {pkg}")
        
        # Start application
        package_name = "com.android.settings"
        print(f"\nStarting application: {package_name}")
        success = adb.start_application(package_name)
        print(f"Start {'successful' if success else 'failed'}")
        
        # Check if app is running
        time.sleep(2)
        running_apps = adb.get_running_applications()
        if package_name in running_apps:
            print(f"✓ {package_name} is running")
        
        # Stop application
        print(f"Stopping application: {package_name}")
        success = adb.stop_application(package_name)
        print(f"Stop {'successful' if success else 'failed'}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        adb.disconnect()


def file_operations_example():
    """File transfer and management operations."""
    print("\n=== File Operations ===")
    
    adb = APIFactory.create_adb_client()
    
    try:
        adb.connect()
        
        # Push file to device
        print("Pushing file to device...")
        local_file = "test.txt"
        remote_file = "/sdcard/test.txt"
        
        # Create test file
        with open(local_file, 'w') as f:
            f.write("Hello from ADB client!")
        
        success = adb.push_file(local_file, remote_file)
        print(f"Push {'successful' if success else 'failed'}")
        
        # List files in directory
        print("\n--- Files in /sdcard ---")
        files = adb.list_directory("/sdcard")
        for file_info in files[:10]:  # Show first 10
            print(f"- {file_info}")
        
        # Pull file from device
        print("Pulling file from device...")
        pulled_file = "pulled_test.txt"
        success = adb.pull_file(remote_file, pulled_file)
        print(f"Pull {'successful' if success else 'failed'}")
        
        if success:
            with open(pulled_file, 'r') as f:
                content = f.read()
                print(f"File content: {content}")
        
        # Remove file from device
        print("Removing file from device...")
        success = adb.remove_file(remote_file)
        print(f"Remove {'successful' if success else 'failed'}")
        
        # Cleanup local files
        import os
        try:
            os.remove(local_file)
            os.remove(pulled_file)
        except Exception:
            pass
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        adb.disconnect()


def ui_automation_example():
    """UI automation and input operations."""
    print("\n=== UI Automation ===")
    
    adb = APIFactory.create_adb_client()
    
    try:
        adb.connect()
        
        # Take screenshot
        print("Taking screenshot...")
        screenshot_path = "screenshot.png"
        success = adb.take_screenshot(screenshot_path)
        print(f"Screenshot {'saved' if success else 'failed'}")
        
        # Screen interactions
        print("\n--- Screen Interactions ---")
        
        # Tap at coordinates
        print("Tapping at (500, 300)...")
        adb.tap_screen(500, 300)
        
        # Swipe gesture
        print("Swiping from (300, 800) to (300, 200)...")
        adb.swipe_screen(300, 800, 300, 200, duration=500)
        
        # Send text input
        print("Sending text input...")
        adb.send_text("Hello ADB!")
        
        # Send key events
        print("Sending key events...")
        adb.send_key_event("KEYCODE_HOME")  # Home button
        time.sleep(1)
        adb.send_key_event("KEYCODE_MENU")  # Menu button
        
        # Volume control
        print("Volume control...")
        adb.send_key_event("KEYCODE_VOLUME_UP")
        time.sleep(0.5)
        adb.send_key_event("KEYCODE_VOLUME_DOWN")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        adb.disconnect()


def device_info_example():
    """Device information and monitoring."""
    print("\n=== Device Information ===")
    
    adb = APIFactory.create_adb_client()
    
    try:
        adb.connect()
        
        # Get device info
        print("--- Device Information ---")
        device_info = adb.get_device_info()
        for key, value in device_info.items():
            print(f"{key}: {value}")
        
        # Battery information
        print("\n--- Battery Information ---")
        battery_info = adb.get_battery_info()
        for key, value in battery_info.items():
            print(f"{key}: {value}")
        
        # Memory usage
        print("\n--- Memory Usage ---")
        memory_info = adb.get_memory_info()
        for key, value in memory_info.items():
            print(f"{key}: {value}")
        
        # Storage information
        print("\n--- Storage Information ---")
        storage_info = adb.get_storage_info()
        for key, value in storage_info.items():
            print(f"{key}: {value}")
        
        # Network information
        print("\n--- Network Information ---")
        network_info = adb.get_network_info()
        for key, value in network_info.items():
            print(f"{key}: {value}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        adb.disconnect()


def advanced_adb_example():
    """Advanced ADB operations and custom configurations."""
    print("\n=== Advanced ADB Operations ===")
    
    # Custom configuration
    config = ClientConfig(
        timeout=60.0,  # Longer timeout for slow operations
        retry_count=5,
        retry_delay=2.0,
        extra_config={
            "adb_path": "C:/platform-tools/adb.exe",  # Custom ADB path
            "enable_logging": True,
            "log_commands": True
        }
    )
    
    adb = APIFactory.create_client(APIFactory.ClientType.ADB_CLIENT, config)
    
    try:
        adb.connect()
        
        # Execute complex shell command
        print("Executing complex shell command...")
        cmd = "pm list packages -f | grep -E '(google|android)' | head -5"
        result = adb.execute_command(cmd)
        print(f"Result: {result}")
        
        # Logcat monitoring
        print("\n--- Logcat Monitoring ---")
        print("Starting logcat (will run for 10 seconds)...")
        adb.start_logcat_monitoring()
        time.sleep(10)
        adb.stop_logcat_monitoring()
        
        logs = adb.get_recent_logs(count=20)
        print(f"Retrieved {len(logs)} log entries")
        for log in logs[:5]:  # Show first 5
            print(f"- {log}")
        
        # Performance monitoring
        print("\n--- Performance Monitoring ---")
        cpu_usage = adb.get_cpu_usage()
        print(f"CPU Usage: {cpu_usage}%")
        
        # Custom ADB command
        print("\n--- Custom ADB Command ---")
        result = adb.execute_raw_adb_command("devices -l")
        print(f"Available devices:\n{result}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        adb.disconnect()


def multiple_devices_example():
    """Managing multiple ADB devices."""
    print("\n=== Multiple Devices Example ===")
    
    # Get available devices (example)
    print("--- Available Devices ---")
    # available_devices = adb.get_devices()  # This would get actual devices
    
    # Simulate multiple devices
    device_ids = ["emulator-5554", "emulator-5556", "device-serial-123"]
    
    clients = []
    
    try:
        # Create clients for each device
        for device_id in device_ids:
            print(f"Setting up client for {device_id}...")
            client = APIFactory.create_adb_client(device_id=device_id)
            
            try:
                if client.connect():
                    clients.append((device_id, client))
                    print(f"✓ Connected to {device_id}")
                else:
                    print(f"✗ Failed to connect to {device_id}")
            except Exception as e:
                print(f"✗ Error connecting to {device_id}: {e}")
        
        # Perform operations on all connected devices
        print(f"\n--- Operations on {len(clients)} devices ---")
        for device_id, client in clients:
            try:
                print(f"\nDevice: {device_id}")
                model = client.execute_command("getprop ro.product.model")
                version = client.execute_command("getprop ro.build.version.release")
                print(f"  Model: {model}")
                print(f"  Android: {version}")
                
                # Take screenshot for each device
                screenshot_path = f"screenshot_{device_id.replace('-', '_')}.png"
                if client.take_screenshot(screenshot_path):
                    print(f"  Screenshot saved: {screenshot_path}")
                
            except Exception as e:
                print(f"  Error: {e}")
    
    finally:
        # Cleanup all connections
        for device_id, client in clients:
            try:
                client.disconnect()
                print(f"Disconnected from {device_id}")
            except Exception:
                pass


if __name__ == "__main__":
    print("VTA ADB Client Examples")
    print("=======================")
    
    # Run all examples
    try:
        basic_adb_operations()
        app_management_example()
        file_operations_example()
        ui_automation_example()
        device_info_example()
        advanced_adb_example()
        multiple_devices_example()
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    
    print("\nAll ADB examples completed!")

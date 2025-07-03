# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
Hardware Client Usage Examples

This file demonstrates various usage patterns for the HardwareClient,
which provides unified control for relay systems, power supplies, and other hardware devices.
"""

import time
from vta.api.factory import APIFactory
from vta.api.base import ClientConfig


def relay_control_example():
    """Basic relay control operations."""
    print("=== Relay Control Example ===")
    
    # Create relay client with default settings
    relay_client = APIFactory.create_relay_client()
    
    try:
        # Connect to relay hardware
        print("Connecting to relay hardware...")
        relay_client.connect()
        
        if relay_client.is_connected():
            print("✓ Relay hardware connected successfully")
        
        # Get relay count
        relay_count = relay_client.get_relay_count()
        print(f"Available relays: {relay_count}")
        
        # Control individual relays
        print("\n--- Individual Relay Control ---")
        for relay_num in range(1, min(5, relay_count + 1)):  # Test first 4 relays
            print(f"Testing relay {relay_num}...")
            
            # Turn on relay
            success = relay_client.set_relay_state(relay_num, True)
            print(f"  Turn ON: {'✓' if success else '✗'}")
            
            # Check state
            state = relay_client.get_relay_state(relay_num)
            print(f"  State: {state}")
            
            time.sleep(1)
            
            # Turn off relay
            success = relay_client.set_relay_state(relay_num, False)
            print(f"  Turn OFF: {'✓' if success else '✗'}")
            
            # Check state again
            state = relay_client.get_relay_state(relay_num)
            print(f"  State: {state}")
            
            time.sleep(0.5)
        
        # Control all relays at once
        print("\n--- All Relays Control ---")
        print("Turning all relays ON...")
        success = relay_client.set_all_relays(True)
        print(f"All ON: {'✓' if success else '✗'}")
        
        time.sleep(2)
        
        print("Turning all relays OFF...")
        success = relay_client.set_all_relays(False)
        print(f"All OFF: {'✓' if success else '✗'}")
        
        # Get status
        print("\n--- Relay Status ---")
        status = relay_client.get_status()
        print(f"Device Type: {status.get('device_type')}")
        print(f"Connected: {status.get('connected')}")
        if 'relay_states' in status:
            print("Relay States:")
            for relay, state in status['relay_states'].items():
                print(f"  {relay}: {state}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        relay_client.disconnect()


def power_supply_example():
    """Power supply control operations."""
    print("\n=== Power Supply Control Example ===")
    
    # Create power supply client
    psu_client = APIFactory.create_power_supply_client(
        serial_port="COM1",  # Adjust to your setup
        extra_config={
            "baud_rate": 9600,
            "timeout": 10.0
        }
    )
    
    try:
        # Connect to power supply
        print("Connecting to power supply...")
        psu_client.connect()
        
        if psu_client.is_connected():
            print("✓ Power supply connected successfully")
        
        # Set voltage levels
        print("\n--- Voltage Control ---")
        voltages = [3.3, 5.0, 12.0, 24.0]
        
        for voltage in voltages:
            print(f"Setting voltage to {voltage}V...")
            success = psu_client.set_voltage(voltage)
            print(f"  Set {voltage}V: {'✓' if success else '✗'}")
            time.sleep(1)
        
        # Set current limits
        print("\n--- Current Limit Control ---")
        current_limits = [0.5, 1.0, 2.0, 3.0]
        
        for current in current_limits:
            print(f"Setting current limit to {current}A...")
            success = psu_client.set_current_limit(current)
            print(f"  Set {current}A: {'✓' if success else '✗'}")
            time.sleep(1)
        
        # Power cycling simulation
        print("\n--- Power Cycling ---")
        print("Power cycling sequence...")
        
        # Set to 0V (power off)
        psu_client.set_voltage(0.0)
        print("  Power OFF (0V)")
        time.sleep(2)
        
        # Set to 12V (power on)
        psu_client.set_voltage(12.0)
        psu_client.set_current_limit(2.0)
        print("  Power ON (12V, 2A limit)")
        time.sleep(2)
        
        # Back to 0V
        psu_client.set_voltage(0.0)
        print("  Power OFF (0V)")
        
        # Get status
        print("\n--- Power Supply Status ---")
        status = psu_client.get_status()
        print(f"Device Type: {status.get('device_type')}")
        print(f"Connected: {status.get('connected')}")
        print(f"Serial Port: {status.get('serial_port')}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        psu_client.disconnect()


def cleware_relay_example():
    """Cleware USB relay specific example."""
    print("\n=== Cleware USB Relay Example ===")
    
    # Create hardware client with Cleware configuration
    config = ClientConfig(
        timeout=15.0,
        extra_config={
            "device_type": "relay",
            "cleware_path": "vta/bin/cleware",  # Path to Cleware tools
            "relay_count": 8
        }
    )
    
    cleware_client = APIFactory.create_client(APIFactory.ClientType.HARDWARE_CLIENT, config)
    
    try:
        print("Connecting to Cleware USB relay...")
        cleware_client.connect()
        
        if cleware_client.is_connected():
            print("✓ Cleware USB relay connected")
        
        # Test relay pattern
        print("\n--- Relay Pattern Test ---")
        patterns = [
            [1, 3, 5, 7],  # Odd relays
            [2, 4, 6, 8],  # Even relays
            [1, 2, 3, 4],  # First half
            [5, 6, 7, 8]   # Second half
        ]
        
        for i, pattern in enumerate(patterns, 1):
            print(f"Pattern {i}: Relays {pattern}")
            
            # Turn on relays in pattern
            for relay in pattern:
                cleware_client.set_relay_state(relay, True)
                time.sleep(0.2)
            
            time.sleep(1)
            
            # Turn off relays in pattern
            for relay in pattern:
                cleware_client.set_relay_state(relay, False)
                time.sleep(0.2)
            
            time.sleep(0.5)
        
        # Sequential relay test
        print("\n--- Sequential Relay Test ---")
        for relay in range(1, 9):  # Relays 1-8
            print(f"Activating relay {relay}...")
            cleware_client.set_relay_state(relay, True)
            time.sleep(0.5)
            cleware_client.set_relay_state(relay, False)
            time.sleep(0.2)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cleware_client.disconnect()


def serial_hardware_example():
    """Serial hardware communication example."""
    print("\n=== Serial Hardware Communication Example ===")
    
    # Create serial hardware client
    config = ClientConfig(
        timeout=10.0,
        extra_config={
            "device_type": "serial",
            "serial_port": "COM3",  # Adjust to your setup
            "baud_rate": 115200,
            "enable_logging": True
        }
    )
    
    serial_hw = APIFactory.create_client(APIFactory.ClientType.HARDWARE_CLIENT, config)
    
    try:
        print("Connecting to serial hardware...")
        serial_hw.connect()
        
        if serial_hw.is_connected():
            print("✓ Serial hardware connected")
        
        # Send test commands (adjust for your hardware)
        print("\n--- Hardware Commands ---")
        commands = [
            "*IDN?",           # Identification
            "STATUS?",         # Status query
            "VERSION?",        # Version query
            "RESET",           # Reset command
        ]
        
        for cmd in commands:
            print(f"Sending command: {cmd}")
            try:
                # This would use the serial communication from the hardware client
                # The actual implementation depends on your hardware protocol
                print(f"  Command '{cmd}' sent")
                time.sleep(0.5)
            except Exception as e:
                print(f"  Error: {e}")
        
        # Get hardware status
        print("\n--- Hardware Status ---")
        status = serial_hw.get_status()
        for key, value in status.items():
            print(f"{key}: {value}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        serial_hw.disconnect()


def advanced_hardware_automation():
    """Advanced hardware automation example."""
    print("\n=== Advanced Hardware Automation ===")
    
    # Create multiple hardware clients for complex automation
    relay_client = APIFactory.create_relay_client()
    psu_client = APIFactory.create_power_supply_client(serial_port="COM1")
    
    try:
        # Connect all hardware
        print("Connecting to hardware systems...")
        
        relay_connected = False
        psu_connected = False
        
        try:
            relay_client.connect()
            relay_connected = relay_client.is_connected()
            print(f"Relay system: {'✓' if relay_connected else '✗'}")
        except Exception as e:
            print(f"Relay connection failed: {e}")
        
        try:
            psu_client.connect()
            psu_connected = psu_client.is_connected()
            print(f"Power supply: {'✓' if psu_connected else '✗'}")
        except Exception as e:
            print(f"Power supply connection failed: {e}")
        
        if relay_connected and psu_connected:
            # Automated test sequence
            print("\n--- Automated Test Sequence ---")
            
            # Step 1: Initialize power
            print("Step 1: Initialize power supply")
            psu_client.set_voltage(0.0)
            psu_client.set_current_limit(1.0)
            relay_client.set_all_relays(False)
            time.sleep(1)
            
            # Step 2: Power up sequence
            print("Step 2: Power up sequence")
            relay_client.set_relay_state(1, True)  # Enable main power relay
            time.sleep(0.5)
            psu_client.set_voltage(12.0)  # Set main voltage
            time.sleep(1)
            
            # Step 3: Enable subsystems
            print("Step 3: Enable subsystems")
            subsystem_relays = [2, 3, 4]  # Subsystem relays
            for relay in subsystem_relays:
                print(f"  Enabling subsystem {relay}")
                relay_client.set_relay_state(relay, True)
                time.sleep(0.5)
            
            # Step 4: Run test pattern
            print("Step 4: Run test pattern")
            test_relays = [5, 6, 7, 8]
            for cycle in range(3):
                print(f"  Test cycle {cycle + 1}")
                for relay in test_relays:
                    relay_client.set_relay_state(relay, True)
                    time.sleep(0.3)
                    relay_client.set_relay_state(relay, False)
                    time.sleep(0.2)
            
            # Step 5: Shutdown sequence
            print("Step 5: Shutdown sequence")
            relay_client.set_all_relays(False)  # Turn off all relays
            time.sleep(0.5)
            psu_client.set_voltage(0.0)  # Turn off power
            
            print("✓ Automated test sequence completed")
        
        # Generate test report
        print("\n--- Test Report ---")
        
        if relay_connected:
            relay_status = relay_client.get_status()
            print(f"Relay System Status: {relay_status.get('connected')}")
            print(f"Relay Count: {relay_client.get_relay_count()}")
        
        if psu_connected:
            psu_status = psu_client.get_status()
            print(f"Power Supply Status: {psu_status.get('connected')}")
            print(f"Serial Port: {psu_status.get('serial_port')}")
        
    except Exception as e:
        print(f"Error in automation: {e}")
    finally:
        # Cleanup
        print("\nCleaning up...")
        try:
            if relay_connected:
                relay_client.set_all_relays(False)
                relay_client.disconnect()
        except Exception:
            pass
        
        try:
            if psu_connected:
                psu_client.set_voltage(0.0)
                psu_client.disconnect()
        except Exception:
            pass


def hardware_monitoring_example():
    """Hardware monitoring and status example."""
    print("\n=== Hardware Monitoring Example ===")
    
    # Create hardware client with monitoring configuration
    config = ClientConfig(
        timeout=30.0,
        extra_config={
            "device_type": "relay",
            "enable_monitoring": True,
            "monitor_interval": 1.0
        }
    )
    
    hw_client = APIFactory.create_client(APIFactory.ClientType.HARDWARE_CLIENT, config)
    
    try:
        hw_client.connect()
        
        if hw_client.is_connected():
            print("✓ Hardware monitoring started")
        
        # Monitor hardware status over time
        print("\n--- Hardware Status Monitoring ---")
        print("Monitoring for 10 seconds...")
        
        start_time = time.time()
        while time.time() - start_time < 10:
            status = hw_client.get_status()
            
            print(f"\nTime: {time.time() - start_time:.1f}s")
            print(f"Connected: {status.get('connected')}")
            print(f"Device Enabled: {status.get('device_enabled')}")
            
            if 'relay_states' in status:
                active_relays = [k for k, v in status['relay_states'].items() if v is True]
                print(f"Active Relays: {len(active_relays)} - {active_relays}")
            
            # Toggle a relay for demonstration
            test_relay = ((int(time.time()) % 4) + 1)  # Cycle through relays 1-4
            current_state = hw_client.get_relay_state(test_relay)
            new_state = not current_state if current_state is not None else True
            hw_client.set_relay_state(test_relay, new_state)
            
            time.sleep(2)
        
        print("\n✓ Monitoring completed")
        
    except Exception as e:
        print(f"Error in monitoring: {e}")
    finally:
        hw_client.disconnect()


if __name__ == "__main__":
    print("VTA Hardware Client Examples")
    print("============================")
    
    # Run all examples
    try:
        relay_control_example()
        power_supply_example()
        cleware_relay_example()
        serial_hardware_example()
        advanced_hardware_automation()
        hardware_monitoring_example()
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    
    print("\nAll hardware examples completed!")

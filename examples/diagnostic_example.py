# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
Example usage of the refactored DiagnosticClient.

This example demonstrates how to use the DiagnosticClient for:
1. Socket-based DLT (Diagnostic Log and Trace) reception
2. Serial port communication for diagnostic commands

The DiagnosticClient now uses direct socket and serial communication
instead of TCP/Putty/SSH.
"""

import time
from vta.api.factory import APIFactory
from vta.api.diagnostic_client import DLTMessage


def dlt_message_handler(message: DLTMessage):
    """Handler for DLT messages."""
    print(f"[{message.timestamp}] {message.app_id}.{message.context_id}: {message.payload}")


def example_socket_dlt_reception():
    """Example of socket-based DLT reception."""
    print("=== Socket-based DLT Reception Example ===")
    
    # Create DLT client for socket communication
    dlt_client = APIFactory.create_dlt_client(
        socket_host="192.168.1.100",  # ECU IP address
        socket_port=3490,             # DLT port
        timeout=30.0
    )
    
    try:
        # Connect to DLT socket
        print("Connecting to DLT socket...")
        dlt_client.connect()
        print(f"Connected: {dlt_client.is_connected()}")
        
        # Start DLT reception with message handler
        print("Starting DLT message reception...")
        dlt_client.start_dlt_reception(message_handler=dlt_message_handler)
        
        # Let it run for 30 seconds
        print("Receiving DLT messages for 30 seconds...")
        time.sleep(30)
        
        # Stop reception
        print("Stopping DLT reception...")
        dlt_client.stop_dlt_reception()
        
        # Get some statistics
        stats = dlt_client.get_statistics()
        print(f"Total messages received: {stats['total_messages']}")
        
        # Get recent messages
        recent_messages = dlt_client.get_recent_messages(count=10)
        print(f"\nLast {len(recent_messages)} messages:")
        for msg in recent_messages:
            print(f"  {msg.app_id}.{msg.context_id}: {msg.payload[:50]}...")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        dlt_client.disconnect()


def example_serial_diagnostic():
    """Example of serial diagnostic communication."""
    print("\n=== Serial Diagnostic Communication Example ===")
    
    # Create serial diagnostic client
    serial_client = APIFactory.create_serial_client(
        serial_port="COM3",    # Adjust to your serial port
        baudrate=115200,
        timeout=10.0
    )
    
    try:
        # Connect to serial port
        print("Connecting to serial port...")
        serial_client.connect()
        print(f"Connected: {serial_client.is_connected()}")
        
        # Send diagnostic commands
        commands = [
            "AT",              # Basic AT command
            "AT+VERSION",      # Get version
            "AT+CSQ",          # Signal quality
            "AT+CIMI"          # IMSI
        ]
        
        for command in commands:
            print(f"\nSending command: {command}")
            try:
                response = serial_client.send_command(command, expect_response=True, timeout=5.0)
                print(f"Response: {response}")
            except Exception as e:
                print(f"Command failed: {e}")
        
        # Send raw data
        print("\nSending raw data...")
        raw_data = b'\x7E\x01\x02\x03\x7E'  # Example binary data
        success = serial_client.send_raw_data(raw_data)
        print(f"Raw data sent: {success}")
        
        # Read available data
        print("\nReading available data...")
        available_data = serial_client.read_available_data(timeout=2.0)
        if available_data:
            print(f"Received {len(available_data)} bytes: {available_data}")
        else:
            print("No data available")
        
        # Get connection info
        info = serial_client.get_connection_info()
        print(f"\nConnection info: {info}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        serial_client.disconnect()


def example_advanced_dlt_filtering():
    """Example of advanced DLT message filtering."""
    print("\n=== Advanced DLT Filtering Example ===")
    
    # Create DLT client
    dlt_client = APIFactory.create_dlt_client(
        socket_host="localhost",
        socket_port=3490
    )
    
    try:
        dlt_client.connect()
        
        # Start reception without handler to collect messages
        dlt_client.start_dlt_reception()
        
        # Simulate some time to collect messages
        print("Collecting DLT messages for 10 seconds...")
        time.sleep(10)
        
        dlt_client.stop_dlt_reception()
        
        # Filter messages by criteria
        print("\nFiltering messages...")
        
        # Filter by app ID
        app_messages = dlt_client.filter_messages(app_id="APP")
        print(f"Messages from APP: {len(app_messages)}")
        
        # Filter by log level
        error_messages = dlt_client.filter_messages(log_level="ERROR")
        print(f"Error messages: {len(error_messages)}")
        
        # Filter by time (last 5 seconds)
        recent_time = time.time() - 5.0
        recent_messages = dlt_client.filter_messages(since=recent_time)
        print(f"Messages from last 5 seconds: {len(recent_messages)}")
        
        # Combined filter
        filtered = dlt_client.filter_messages(
            app_id="APP",
            log_level="INFO",
            since=recent_time
        )
        print(f"APP INFO messages from last 5 seconds: {len(filtered)}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        dlt_client.disconnect()


if __name__ == "__main__":
    print("VTA Diagnostic Client Examples")
    print("==============================")
    
    # Note: Adjust IP addresses, ports, and serial ports according to your setup
    
    # Example 1: Socket-based DLT reception
    example_socket_dlt_reception()
    
    # Example 2: Serial diagnostic communication
    example_serial_diagnostic()
    
    # Example 3: Advanced DLT filtering
    example_advanced_dlt_filtering()
    
    print("\nAll examples completed!")

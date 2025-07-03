# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
VTA API Client Examples Index

This file provides an overview of all available examples for the VTA API clients
and serves as a quick reference for developers.
"""

import importlib
import sys
import os

# Add the parent directory to the path so we can import VTA modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def print_header(title):
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}")


def print_section(title):
    """Print a formatted section header."""
    print(f"\n--- {title} ---")


def run_example_module(module_name, description):
    """Run an example module with error handling."""
    print_section(f"{description}")
    print(f"Running {module_name}...")
    
    try:
        # Import and run the example module
        module = importlib.import_module(f"examples.{module_name}")
        print(f"✓ {description} completed successfully")
    except ImportError as e:
        print(f"✗ Could not import {module_name}: {e}")
    except Exception as e:
        print(f"✗ Error running {description}: {e}")


def show_examples_overview():
    """Display overview of all available examples."""
    
    print_header("VTA API Client Examples Overview")
    
    examples = [
        {
            "module": "adb_client_examples",
            "title": "ADB Client Examples",
            "description": "Android Debug Bridge integration for mobile device automation",
            "features": [
                "Device connection and management",
                "Application installation and control", 
                "File transfer operations",
                "UI automation and input simulation",
                "Device information and monitoring",
                "Multi-device management"
            ]
        },
        {
            "module": "hardware_client_examples", 
            "title": "Hardware Client Examples",
            "description": "Hardware control for relays, power supplies, and automation",
            "features": [
                "Relay control (Cleware USB and serial)",
                "Power supply management",
                "Serial hardware communication",
                "Hardware automation sequences",
                "Hardware monitoring and status",
                "Multi-hardware coordination"
            ]
        },
        {
            "module": "network_client_examples",
            "title": "Network Client Examples", 
            "description": "HTTP/HTTPS communication for web APIs and REST services",
            "features": [
                "Basic HTTP operations (GET, POST, PUT, DELETE)",
                "REST API integration",
                "File upload and download",
                "Authentication and headers",
                "Streaming and chunked data",
                "Advanced networking features"
            ]
        },
        {
            "module": "agent_client_examples",
            "title": "Agent Client Examples",
            "description": "VTA agent communication for test automation and orchestration", 
            "features": [
                "Agent connection and status",
                "Test execution and monitoring",
                "Device management through agent",
                "Resource monitoring and health",
                "Configuration management",
                "Agent clustering and load balancing"
            ]
        },
        {
            "module": "canoe_client_examples",
            "title": "CANoe Client Examples",
            "description": "Vector CANoe integration for CAN bus testing and simulation",
            "features": [
                "CANoe connection and control",
                "CAN message handling",
                "Test automation execution",
                "Signal monitoring and analysis", 
                "Diagnostic communication",
                "Advanced CANoe automation"
            ]
        },
        {
            "module": "device_client_examples",
            "title": "Device Client Examples",
            "description": "General device management and communication",
            "features": [
                "Device connection and information",
                "Configuration management",
                "File management operations",
                "Device monitoring and health",
                "Device automation and scripting",
                "Multi-device coordination"
            ]
        },
        {
            "module": "diagnostic_example",
            "title": "Diagnostic Client Examples", 
            "description": "Socket and serial diagnostic communication",
            "features": [
                "Socket-based DLT message reception",
                "Serial diagnostic communication",
                "Message filtering and analysis",
                "Real-time message processing",
                "Advanced DLT operations"
            ]
        }
    ]
    
    for example in examples:
        print_section(example["title"])
        print(f"Module: {example['module']}.py")
        print(f"Description: {example['description']}")
        print("Features:")
        for feature in example["features"]:
            print(f"  • {feature}")
        print()
    
    return examples


def run_all_examples():
    """Run all example modules."""
    
    print_header("Running All VTA API Examples")
    
    examples = [
        ("adb_client_examples", "ADB Client Examples"),
        ("hardware_client_examples", "Hardware Client Examples"), 
        ("network_client_examples", "Network Client Examples"),
        ("agent_client_examples", "Agent Client Examples"),
        ("canoe_client_examples", "CANoe Client Examples"),
        ("device_client_examples", "Device Client Examples"),
        ("diagnostic_example", "Diagnostic Client Examples")
    ]
    
    for module_name, description in examples:
        run_example_module(module_name, description)
    
    print_header("All Examples Completed")


def run_specific_examples():
    """Run specific examples based on user selection."""
    
    examples = show_examples_overview()
    
    print_header("Example Selection")
    print("Available examples:")
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['title']}")
    
    print(f"{len(examples) + 1}. Run all examples")
    print("0. Exit")
    
    while True:
        try:
            choice = input(f"\nSelect example to run (0-{len(examples) + 1}): ").strip()
            
            if choice == "0":
                print("Exiting...")
                break
            elif choice == str(len(examples) + 1):
                run_all_examples()
                break
            elif choice.isdigit() and 1 <= int(choice) <= len(examples):
                example = examples[int(choice) - 1]
                run_example_module(example["module"], example["title"])
                break
            else:
                print(f"Invalid choice. Please enter a number between 0 and {len(examples) + 1}")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


def show_quick_start_guide():
    """Show quick start guide for VTA API."""
    
    print_header("VTA API Quick Start Guide")
    
    print("""
Getting Started with VTA API:

1. INSTALLATION
   - Ensure Python 3.8+ is installed
   - Install required dependencies:
     pip install pyserial loguru requests

2. BASIC USAGE
   from vta.api.factory import APIFactory
   
   # Create a client
   client = APIFactory.create_adb_client(device_id="emulator-5554")
   
   # Connect and use
   client.connect()
   result = client.execute_command("getprop ro.build.version.release")
   client.disconnect()

3. FACTORY METHODS
   Available factory methods for creating clients:
   
   • APIFactory.create_adb_client()        - Android Debug Bridge
   • APIFactory.create_hardware_client()   - Hardware control
   • APIFactory.create_network_client()    - HTTP/REST APIs
   • APIFactory.create_agent_client()      - VTA agent communication
   • APIFactory.create_canoe_client()      - Vector CANoe integration
   • APIFactory.create_device_client()     - General device management
   • APIFactory.create_dlt_client()        - DLT diagnostic (socket)
   • APIFactory.create_serial_client()     - Serial diagnostic

4. CONFIGURATION
   Use ClientConfig for advanced configuration:
   
   config = ClientConfig(
       timeout=30.0,
       retry_count=3,
       extra_config={"custom_param": "value"}
   )
   client = APIFactory.create_client(ClientType.ADB_CLIENT, config)

5. ERROR HANDLING
   All clients use consistent error handling:
   
   try:
       client.connect()
       result = client.some_operation()
   except ConnectionError:
       print("Connection failed")
   except OperationError:
       print("Operation failed")
   except TimeoutError:
       print("Operation timed out")
   finally:
       client.disconnect()

6. EXAMPLES
   Run specific examples:
   • python examples/adb_client_examples.py
   • python examples/hardware_client_examples.py
   • python examples/network_client_examples.py
   • etc.

7. DOCUMENTATION
   Check the docs/ directory for detailed documentation:
   • API reference
   • Configuration guides
   • Best practices
   • Troubleshooting

For more information, see the README.md file or run specific examples.
    """)


def main():
    """Main function for the examples index."""
    
    print_header("VTA API Client Examples")
    
    print("""
Welcome to the VTA API Client Examples!

This collection demonstrates the capabilities of all VTA API clients
through practical, runnable examples.

Choose an option:
1. Show examples overview
2. Run specific examples
3. Run all examples
4. Show quick start guide
5. Exit
    """)
    
    while True:
        try:
            choice = input("Select option (1-5): ").strip()
            
            if choice == "1":
                show_examples_overview()
            elif choice == "2":
                run_specific_examples()
            elif choice == "3":
                run_all_examples()
            elif choice == "4":
                show_quick_start_guide()
            elif choice == "5":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()

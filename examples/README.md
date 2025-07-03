# VTA API Client Examples

This directory contains comprehensive examples for all VTA API clients, demonstrating their capabilities and usage patterns.

## 📁 Available Examples

### 🤖 ADB Client Examples (`adb_client_examples.py`)
**Android Debug Bridge integration for mobile device automation**

- **Basic ADB Operations**: Device connection, information retrieval
- **Application Management**: Install/uninstall apps, start/stop applications
- **File Operations**: Push/pull files, directory management
- **UI Automation**: Screen interactions, input simulation, screenshots
- **Device Information**: Battery, memory, storage, network info
- **Multi-device Management**: Coordinate multiple Android devices

```python
# Quick example
adb = APIFactory.create_adb_client(device_id="emulator-5554")
adb.connect()
adb.take_screenshot("screenshot.png")
adb.tap_screen(500, 300)
adb.disconnect()
```

### 🔧 Hardware Client Examples (`hardware_client_examples.py`)
**Hardware control for relays, power supplies, and automation**

- **Relay Control**: Cleware USB relays, serial relay modules
- **Power Supply Management**: Voltage/current control, power cycling
- **Serial Hardware Communication**: Custom hardware protocols
- **Automation Sequences**: Complex hardware automation
- **Hardware Monitoring**: Status monitoring and health checks
- **Multi-hardware Coordination**: Synchronized hardware operations

```python
# Quick example
relay = APIFactory.create_relay_client()
relay.connect()
relay.set_relay_state(1, True)  # Turn on relay 1
relay.set_all_relays(False)     # Turn off all relays
relay.disconnect()
```

### 🌐 Network Client Examples (`network_client_examples.py`)
**HTTP/HTTPS communication for web APIs and REST services**

- **Basic HTTP Operations**: GET, POST, PUT, DELETE requests
- **REST API Integration**: JSON APIs, RESTful services
- **File Upload/Download**: Multipart uploads, binary downloads
- **Authentication**: Bearer tokens, basic auth, custom headers
- **Streaming**: Chunked encoding, large file handling
- **Advanced Features**: SSL, redirects, cookies, compression

```python
# Quick example
api = APIFactory.create_network_client(base_url="https://api.example.com")
api.connect()
response = api.get("/users", params={"limit": 10})
data = response.json()
api.disconnect()
```

### 🤖 Agent Client Examples (`agent_client_examples.py`)
**VTA agent communication for test automation and orchestration**

- **Agent Connection**: Connect to VTA agent services
- **Test Execution**: Submit and monitor test jobs
- **Device Management**: Device reservation and control through agent
- **Resource Monitoring**: System resources and performance metrics
- **Configuration Management**: Agent configuration and settings
- **Clustering**: Multi-agent coordination and load balancing

```python
# Quick example
agent = APIFactory.create_agent_client(host="localhost", port=6666)
agent.connect()
job_id = agent.submit_test_job({"test_suite": "smoke_tests"})
status = agent.get_job_status(job_id)
agent.disconnect()
```

### 🚗 CANoe Client Examples (`canoe_client_examples.py`)
**Vector CANoe integration for CAN bus testing and simulation**

- **CANoe Control**: Start/stop measurements, load configurations
- **CAN Message Handling**: Send/receive CAN messages
- **Test Automation**: Execute CANoe test modules
- **Signal Monitoring**: Monitor and analyze CAN signals
- **Diagnostic Communication**: ECU diagnosis via CAN
- **Advanced Automation**: Performance monitoring, batch testing

```python
# Quick example
canoe = APIFactory.create_canoe_client()
canoe.connect()
canoe.load_configuration("test_config.cfg")
canoe.start_measurement()
canoe.send_can_message(0x123, [0x01, 0x02, 0x03, 0x04])
canoe.disconnect()
```

### 📱 Device Client Examples (`device_client_examples.py`) 
**General device management and communication**

- **Device Operations**: Connection, information, status
- **Configuration Management**: Get/set device parameters
- **File Management**: Upload/download files, directory operations
- **Device Monitoring**: Health checks, performance metrics
- **Automation**: Scripting, scheduled operations, batch commands
- **Multi-device Coordination**: Synchronized device operations

```python
# Quick example
device = APIFactory.create_device_client(device_id="192.168.1.100")
device.connect()
info = device.get_device_info()
device.set_configuration_parameter("timeout", 30)
device.disconnect()
```

### 🔍 Diagnostic Client Examples (`diagnostic_example.py`)
**Socket and serial diagnostic communication**

- **Socket-based DLT Reception**: Real-time DLT message handling
- **Serial Communication**: Direct serial port communication
- **Message Filtering**: Advanced message filtering and analysis
- **Real-time Processing**: Custom message handlers
- **Data Export**: Export diagnostic data for analysis

```python
# Quick example - DLT socket
dlt = APIFactory.create_dlt_client(socket_host="192.168.1.100", socket_port=3490)
dlt.connect()
dlt.start_dlt_reception()
messages = dlt.get_recent_messages(count=10)
dlt.disconnect()

# Quick example - Serial
serial = APIFactory.create_serial_client(serial_port="COM1", baudrate=115200)
serial.connect()
response = serial.send_command("AT+VERSION")
serial.disconnect()
```

## 🚀 Running Examples

### Individual Examples
Run specific client examples:

```bash
# Run ADB client examples
python examples/adb_client_examples.py

# Run hardware client examples  
python examples/hardware_client_examples.py

# Run network client examples
python examples/network_client_examples.py

# Run agent client examples
python examples/agent_client_examples.py

# Run CANoe client examples
python examples/canoe_client_examples.py

# Run device client examples
python examples/device_client_examples.py

# Run diagnostic client examples
python examples/diagnostic_example.py
```

### Interactive Examples Runner
Use the interactive examples index:

```bash
python examples/README.py
```

This provides an interactive menu to:
- Browse example descriptions
- Run specific examples
- Run all examples
- View quick start guide

## 📋 Prerequisites

### Software Requirements
- Python 3.8 or higher
- Required Python packages:
  ```bash
  pip install pyserial loguru requests
  ```

### Hardware/Software Setup (as needed)
- **ADB Examples**: Android SDK platform-tools, connected Android devices/emulators
- **Hardware Examples**: Relay hardware (Cleware USB or serial), power supplies
- **Network Examples**: Internet connection for public APIs
- **Agent Examples**: VTA agent service running
- **CANoe Examples**: Vector CANoe software and CAN hardware
- **Device Examples**: Target devices accessible via network
- **Diagnostic Examples**: DLT-enabled devices or serial diagnostic interfaces

## 🔧 Configuration

### Environment Variables
Set these environment variables for better example experience:

```bash
# ADB path (if not in system PATH)
export ADB_PATH=/path/to/adb

# CANoe installation path
export CANOE_PATH="C:/Program Files/Vector CANoe"

# Hardware paths
export CLEWARE_PATH=vta/bin/cleware
```

### Example Configuration Files
Some examples reference configuration files:

- **CANoe**: Place `.cfg` files in `C:/CANoe_Configs/`
- **Hardware**: Configure COM ports and device paths
- **Network**: Update URLs and endpoints as needed

## 📖 Example Structure

Each example file follows a consistent structure:

1. **Basic Operations**: Fundamental client usage
2. **Advanced Features**: Complex operations and configurations  
3. **Real-world Scenarios**: Practical automation examples
4. **Error Handling**: Robust error handling patterns
5. **Cleanup**: Proper resource cleanup

### Example Function Pattern
```python
def example_operation():
    """Description of what this example demonstrates."""
    print("=== Example Title ===")
    
    # Create client
    client = APIFactory.create_xxx_client(...)
    
    try:
        # Connect
        client.connect()
        
        # Perform operations
        result = client.some_operation()
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Always cleanup
        client.disconnect()
```

## 🛠️ Customization

### Adapting Examples
To adapt examples for your environment:

1. **Update Device IDs**: Change IP addresses, serial numbers, device paths
2. **Modify Parameters**: Adjust timeouts, retry counts, configurations
3. **Custom Protocols**: Extend examples for your specific hardware/software
4. **Add Logging**: Enable detailed logging for debugging

### Example Customization
```python
# Custom configuration
config = ClientConfig(
    timeout=60.0,
    retry_count=5,
    extra_config={
        "custom_param": "your_value",
        "debug_mode": True
    }
)

client = APIFactory.create_client(ClientType.YOUR_CLIENT, config)
```

## 🐛 Troubleshooting

### Common Issues

1. **Connection Failures**
   - Check device connectivity
   - Verify IP addresses/ports
   - Ensure services are running

2. **Import Errors**
   - Install required dependencies
   - Check Python path configuration
   - Verify VTA API installation

3. **Permission Issues**
   - Run with appropriate privileges
   - Check device permissions
   - Verify access credentials

4. **Hardware Not Found**
   - Check hardware connections
   - Verify driver installation
   - Update device paths/ports

### Debugging Tips
- Enable debug logging: `log_level="DEBUG"`
- Use longer timeouts for slow operations
- Check example output for error details
- Verify prerequisites are met

## 📚 Additional Resources

- **API Documentation**: `docs/` directory
- **Configuration Guide**: `docs/configuration.md`
- **Best Practices**: `docs/best_practices.md`
- **Troubleshooting**: `docs/troubleshooting.md`

## 🤝 Contributing

To add new examples:

1. Follow the existing example structure
2. Include comprehensive error handling
3. Add clear documentation and comments
4. Test with various configurations
5. Update this README with new examples

## 📝 License

Copyright (C) 2024 Robert Bosch GmbH. All rights reserved.

# VTA API Refactoring Guide

## Overview

The VTA (Vite Test Automation) API has been completely refactored to provide a more readable, user-friendly, and maintainable interface. The new design follows modern Python practices and provides a consistent experience across all API clients.

## Key Improvements

### 1. **Unified Base Architecture**
- All clients inherit from a common `BaseClient` class
- Consistent error handling and logging across all clients
- Built-in retry mechanisms and timeout management
- Context manager support for automatic resource cleanup

### 2. **Factory Pattern**
- Centralized client creation through `APIFactory`
- Automatic configuration management
- Easy client discovery and instantiation

### 3. **Enhanced Error Handling**
- Custom exception hierarchy for different error types
- Detailed error messages with context information
- Graceful failure handling with proper cleanup

### 4. **Type Safety and Documentation**
- Full type hints throughout the codebase
- Comprehensive docstrings with examples
- Input validation and sanitization

### 5. **Configuration Management**
- Centralized configuration through `ClientConfig` class
- Default configurations for all client types
- Override capabilities for specific use cases

## Usage Examples

### Basic Client Creation

```python
from vta.api import APIFactory, ClientType, ClientConfig

# Method 1: Using factory convenience methods
adb = APIFactory.create_adb_client(device_id="emulator-5554")
device = APIFactory.create_device_client(device_id="192.168.1.100")
agent = APIFactory.create_agent_client(host="localhost", port=6666)

# Method 2: Using generic factory method
config = ClientConfig(device_id="emulator-5554", timeout=60)
adb = APIFactory.create_client(ClientType.ADB_CLIENT, config)
```

### ADB Client Usage

```python
from vta.api import ADBClient, ClientConfig

# Basic usage
config = ClientConfig(device_id="emulator-5554")
adb = ADBClient(config)

# UI interactions
adb.tap(100, 200)
adb.swipe(100, 200, 300, 400)
adb.long_press(150, 250, duration=3000)

# Get device information
device_info = adb.get_device_info()
print(f"Device: {device_info['brand']} {device_info['model']}")

# Using context manager (recommended)
with ADBClient(config) as adb:
    adb.tap(100, 200)
    screen_size = adb.get_screen_size()
    print(f"Screen: {screen_size[0]}x{screen_size[1]}")
```

### Device Client Usage

```python
from vta.api import DeviceClient, ClientConfig, ElementSelector

# App management
config = ClientConfig(device_id="192.168.1.100")
with DeviceClient(config) as device:
    # Install and start app
    device.install_app("/path/to/app.apk", grant_permissions=True)
    device.start_app("com.example.app")
    
    # UI interactions
    device.click_element("Login")
    device.input_text("username", "testuser")
    
    # Advanced element selection
    selector = ElementSelector(
        resource_id="com.example:id/login_button",
        text="Login"
    )
    device.click_element(selector)
    
    # App lifecycle
    device.stop_app("com.example.app")
    device.uninstall_app("com.example.app")
```

### Agent Client Usage

```python
from vta.api import AgentClient, ClientConfig

# Basic communication
config = ClientConfig(host="192.168.1.50", port=6666)
with AgentClient(config) as agent:
    # Send commands
    response = agent.send_command({"action": "get_status"})
    print(f"Agent status: {response}")
    
    # Execute scripts
    result = agent.execute_script("test_script.py", args={"param1": "value1"})
    
    # Task management
    task_result = agent.start_agent_task("data_collection", {"duration": 60})
    task_id = task_result.get("task_id")
    
    # Health check
    health = agent.health_check()
    print(f"Agent health: {health['status']}")
```

### Network Client Usage

```python
from vta.api import NetworkClient, ClientConfig

# REST API operations
config = ClientConfig(extra_config={"base_url": "https://api.example.com"})
with NetworkClient(config) as http:
    # Authentication
    http.set_auth_token("your-api-token")
    
    # GET request
    users = http.get("/users", params={"page": 1, "limit": 10})
    
    # POST request
    new_user = http.post("/users", json_data={
        "name": "John Doe",
        "email": "john@example.com"
    })
    
    # Custom headers
    http.set_custom_headers({"X-Custom-Header": "value"})
    response = http.get("/protected-endpoint")
```

### CANoe Client Usage

```python
from vta.api import CANoeClient, ClientConfig

# CANoe operations
with CANoeClient() as canoe:
    # Configuration management
    canoe.open_configuration("test_config.cfg")
    
    # Measurement control
    canoe.start_measurement()
    
    # Environment variables
    canoe.set_environment_variable("TestSpeed", 50.0)
    speed = canoe.get_environment_variable("TestSpeed")
    
    # Diagnostic operations
    response = canoe.send_diagnostic_request("22 F1 90")
    
    canoe.stop_measurement()
```

## Configuration Options

### ClientConfig Parameters

```python
from vta.api import ClientConfig

config = ClientConfig(
    # Connection settings
    timeout=30.0,              # Operation timeout in seconds
    retry_count=3,             # Number of retry attempts
    retry_delay=1.0,           # Delay between retries
    auto_connect=True,         # Automatically connect on creation
    
    # Device/Service specific
    device_id="emulator-5554", # Device identifier
    host="localhost",          # Server host
    port=6666,                 # Server port
    
    # Performance settings
    connection_pool_size=5,    # Connection pool size
    
    # Behavior settings
    validate_inputs=True,      # Enable input validation
    log_level="INFO",          # Logging level
    
    # Additional configuration
    extra_config={             # Client-specific config
        "adb_path": "/usr/bin/adb",
        "base_url": "https://api.example.com"
    }
)
```

## Error Handling

The refactored API provides a comprehensive error handling system:

```python
from vta.api import VTAError, ConnectionError, OperationError, ValidationError, TimeoutError

try:
    with ADBClient(config) as adb:
        adb.tap(100, 200)
        
except ConnectionError as e:
    print(f"Failed to connect: {e}")
    print(f"Error code: {e.error_code}")
    print(f"Details: {e.details}")
    
except ValidationError as e:
    print(f"Invalid input: {e}")
    
except TimeoutError as e:
    print(f"Operation timed out: {e}")
    
except OperationError as e:
    print(f"Operation failed: {e}")
    
except VTAError as e:
    print(f"General VTA error: {e}")
```

## Migration from Old API

### Before (Old API)
```python
from vta.api.ADBClient import ADBClient
from vta.api.DeviceClient import DeviceClient

# Manual initialization
adb = ADBClient(adb_path="adb", device_id="emulator-5554")
adb.click_coordinates(100, 200)

device = DeviceClient()
device.connect("192.168.1.100")
device.install_apk("app.apk")
```

### After (New API)
```python
from vta.api import APIFactory, ClientType

# Factory-based creation with configuration
adb = APIFactory.create_adb_client(device_id="emulator-5554")
adb.tap(100, 200)  # More intuitive method names

device = APIFactory.create_device_client(device_id="192.168.1.100")
device.install_app("app.apk")  # Automatic connection management
```

## Best Practices

### 1. Use Context Managers
```python
# Recommended
with APIFactory.create_adb_client(device_id="emulator-5554") as adb:
    adb.tap(100, 200)
# Automatic cleanup

# Not recommended
adb = APIFactory.create_adb_client(device_id="emulator-5554")
adb.tap(100, 200)
adb.disconnect()  # Manual cleanup required
```

### 2. Handle Errors Gracefully
```python
try:
    with DeviceClient(config) as device:
        device.install_app("app.apk")
except ValidationError:
    print("APK file not found or invalid")
except ConnectionError:
    print("Could not connect to device")
except OperationError:
    print("Installation failed")
```

### 3. Use Configuration Objects
```python
# Recommended - reusable configuration
config = ClientConfig(
    device_id="emulator-5554",
    timeout=60,
    retry_count=5
)

adb = ADBClient(config)
device = DeviceClient(config)

# Not recommended - scattered parameters
adb = APIFactory.create_adb_client(device_id="emulator-5554", timeout=60)
```

### 4. Leverage Type Hints
```python
from typing import Optional
from vta.api import ADBClient, ClientConfig

def setup_device(device_id: str, timeout: float = 30.0) -> Optional[ADBClient]:
    try:
        config = ClientConfig(device_id=device_id, timeout=timeout)
        return ADBClient(config)
    except Exception:
        return None
```

## Advanced Features

### Custom Client Registration
```python
from vta.api import APIFactory, BaseClient

class CustomClient(BaseClient):
    def connect(self) -> bool:
        # Implementation
        return True
    
    def disconnect(self) -> bool:
        # Implementation
        return True
    
    def is_connected(self) -> bool:
        # Implementation
        return True

# Register custom client
APIFactory.register_client("custom_client", CustomClient)

# Use custom client
client = APIFactory.create_client("custom_client")
```

### Health Monitoring
```python
def monitor_client_health(client: BaseClient):
    status = client.get_status()
    print(f"Client: {status['client_type']}")
    print(f"Connected: {status['connected']}")
    print(f"Config: {status['config']}")
    
    if hasattr(client, 'health_check'):
        health = client.health_check()
        print(f"Health: {health['status']}")
```

This refactored API provides a much more maintainable, readable, and user-friendly interface while maintaining backward compatibility where possible and providing clear migration paths for existing code.

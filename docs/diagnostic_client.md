# DiagnosticClient - Socket and Serial Communication

The DiagnosticClient has been refactored to use direct socket and serial communication instead of TCP/Putty/SSH connections. This provides better performance, reliability, and simpler configuration for diagnostic operations.

## Features

### Socket-based DLT Reception
- Direct socket connection for DLT (Diagnostic Log and Trace) message reception
- Real-time message parsing and filtering
- Multi-threaded message reception
- Message handlers for custom processing
- Built-in message buffering and statistics

### Serial Communication
- Direct serial port communication using pyserial
- Support for diagnostic commands and raw data transmission
- Configurable serial parameters (baudrate, parity, etc.)
- Command/response handling with timeout support
- Raw data transmission capabilities

## Usage Examples

### Socket-based DLT Reception

```python
from vta.api.factory import APIFactory

# Create DLT client for socket communication
dlt_client = APIFactory.create_dlt_client(
    socket_host="192.168.1.100",  # ECU IP address
    socket_port=3490,             # DLT port
    timeout=30.0
)

# Connect and start reception
dlt_client.connect()
dlt_client.start_dlt_reception()

# Process messages for 30 seconds
time.sleep(30)

# Stop and get statistics
dlt_client.stop_dlt_reception()
stats = dlt_client.get_statistics()
print(f"Total messages: {stats['total_messages']}")

# Get recent messages
recent = dlt_client.get_recent_messages(count=100)
for msg in recent:
    print(f"{msg.app_id}.{msg.context_id}: {msg.payload}")

dlt_client.disconnect()
```

### Serial Diagnostic Communication

```python
from vta.api.factory import APIFactory

# Create serial diagnostic client
serial_client = APIFactory.create_serial_client(
    serial_port="COM1",
    baudrate=115200,
    timeout=10.0
)

# Connect and send commands
serial_client.connect()

# Send AT commands
response = serial_client.send_command("AT+VERSION", expect_response=True)
print(f"Version: {response}")

# Send raw binary data
raw_data = b'\x7E\x01\x02\x03\x7E'
serial_client.send_raw_data(raw_data)

# Read available data
data = serial_client.read_available_data(timeout=2.0)
print(f"Received: {data}")

serial_client.disconnect()
```

### Message Handling and Filtering

```python
def my_message_handler(message):
    """Custom DLT message handler."""
    if message.log_level == "ERROR":
        print(f"ERROR: {message.payload}")

# Add handler for real-time processing
dlt_client.add_message_handler(my_message_handler)
dlt_client.start_dlt_reception()

# Filter collected messages
error_messages = dlt_client.filter_messages(log_level="ERROR")
app_messages = dlt_client.filter_messages(app_id="MY_APP")
recent_messages = dlt_client.filter_messages(since=time.time() - 60)
```

## Configuration Options

### Socket Mode (DLT)
- `mode`: "socket"
- `socket_host`: DLT server IP address
- `socket_port`: DLT server port (typically 3490)
- `timeout`: Connection timeout

### Serial Mode
- `mode`: "serial"
- `serial_port`: Serial port name (e.g., "COM1", "/dev/ttyUSB0")
- `baudrate`: Communication speed (default: 115200)
- `bytesize`: Data bits (default: 8)
- `parity`: Parity checking (default: 'N')
- `stopbits`: Stop bits (default: 1)
- `timeout`: Read timeout
- `xonxoff`: Software flow control
- `rtscts`: Hardware flow control
- `dsrdtr`: DSR/DTR flow control

## Factory Methods

The factory provides convenient methods for creating diagnostic clients:

```python
# DLT socket client
dlt_client = APIFactory.create_dlt_client(
    socket_host="192.168.1.100",
    socket_port=3490
)

# Serial diagnostic client
serial_client = APIFactory.create_serial_client(
    serial_port="COM1",
    baudrate=115200
)

# Generic diagnostic client with custom config
config = ClientConfig(extra_config={
    "mode": "socket",
    "socket_host": "10.0.0.100",
    "socket_port": 3490
})
diag_client = APIFactory.create_client(ClientType.DIAGNOSTIC_CLIENT, config)
```

## Error Handling

The DiagnosticClient provides comprehensive error handling:

```python
try:
    serial_client.connect()
    response = serial_client.send_command("AT+VERSION")
except ConnectionError as e:
    print(f"Connection failed: {e}")
except TimeoutError as e:
    print(f"Operation timed out: {e}")
except ValidationError as e:
    print(f"Invalid configuration: {e}")
except OperationError as e:
    print(f"Operation failed: {e}")
```

## Dependencies

The DiagnosticClient requires:
- `socket` (built-in Python module)
- `pyserial` for serial communication (install with `pip install pyserial`)
- `loguru` for logging

## Migration from Legacy Implementation

If you were using the old TCP/Putty-based implementation:

### Old Usage (TCP/Putty)
```python
# Old TCP-based approach
putty_client = create_putty_client(host="192.168.1.100", protocol="ssh")
```

### New Usage (Socket/Serial)
```python
# New socket-based approach for DLT
dlt_client = APIFactory.create_dlt_client(
    socket_host="192.168.1.100",
    socket_port=3490
)

# New serial-based approach for direct communication
serial_client = APIFactory.create_serial_client(
    serial_port="COM1",
    baudrate=115200
)
```

## Performance Benefits

The new socket/serial implementation provides:
- **Faster connection establishment** - Direct socket/serial vs SSH overhead
- **Lower latency** - No intermediate protocol layers
- **Better resource usage** - Native Python socket/serial handling
- **Simplified configuration** - No external tool dependencies
- **More reliable** - Direct control over connection handling

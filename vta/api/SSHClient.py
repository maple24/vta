# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

import queue
import re
import threading
import time
from dataclasses import dataclass
from functools import wraps
from typing import Optional, Tuple, List, Dict, Any, Callable, Union
from contextlib import contextmanager
import io

import paramiko
from loguru import logger

from .SerialClient import (
    ConnectionState, 
    SerialInterface, 
    QueueManager,
    require_connection,
)


class SSHConnectionError(Exception):
    """Custom exception for SSH connection errors."""
    pass


class SSHAuthenticationError(Exception):
    """Custom exception for SSH authentication errors."""
    pass


@dataclass
class SSHConfig:
    """Configuration for SSH connection."""
    
    enabled: bool = True
    hostname: str = ""
    port: int = 22
    username: str = "root"
    password: str = ""
    key_file: str = ""
    timeout: float = 10.0
    keepalive_interval: int = 30
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "SSHConfig":
        """Create config from dictionary."""
        return cls(
            enabled=config.get("ssh_enabled", True),
            hostname=config.get("ssh_hostname", ""),
            port=int(config.get("ssh_port", 22)),
            username=config.get("ssh_username", "root"),
            password=config.get("ssh_password", ""),
            key_file=config.get("ssh_key_file", ""),
            timeout=float(config.get("ssh_timeout", 10.0)),
            keepalive_interval=int(config.get("ssh_keepalive_interval", 30)),
        )


def safe_ssh_operation(func: Callable) -> Callable:
    """Decorator for safe SSH operations with error handling."""
    
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except (paramiko.SSHException, paramiko.AuthenticationException, OSError) as e:
            logger.error(f"SSH operation failed in {func.__name__}: {e}")
            raise SSHConnectionError(f"SSH operation failed: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error in {func.__name__}: {e}")
            raise
    
    return wrapper


class SSHClient(SerialInterface):
    """SSH client for remote device interaction."""
    
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    
    def __init__(self):
        self._ssh_client: Optional[paramiko.SSHClient] = None
        self._shell_channel: Optional[paramiko.Channel] = None
        self._wait_queue: queue.Queue[Tuple[float, str]] = queue.Queue()
        self._monitor_queue: queue.Queue[Tuple[float, str]] = queue.Queue()
        self._wait_event = threading.Event()
        self._monitor_event = threading.Event()
        self._reader_event = threading.Event()
        self._reader_thread: Optional[threading.Thread] = None
        self._config: Optional[SSHConfig] = None
        self._state = ConnectionState.DISCONNECTED
        self._lock = threading.RLock()
        self._shell_buffer = io.StringIO()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
    
    @property
    def is_connected(self) -> bool:
        """Check if the SSH connection is active."""
        with self._lock:
            return (self._state == ConnectionState.CONNECTED and 
                   self._ssh_client and 
                   self._shell_channel and 
                   not self._shell_channel.closed)
    
    @property
    def state(self) -> ConnectionState:
        """Get current connection state."""
        return self._state
    
    def _ssh_reader(self) -> None:
        """Continuously read data from SSH shell channel."""
        logger.info("SSH reader thread started")
        try:
            while self._reader_event.is_set():
                if not self._shell_channel or self._shell_channel.closed:
                    break
                
                try:
                    if self._shell_channel.recv_ready():
                        data = self._shell_channel.recv(4096).decode('utf-8', 'ignore')
                        if data:
                            self._shell_buffer.write(data)
                            
                            # Process complete lines
                            buffer_content = self._shell_buffer.getvalue()
                            lines = buffer_content.split('\n')
                            
                            # Keep the last incomplete line in buffer
                            self._shell_buffer = io.StringIO()
                            if not buffer_content.endswith('\n'):
                                self._shell_buffer.write(lines[-1])
                                lines = lines[:-1]
                            
                            # Process complete lines
                            for line in lines:
                                line = line.strip()
                                if line:
                                    logger.trace("[SSHRx] - {message}", message=line)
                                    timestamp = time.time()
                                    
                                    if self._monitor_event.is_set():
                                        self._monitor_queue.put((timestamp, line))
                                    if self._wait_event.is_set():
                                        self._wait_queue.put((timestamp, line))
                    
                    time.sleep(0.01)  # Small delay to prevent CPU spinning
                    
                except (paramiko.SSHException, OSError) as e:
                    logger.error(f"SSH read error: {e}")
                    self._state = ConnectionState.ERROR
                    break
        except Exception as e:
            logger.exception(f"Unexpected error in SSH reader: {e}")
            self._state = ConnectionState.ERROR
        finally:
            logger.info("SSH reader thread terminated")
    
    def _authenticate(self) -> None:
        """Authenticate SSH connection using password or key file."""
        if not self._config:
            raise SSHConnectionError("No configuration available")
        
        try:
            if self._config.key_file:
                logger.info(f"Authenticating with key file: {self._config.key_file}")
                self._ssh_client.connect(
                    hostname=self._config.hostname,
                    port=self._config.port,
                    username=self._config.username,
                    key_filename=self._config.key_file,
                    timeout=self._config.timeout
                )
            elif self._config.password:
                logger.info("Authenticating with password")
                self._ssh_client.connect(
                    hostname=self._config.hostname,
                    port=self._config.port,
                    username=self._config.username,
                    password=self._config.password,
                    timeout=self._config.timeout
                )
            else:
                raise SSHAuthenticationError("No authentication method provided")
                
        except paramiko.AuthenticationException as e:
            raise SSHAuthenticationError(f"Authentication failed: {e}")
        except Exception as e:
            raise SSHConnectionError(f"Connection failed: {e}")
    
    def connect(self, config: Union[Dict[str, Any], SSHConfig]) -> None:
        """
        Establish SSH connection with the given configuration.
        
        Args:
            config: Dictionary or SSHConfig object containing connection parameters
        """
        if isinstance(config, dict):
            self._config = SSHConfig.from_dict(config)
        else:
            self._config = config
        
        if not self._config.enabled:
            logger.warning("SSH disabled in configuration")
            return
        
        with self._lock:
            if self._state == ConnectionState.CONNECTED:
                logger.warning("Already connected")
                return
            
            self._state = ConnectionState.CONNECTING
            logger.info("Establishing SSH connection...")
            
            try:
                if not self._config.hostname:
                    raise SSHConnectionError("No hostname specified")
                
                # Create SSH client
                self._ssh_client = paramiko.SSHClient()
                self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                # Authenticate and connect
                self._authenticate()
                
                # Create interactive shell
                self._shell_channel = self._ssh_client.invoke_shell()
                self._shell_channel.settimeout(self._config.timeout)
                
                # Set keepalive
                transport = self._ssh_client.get_transport()
                if transport:
                    transport.set_keepalive(self._config.keepalive_interval)
                
                # Start reader thread
                self._reader_event.set()
                self._reader_thread = threading.Thread(
                    target=self._ssh_reader, 
                    daemon=True, 
                    name="SSHReader"
                )
                self._reader_thread.start()
                
                self._state = ConnectionState.CONNECTED
                logger.success(f"Connected to {self._config.hostname}:{self._config.port}")
                
                # Wait for initial shell prompt
                time.sleep(1.0)
                
            except Exception as e:
                self._state = ConnectionState.ERROR
                logger.exception("Failed to establish SSH connection")
                raise SSHConnectionError(f"Connection failed: {e}")
    
    def disconnect(self) -> None:
        """Close the SSH connection and cleanup resources."""
        with self._lock:
            if self._state == ConnectionState.DISCONNECTED:
                return
            
            logger.info("Disconnecting from SSH...")
            self._state = ConnectionState.DISCONNECTED
            
            # Stop reader thread
            self._reader_event.clear()
            self._wait_event.clear()
            self._monitor_event.clear()
            
            # Wait for thread to finish
            if self._reader_thread and self._reader_thread.is_alive():
                self._reader_thread.join(timeout=2.0)
            
            # Close shell channel
            if self._shell_channel:
                self._shell_channel.close()
                self._shell_channel = None
            
            # Close SSH connection
            if self._ssh_client:
                self._ssh_client.close()
                self._ssh_client = None
            
            logger.info("SSH connection closed")
    
    @require_connection
    @safe_ssh_operation
    def send_command(self, command: str) -> None:
        """
        Send command to the SSH shell.
        
        Args:
            command: Command string to send
        """
        command = command.rstrip()
        self._shell_channel.send(f"{command}\n")
        logger.info("[SSHTx] - {message}", message=command)
    
    @require_connection
    def execute_command(self, command: str, wait_time: float = 1.0) -> List[str]:
        """
        Execute command and return captured output.
        
        Args:
            command: Command to execute
            wait_time: Time to wait for output
        
        Returns:
            List of output lines
        """
        # Clear queue and enable monitoring before sending command
        QueueManager.clear_queue(self._wait_queue)
        self._wait_event.set()
        
        try:
            self.send_command(command)
            if wait_time > 0:
                time.sleep(wait_time)
            
            return QueueManager.extract_lines(self._wait_queue)
        finally:
            self._wait_event.clear()
    
    @require_connection
    def execute_command_with_exit_code(self, command: str, timeout: float = 30.0) -> Tuple[List[str], int]:
        """
        Execute command using exec_command and return output with exit code.
        
        Args:
            command: Command to execute
            timeout: Command timeout
            
        Returns:
            Tuple of (output_lines, exit_code)
        """
        try:
            stdin, stdout, stderr = self._ssh_client.exec_command(command, timeout=timeout)
            
            # Read output
            output_lines = []
            for line in stdout:
                line = line.strip()
                if line:
                    output_lines.append(line)
                    logger.trace("[SSHExec] - {message}", message=line)
            
            # Read errors
            error_lines = []
            for line in stderr:
                line = line.strip()
                if line:
                    error_lines.append(line)
                    logger.warning("[SSHErr] - {message}", message=line)
            
            # Get exit code
            exit_code = stdout.channel.recv_exit_status()
            
            # Combine output and errors
            all_output = output_lines + error_lines
            
            logger.info(f"Command '{command}' completed with exit code: {exit_code}")
            return all_output, exit_code
            
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise SSHConnectionError(f"Command execution failed: {e}")
    
    def _wait_for_pattern(
        self, pattern: str, command: str = "", timeout: float = 10.0
    ) -> Tuple[bool, Optional[Tuple]]:
        """Internal method to wait for a specific pattern."""
        if not self.is_connected:
            raise SSHConnectionError("Not connected to SSH")
        
        self._wait_event.set()
        start_time = time.time()
        
        try:
            if command:
                self.send_command(command)
            
            while True:
                if time.time() - start_time > timeout:
                    logger.warning(f"Timeout waiting for pattern: {pattern}")
                    return False, None
                
                try:
                    timestamp, line = self._wait_queue.get(timeout=0.1)
                    self._wait_queue.task_done()
                    
                    match = re.search(pattern, line)
                    if match:
                        elapsed = round(timestamp - start_time, 2)
                        logger.success(f"Pattern matched: {match.groups()}, elapsed: {elapsed}s")
                        return True, match.groups()
                
                except queue.Empty:
                    continue
        
        finally:
            self._wait_event.clear()
            QueueManager.clear_queue(self._wait_queue)
    
    def wait_for_trace(
        self, pattern: str, command: str = "", timeout: float = 10.0
    ) -> Tuple[bool, Optional[List]]:
        """
        Wait for a specific trace pattern.
        
        Args:
            pattern: Regular expression pattern to match
            command: Optional command to send first
            timeout: Maximum time to wait
            
        Returns:
            Tuple of (success, matched_groups)
        """
        success, groups = self._wait_for_pattern(pattern, command, timeout)
        return success, list(groups) if groups else None
    
    @contextmanager
    def monitor_traces(self):
        """Context manager for trace monitoring."""
        self.enable_monitor()
        try:
            yield self
        finally:
            self.disable_monitor()
    
    def enable_monitor(self) -> None:
        """Enable trace monitoring."""
        QueueManager.clear_queue(self._monitor_queue)
        self._monitor_event.set()
        logger.info("SSH trace monitoring enabled")
    
    def disable_monitor(self) -> None:
        """Disable trace monitoring."""
        self._monitor_event.clear()
        logger.info("SSH trace monitoring disabled")
    
    def get_monitored_traces(self) -> List[str]:
        """Get all monitored traces."""
        if not self._monitor_event.is_set():
            logger.warning("SSH trace monitoring is not enabled")
            return []
        
        return QueueManager.extract_lines(self._monitor_queue)
    
    def transfer_file(self, local_path: str, remote_path: str, direction: str = "upload") -> bool:
        """
        Transfer file using SFTP.
        
        Args:
            local_path: Local file path
            remote_path: Remote file path
            direction: "upload" or "download"
            
        Returns:
            True if transfer successful
        """
        if not self.is_connected:
            raise SSHConnectionError("Not connected to SSH")
        
        try:
            with self._ssh_client.open_sftp() as sftp:
                if direction.lower() == "upload":
                    logger.info(f"Uploading {local_path} to {remote_path}")
                    sftp.put(local_path, remote_path)
                elif direction.lower() == "download":
                    logger.info(f"Downloading {remote_path} to {local_path}")
                    sftp.get(remote_path, local_path)
                else:
                    raise ValueError("Direction must be 'upload' or 'download'")
            
            logger.success(f"File transfer completed: {direction}")
            return True
            
        except Exception as e:
            logger.error(f"File transfer failed: {e}")
            raise SSHConnectionError(f"File transfer failed: {e}")


if __name__ == "__main__":
    """
    Examples demonstrating SSHClient usage.
    """
    
    # Example 1: Basic SSH connection
    print("=== Example 1: Basic SSH Usage ===")
    ssh_config = SSHConfig(
        enabled=True,
        hostname="192.168.1.100",
        port=22,
        username="admin",
        password="password123",
        timeout=10.0
    )
    
    with SSHClient() as ssh:
        try:
            ssh.connect(ssh_config)
            print(f"Connection state: {ssh.state}")
            
            # Execute commands
            output = ssh.execute_command("uname -a", wait_time=2.0)
            print(f"System info: {output}")
            
            # Execute with exit code
            output, exit_code = ssh.execute_command_with_exit_code("ls -la /tmp")
            print(f"Command exit code: {exit_code}")
            
        except (SSHConnectionError, SSHAuthenticationError) as e:
            print(f"SSH failed: {e}")
    
    # Example 2: Pattern matching
    print("\n=== Example 2: SSH Pattern Matching ===")
    with SSHClient() as ssh:
        try:
            ssh.connect(ssh_config)
            
            success, groups = ssh.wait_for_trace(
                pattern=r"(\d+) total",
                command="ls -la | wc -l",
                timeout=10.0
            )
            
            if success and groups:
                print(f"Found {groups[0]} total lines")
                
        except Exception as e:
            print(f"Pattern matching error: {e}")
    
    # Example 3: File transfer
    print("\n=== Example 3: File Transfer ===")
    with SSHClient() as ssh:
        try:
            ssh.connect(ssh_config)
            
            # Upload file
            ssh.transfer_file("/local/test.txt", "/remote/test.txt", "upload")
            
            # Download file
            ssh.transfer_file("/local/downloaded.txt", "/remote/config.cfg", "download")
            
        except Exception as e:
            print(f"File transfer error: {e}")
    
    print("\n=== SSH Examples Completed ===")

# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
Device Client Usage Examples

This file demonstrates various usage patterns for the DeviceClient,
which provides general device management and communication capabilities.
"""

import time
from vta.api.factory import APIFactory
from vta.api.base import ClientConfig


def basic_device_operations():
    """Basic device operations example."""
    print("=== Basic Device Operations ===")
    
    # Create device client
    device = APIFactory.create_device_client(
        device_id="192.168.1.100"  # Device IP or identifier
    )
    
    try:
        # Connect to device
        print("Connecting to device...")
        device.connect()
        
        if device.is_connected():
            print("✓ Device connected successfully")
        
        # Get device information
        print("\n--- Device Information ---")
        device_info = device.get_device_info()
        
        print(f"Device ID: {device_info.get('device_id')}")
        print(f"Device Type: {device_info.get('device_type')}")
        print(f"Firmware Version: {device_info.get('firmware_version')}")
        print(f"Hardware Version: {device_info.get('hardware_version')}")
        print(f"Serial Number: {device_info.get('serial_number')}")
        print(f"Manufacturer: {device_info.get('manufacturer')}")
        
        # Get device status
        print("\n--- Device Status ---")
        status = device.get_status()
        
        print(f"Connection Status: {status.get('connected')}")
        print(f"Power State: {status.get('power_state')}")
        print(f"Temperature: {status.get('temperature', 'N/A')}°C")
        print(f"Uptime: {status.get('uptime', 'N/A')}s")
        
        # Execute basic commands
        print("\n--- Basic Commands ---")
        
        # Get device capabilities
        capabilities = device.get_capabilities()
        print(f"Device Capabilities: {capabilities}")
        
        # Ping device
        ping_result = device.ping()
        print(f"Device ping: {'✓' if ping_result else '✗'}")
        
        # Get device time
        device_time = device.get_device_time()
        print(f"Device time: {device_time}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        device.disconnect()


def device_configuration_example():
    """Device configuration management example."""
    print("\n=== Device Configuration Example ===")
    
    device = APIFactory.create_device_client(device_id="test_device_001")
    
    try:
        device.connect()
        
        # Get current configuration
        print("--- Current Configuration ---")
        current_config = device.get_configuration()
        
        print("Current Settings:")
        for key, value in current_config.items():
            print(f"  {key}: {value}")
        
        # Update configuration
        print("\n--- Configuration Update ---")
        new_config = {
            "timeout": 30,
            "retry_count": 5,
            "log_level": "DEBUG",
            "auto_reconnect": True,
            "heartbeat_interval": 10
        }
        
        for key, value in new_config.items():
            update_result = device.set_configuration_parameter(key, value)
            print(f"Set {key} = {value}: {'✓' if update_result else '✗'}")
        
        # Verify updates
        print("\n--- Configuration Verification ---")
        updated_config = device.get_configuration()
        
        for key, expected_value in new_config.items():
            actual_value = updated_config.get(key)
            match = actual_value == expected_value
            print(f"{key}: {actual_value} {'✓' if match else '✗'}")
        
        # Save configuration
        print("\n--- Configuration Persistence ---")
        save_result = device.save_configuration()
        print(f"Configuration saved: {'✓' if save_result else '✗'}")
        
        # Reset to defaults
        print("\n--- Reset to Defaults ---")
        reset_result = device.reset_configuration()
        print(f"Configuration reset: {'✓' if reset_result else '✗'}")
        
        # Verify reset
        default_config = device.get_configuration()
        print("Configuration after reset:")
        for key, value in default_config.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        device.disconnect()


def device_file_management():
    """Device file management example."""
    print("\n=== Device File Management ===")
    
    device = APIFactory.create_device_client(device_id="file_device")
    
    try:
        device.connect()
        
        # List files and directories
        print("--- File System Exploration ---")
        
        # List root directory
        root_files = device.list_files("/")
        print("Root directory contents:")
        for file_info in root_files[:10]:  # Show first 10 entries
            file_type = "DIR" if file_info.get('is_directory') else "FILE"
            size = file_info.get('size', 0)
            print(f"  [{file_type}] {file_info.get('name')} ({size} bytes)")
        
        # Create test directory
        print("\n--- Directory Operations ---")
        test_dir = "/tmp/vta_test"
        create_result = device.create_directory(test_dir)
        print(f"Create directory {test_dir}: {'✓' if create_result else '✗'}")
        
        # Upload file to device
        print("\n--- File Upload ---")
        
        # Create local test file
        local_file = "device_test.txt"
        test_content = "This is a test file for device file management."
        
        with open(local_file, 'w') as f:
            f.write(test_content)
        
        remote_file = f"{test_dir}/uploaded_file.txt"
        upload_result = device.upload_file(local_file, remote_file)
        print(f"Upload {local_file} -> {remote_file}: {'✓' if upload_result else '✗'}")
        
        # Verify file exists
        file_exists = device.file_exists(remote_file)
        print(f"File exists on device: {'✓' if file_exists else '✗'}")
        
        # Get file info
        file_info = device.get_file_info(remote_file)
        if file_info:
            print(f"Remote file info:")
            print(f"  Size: {file_info.get('size')} bytes")
            print(f"  Modified: {file_info.get('modified_time')}")
            print(f"  Permissions: {file_info.get('permissions')}")
        
        # Download file from device
        print("\n--- File Download ---")
        downloaded_file = "downloaded_device_test.txt"
        download_result = device.download_file(remote_file, downloaded_file)
        print(f"Download {remote_file} -> {downloaded_file}: {'✓' if download_result else '✗'}")
        
        # Verify download content
        if download_result:
            with open(downloaded_file, 'r') as f:
                downloaded_content = f.read()
                content_match = downloaded_content == test_content
                print(f"Content verification: {'✓' if content_match else '✗'}")
        
        # File operations
        print("\n--- File Operations ---")
        
        # Copy file
        copied_file = f"{test_dir}/copied_file.txt"
        copy_result = device.copy_file(remote_file, copied_file)
        print(f"Copy file: {'✓' if copy_result else '✗'}")
        
        # Move file
        moved_file = f"{test_dir}/moved_file.txt"
        move_result = device.move_file(copied_file, moved_file)
        print(f"Move file: {'✓' if move_result else '✗'}")
        
        # Delete files
        print("\n--- Cleanup ---")
        
        files_to_delete = [remote_file, moved_file]
        for file_path in files_to_delete:
            delete_result = device.delete_file(file_path)
            print(f"Delete {file_path}: {'✓' if delete_result else '✗'}")
        
        # Remove directory
        remove_dir_result = device.remove_directory(test_dir)
        print(f"Remove directory {test_dir}: {'✓' if remove_dir_result else '✗'}")
        
        # Cleanup local files
        import os
        try:
            os.remove(local_file)
            os.remove(downloaded_file)
        except Exception:
            pass
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        device.disconnect()


def device_monitoring_example():
    """Device monitoring and health check example."""
    print("\n=== Device Monitoring Example ===")
    
    device = APIFactory.create_device_client(device_id="monitor_device")
    
    try:
        device.connect()
        
        # Start monitoring
        print("--- Device Health Monitoring ---")
        
        # Get baseline metrics
        baseline_metrics = device.get_performance_metrics()
        print("Baseline Metrics:")
        print(f"  CPU Usage: {baseline_metrics.get('cpu_usage', 0)}%")
        print(f"  Memory Usage: {baseline_metrics.get('memory_usage', 0)}%")
        print(f"  Disk Usage: {baseline_metrics.get('disk_usage', 0)}%")
        print(f"  Network I/O: {baseline_metrics.get('network_io', {})}")
        
        # Monitor for a period
        print("\n--- Continuous Monitoring (30 seconds) ---")
        start_time = time.time()
        monitoring_data = []
        
        while time.time() - start_time < 30:
            current_metrics = device.get_performance_metrics()
            current_time = time.time() - start_time
            
            monitoring_data.append({
                "timestamp": current_time,
                "cpu_usage": current_metrics.get('cpu_usage', 0),
                "memory_usage": current_metrics.get('memory_usage', 0),
                "temperature": current_metrics.get('temperature', 0)
            })
            
            print(f"Time: {current_time:.1f}s - "
                  f"CPU: {current_metrics.get('cpu_usage', 0)}%, "
                  f"Memory: {current_metrics.get('memory_usage', 0)}%, "
                  f"Temp: {current_metrics.get('temperature', 0)}°C")
            
            # Check for alerts
            alerts = device.get_health_alerts()
            if alerts:
                print(f"  ⚠️  Alerts: {len(alerts)}")
                for alert in alerts:
                    print(f"    - {alert.get('type')}: {alert.get('message')}")
            
            time.sleep(3)
        
        # Analyze monitoring data
        print("\n--- Monitoring Analysis ---")
        
        if monitoring_data:
            avg_cpu = sum(d['cpu_usage'] for d in monitoring_data) / len(monitoring_data)
            max_cpu = max(d['cpu_usage'] for d in monitoring_data)
            avg_memory = sum(d['memory_usage'] for d in monitoring_data) / len(monitoring_data)
            max_temp = max(d['temperature'] for d in monitoring_data)
            
            print(f"Average CPU Usage: {avg_cpu:.1f}%")
            print(f"Peak CPU Usage: {max_cpu:.1f}%")
            print(f"Average Memory Usage: {avg_memory:.1f}%")
            print(f"Peak Temperature: {max_temp:.1f}°C")
            
            # Health assessment
            health_score = device.calculate_health_score(monitoring_data)
            print(f"Device Health Score: {health_score}/100")
            
            if health_score < 70:
                print("⚠️  Device health is below optimal threshold")
            elif health_score > 90:
                print("✅ Device health is excellent")
            else:
                print("ℹ️  Device health is acceptable")
        
        # Generate monitoring report
        print("\n--- Monitoring Report ---")
        report_data = {
            "monitoring_duration": 30,
            "data_points": len(monitoring_data),
            "metrics": monitoring_data,
            "summary": {
                "avg_cpu": avg_cpu,
                "max_cpu": max_cpu,
                "avg_memory": avg_memory,
                "max_temp": max_temp,
                "health_score": health_score
            }
        }
        
        report_result = device.generate_monitoring_report(report_data)
        print(f"Monitoring report generated: {'✓' if report_result else '✗'}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        device.disconnect()


def device_automation_example():
    """Device automation and scripting example."""
    print("\n=== Device Automation Example ===")
    
    device = APIFactory.create_device_client(device_id="automation_device")
    
    try:
        device.connect()
        
        # Define automation script
        print("--- Automation Script Execution ---")
        
        automation_script = """
        # Device automation script
        print("Starting device automation...")
        
        # Get device status
        status = get_device_status()
        print(f"Initial status: {status}")
        
        # Set device parameters
        set_parameter("operation_mode", "test")
        set_parameter("data_rate", 1000)
        set_parameter("timeout", 30)
        
        # Execute test sequence
        for i in range(5):
            print(f"Test iteration {i+1}")
            result = execute_test_command(f"test_cmd_{i}")
            if not result:
                print(f"Test {i+1} failed")
                break
            wait(2)
        
        print("Automation script completed")
        """
        
        # Execute automation script
        script_result = device.execute_script(automation_script, language="python")
        print(f"Automation script execution: {'✓' if script_result else '✗'}")
        
        if script_result:
            script_output = device.get_script_output()
            print("Script Output:")
            for line in script_output.split('\n')[-10:]:  # Show last 10 lines
                if line.strip():
                    print(f"  {line}")
        
        # Scheduled operations
        print("\n--- Scheduled Operations ---")
        
        # Schedule periodic health check
        schedule_result = device.schedule_operation(
            operation="health_check",
            interval=60,  # Every minute
            duration=300  # For 5 minutes
        )
        print(f"Health check scheduled: {'✓' if schedule_result else '✗'}")
        
        # Schedule configuration backup
        backup_schedule = device.schedule_operation(
            operation="backup_config",
            schedule="0 2 * * *",  # Daily at 2 AM
            enabled=True
        )
        print(f"Config backup scheduled: {'✓' if backup_schedule else '✗'}")
        
        # List scheduled operations
        scheduled_ops = device.get_scheduled_operations()
        print(f"Active scheduled operations: {len(scheduled_ops)}")
        for op in scheduled_ops:
            print(f"  - {op.get('operation')}: {op.get('schedule')}")
        
        # Batch operations
        print("\n--- Batch Operations ---")
        
        batch_commands = [
            {"command": "get_status", "params": {}},
            {"command": "set_parameter", "params": {"key": "mode", "value": "auto"}},
            {"command": "execute_test", "params": {"test_id": "batch_test_1"}},
            {"command": "get_results", "params": {"test_id": "batch_test_1"}},
            {"command": "cleanup", "params": {}}
        ]
        
        batch_result = device.execute_batch_commands(batch_commands)
        print(f"Batch execution: {'✓' if batch_result else '✗'}")
        
        if batch_result:
            batch_results = device.get_batch_results()
            print("Batch Results:")
            for i, result in enumerate(batch_results):
                cmd = batch_commands[i]['command']
                status = result.get('status', 'unknown')
                print(f"  {cmd}: {status}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        device.disconnect()


def multi_device_coordination():
    """Multi-device coordination example."""
    print("\n=== Multi-Device Coordination ===")
    
    # Define multiple devices
    device_configs = [
        {"device_id": "device_001", "role": "primary"},
        {"device_id": "device_002", "role": "secondary"},
        {"device_id": "device_003", "role": "monitor"}
    ]
    
    devices = []
    
    try:
        # Connect to all devices
        print("--- Device Coordination Setup ---")
        
        for config in device_configs:
            try:
                device = APIFactory.create_device_client(device_id=config["device_id"])
                device.connect()
                
                if device.is_connected():
                    devices.append({"client": device, "config": config})
                    print(f"✓ Connected to {config['device_id']} ({config['role']})")
                else:
                    print(f"✗ Failed to connect to {config['device_id']}")
            except Exception as e:
                print(f"✗ Error connecting to {config['device_id']}: {e}")
        
        if len(devices) < 2:
            print("Need at least 2 devices for coordination example")
            return
        
        # Synchronized operations
        print("\n--- Synchronized Operations ---")
        
        # Synchronize device clocks
        print("Synchronizing device clocks...")
        reference_time = time.time()
        
        for device_info in devices:
            device = device_info["client"]
            sync_result = device.synchronize_time(reference_time)
            device_id = device_info["config"]["device_id"]
            print(f"  {device_id}: {'✓' if sync_result else '✗'}")
        
        # Coordinated test execution
        print("\n--- Coordinated Test Execution ---")
        
        # Start test on all devices simultaneously
        test_config = {
            "test_name": "coordinated_test",
            "duration": 30,
            "sync_start": True
        }
        
        start_time = time.time() + 5  # Start in 5 seconds
        
        for device_info in devices:
            device = device_info["client"]
            role = device_info["config"]["role"]
            
            # Customize test for each role
            role_config = dict(test_config)
            role_config["role"] = role
            
            schedule_result = device.schedule_test(role_config, start_time)
            print(f"  {role} test scheduled: {'✓' if schedule_result else '✗'}")
        
        # Wait for tests to start
        time.sleep(6)
        
        # Monitor coordinated execution
        print("\n--- Execution Monitoring ---")
        
        for i in range(10):  # Monitor for 10 intervals
            print(f"\nMonitoring interval {i+1}:")
            
            all_running = True
            for device_info in devices:
                device = device_info["client"]
                role = device_info["config"]["role"]
                
                test_status = device.get_test_status()
                status = test_status.get("status", "unknown")
                progress = test_status.get("progress", 0)
                
                print(f"  {role}: {status} ({progress}%)")
                
                if status not in ["running", "active"]:
                    all_running = False
            
            if not all_running:
                break
            
            time.sleep(3)
        
        # Collect results from all devices
        print("\n--- Results Collection ---")
        
        coordination_results = {}
        for device_info in devices:
            device = device_info["client"]
            role = device_info["config"]["role"]
            
            test_results = device.get_test_results()
            coordination_results[role] = test_results
            
            print(f"{role} Results:")
            print(f"  Status: {test_results.get('status', 'unknown')}")
            print(f"  Duration: {test_results.get('duration', 0)}s")
            print(f"  Data Points: {test_results.get('data_points', 0)}")
        
        # Generate coordination report
        print("\n--- Coordination Report ---")
        
        report_data = {
            "test_type": "coordinated_multi_device",
            "devices": len(devices),
            "results": coordination_results,
            "synchronization": "successful"
        }
        
        # Use primary device to generate report
        if devices:
            primary_device = devices[0]["client"]
            report_result = primary_device.generate_coordination_report(report_data)
            print(f"Coordination report: {'✓' if report_result else '✗'}")
        
    except Exception as e:
        print(f"Error in coordination: {e}")
    finally:
        # Cleanup all device connections
        for device_info in devices:
            try:
                device = device_info["client"]
                device_id = device_info["config"]["device_id"]
                device.disconnect()
                print(f"Disconnected from {device_id}")
            except Exception:
                pass


if __name__ == "__main__":
    print("VTA Device Client Examples")
    print("==========================")
    
    # Run all examples
    try:
        basic_device_operations()
        device_configuration_example()
        device_file_management()
        device_monitoring_example()
        device_automation_example()
        multi_device_coordination()
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    
    print("\nAll device examples completed!")

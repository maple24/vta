# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
CANoe Client Usage Examples

This file demonstrates various usage patterns for the CANoeClient,
which provides integration with Vector CANoe for CAN bus testing and simulation.
"""

import time
from vta.api.factory import APIFactory
from vta.api.base import ClientConfig


def basic_canoe_operations():
    """Basic CANoe operations example."""
    print("=== Basic CANoe Operations ===")
    
    # Create CANoe client
    canoe = APIFactory.create_canoe_client()
    
    try:
        # Connect to CANoe
        print("Connecting to CANoe...")
        canoe.connect()
        
        if canoe.is_connected():
            print("✓ CANoe connected successfully")
        
        # Get CANoe version and status
        print("\n--- CANoe Information ---")
        version = canoe.get_version()
        print(f"CANoe Version: {version}")
        
        status = canoe.get_status()
        print(f"CANoe Status: {status}")
        
        # Load configuration
        print("\n--- Configuration Management ---")
        config_path = "C:/CANoe_Configs/TestConfig.cfg"
        load_result = canoe.load_configuration(config_path)
        print(f"Configuration loaded: {'✓' if load_result else '✗'}")
        
        # Start measurement
        print("\n--- Measurement Control ---")
        start_result = canoe.start_measurement()
        print(f"Measurement started: {'✓' if start_result else '✗'}")
        
        # Wait for measurement to be running
        time.sleep(2)
        
        # Check measurement state
        measurement_state = canoe.get_measurement_state()
        print(f"Measurement state: {measurement_state}")
        
        # Stop measurement
        stop_result = canoe.stop_measurement()
        print(f"Measurement stopped: {'✓' if stop_result else '✗'}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        canoe.disconnect()


def can_message_handling():
    """CAN message sending and receiving example."""
    print("\n=== CAN Message Handling ===")
    
    canoe = APIFactory.create_canoe_client()
    
    try:
        canoe.connect()
        
        # Load configuration and start measurement
        config_path = "C:/CANoe_Configs/CANTestConfig.cfg"
        canoe.load_configuration(config_path)
        canoe.start_measurement()
        
        # Wait for system to be ready
        time.sleep(3)
        
        # Send CAN messages
        print("--- Sending CAN Messages ---")
        
        # Send standard CAN message
        message_data = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
        send_result = canoe.send_can_message(
            can_id=0x123,
            data=message_data,
            channel=1
        )
        print(f"CAN message sent (ID: 0x123): {'✓' if send_result else '✗'}")
        
        # Send multiple messages
        messages = [
            {"id": 0x200, "data": [0x10, 0x20, 0x30, 0x40]},
            {"id": 0x201, "data": [0x50, 0x60, 0x70, 0x80]},
            {"id": 0x202, "data": [0x90, 0xA0, 0xB0, 0xC0]}
        ]
        
        for msg in messages:
            canoe.send_can_message(msg["id"], msg["data"], channel=1)
            print(f"Sent message ID: 0x{msg['id']:03X}")
            time.sleep(0.1)
        
        # Receive CAN messages
        print("\n--- Receiving CAN Messages ---")
        
        # Set up message filter
        filter_ids = [0x300, 0x301, 0x302]
        canoe.set_can_filter(filter_ids, channel=1)
        print(f"CAN filter set for IDs: {[hex(id) for id in filter_ids]}")
        
        # Start reception
        canoe.start_can_reception()
        
        # Simulate some activity and receive messages
        print("Receiving messages for 10 seconds...")
        start_time = time.time()
        
        while time.time() - start_time < 10:
            received_messages = canoe.get_received_messages(count=10)
            
            if received_messages:
                for msg in received_messages[-3:]:  # Show last 3 messages
                    print(f"  Received ID: 0x{msg.get('id', 0):03X}, "
                          f"Data: {msg.get('data', [])}")
            
            time.sleep(1)
        
        # Stop reception
        canoe.stop_can_reception()
        
        # Get reception statistics
        stats = canoe.get_reception_statistics()
        print(f"\nReception Statistics:")
        print(f"  Total Messages: {stats.get('total_messages', 0)}")
        print(f"  Filtered Messages: {stats.get('filtered_messages', 0)}")
        print(f"  Error Frames: {stats.get('error_frames', 0)}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        canoe.stop_measurement()
        canoe.disconnect()


def test_automation_example():
    """Test automation with CANoe example."""
    print("\n=== Test Automation Example ===")
    
    canoe = APIFactory.create_canoe_client()
    
    try:
        canoe.connect()
        
        # Load test configuration
        test_config = "C:/CANoe_Configs/AutomationTest.cfg"
        canoe.load_configuration(test_config)
        
        # Get available test modules
        print("--- Available Test Modules ---")
        test_modules = canoe.get_test_modules()
        
        for module in test_modules:
            print(f"  Module: {module.get('name')}")
            print(f"    Description: {module.get('description')}")
            print(f"    Test Cases: {len(module.get('test_cases', []))}")
        
        # Execute test sequence
        print("\n--- Test Execution ---")
        
        if test_modules:
            module_name = test_modules[0]['name']
            print(f"Executing test module: {module_name}")
            
            # Start test execution
            test_result = canoe.execute_test_module(module_name)
            print(f"Test execution started: {'✓' if test_result else '✗'}")
            
            # Monitor test progress
            print("\nMonitoring test progress...")
            
            while True:
                test_status = canoe.get_test_status()
                print(f"  Test Status: {test_status.get('state', 'unknown')}")
                print(f"  Progress: {test_status.get('progress', 0)}%")
                print(f"  Current Test: {test_status.get('current_test', 'N/A')}")
                
                if test_status.get('state') in ['completed', 'failed', 'aborted']:
                    break
                
                time.sleep(2)
            
            # Get test results
            print("\n--- Test Results ---")
            results = canoe.get_test_results()
            
            print(f"Overall Result: {results.get('overall_result', 'unknown')}")
            print(f"Tests Executed: {results.get('tests_executed', 0)}")
            print(f"Tests Passed: {results.get('tests_passed', 0)}")
            print(f"Tests Failed: {results.get('tests_failed', 0)}")
            print(f"Execution Time: {results.get('execution_time', 0)}s")
            
            # Show failed tests
            failed_tests = results.get('failed_tests', [])
            if failed_tests:
                print("\nFailed Tests:")
                for test in failed_tests:
                    print(f"  - {test.get('name')}: {test.get('reason')}")
        
        # Generate test report
        print("\n--- Test Report Generation ---")
        report_path = "C:/Temp/canoe_test_report.html"
        report_result = canoe.generate_test_report(report_path, format="html")
        print(f"Test report generated: {'✓' if report_result else '✗'}")
        
        if report_result:
            print(f"Report saved to: {report_path}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        canoe.disconnect()


def signal_monitoring_example():
    """Signal monitoring and analysis example."""
    print("\n=== Signal Monitoring Example ===")
    
    canoe = APIFactory.create_canoe_client()
    
    try:
        canoe.connect()
        
        # Load signal database configuration
        config_path = "C:/CANoe_Configs/SignalMonitor.cfg"
        canoe.load_configuration(config_path)
        canoe.start_measurement()
        
        # Define signals to monitor
        print("--- Signal Definition ---")
        signals_to_monitor = [
            {"name": "EngineSpeed", "channel": 1, "message_id": 0x180},
            {"name": "VehicleSpeed", "channel": 1, "message_id": 0x181},
            {"name": "ThrottlePosition", "channel": 1, "message_id": 0x182},
            {"name": "BrakeStatus", "channel": 1, "message_id": 0x183}
        ]
        
        # Set up signal monitoring
        for signal in signals_to_monitor:
            monitor_result = canoe.add_signal_monitor(
                signal["name"],
                signal["message_id"],
                signal["channel"]
            )
            print(f"Monitoring {signal['name']}: {'✓' if monitor_result else '✗'}")
        
        # Start signal monitoring
        canoe.start_signal_monitoring()
        
        # Monitor signals for a period
        print("\n--- Signal Monitoring (30 seconds) ---")
        start_time = time.time()
        
        while time.time() - start_time < 30:
            signal_values = canoe.get_signal_values()
            
            print(f"\nTime: {time.time() - start_time:.1f}s")
            for signal_name, value in signal_values.items():
                print(f"  {signal_name}: {value}")
            
            time.sleep(3)
        
        # Stop monitoring and get statistics
        canoe.stop_signal_monitoring()
        
        print("\n--- Signal Statistics ---")
        for signal in signals_to_monitor:
            stats = canoe.get_signal_statistics(signal["name"])
            print(f"{signal['name']}:")
            print(f"  Min: {stats.get('min', 0)}")
            print(f"  Max: {stats.get('max', 0)}")
            print(f"  Average: {stats.get('average', 0)}")
            print(f"  Sample Count: {stats.get('sample_count', 0)}")
        
        # Export signal data
        print("\n--- Signal Data Export ---")
        export_path = "C:/Temp/signal_data.csv"
        export_result = canoe.export_signal_data(export_path, format="csv")
        print(f"Signal data exported: {'✓' if export_result else '✗'}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        canoe.stop_measurement()
        canoe.disconnect()


def diagnosis_example():
    """Diagnostic communication example."""
    print("\n=== Diagnosis Example ===")
    
    canoe = APIFactory.create_canoe_client()
    
    try:
        canoe.connect()
        
        # Load diagnostic configuration
        diag_config = "C:/CANoe_Configs/DiagnosticTest.cfg"
        canoe.load_configuration(diag_config)
        canoe.start_measurement()
        
        # Connect to ECU
        print("--- ECU Connection ---")
        ecu_address = 0x7E0  # Example ECU address
        connect_result = canoe.connect_to_ecu(ecu_address)
        print(f"ECU connection (0x{ecu_address:03X}): {'✓' if connect_result else '✗'}")
        
        if connect_result:
            # Read ECU information
            print("\n--- ECU Information ---")
            
            # Read VIN
            vin_result = canoe.read_data_by_identifier(0xF190)  # VIN DID
            if vin_result:
                print(f"VIN: {vin_result.get('data', 'Unknown')}")
            
            # Read software version
            sw_version = canoe.read_data_by_identifier(0xF195)  # SW version DID
            if sw_version:
                print(f"Software Version: {sw_version.get('data', 'Unknown')}")
            
            # Read hardware version
            hw_version = canoe.read_data_by_identifier(0xF193)  # HW version DID
            if hw_version:
                print(f"Hardware Version: {hw_version.get('data', 'Unknown')}")
            
            # Diagnostic session control
            print("\n--- Diagnostic Sessions ---")
            
            # Extended diagnostic session
            session_result = canoe.diagnostic_session_control(0x03)  # Extended session
            print(f"Extended session: {'✓' if session_result else '✗'}")
            
            # Security access
            print("\n--- Security Access ---")
            security_result = canoe.security_access(level=0x01)
            print(f"Security access (Level 1): {'✓' if security_result else '✗'}")
            
            # Read diagnostic trouble codes
            print("\n--- Diagnostic Trouble Codes ---")
            dtc_result = canoe.read_dtc_information()
            
            if dtc_result:
                dtcs = dtc_result.get('dtcs', [])
                print(f"Found {len(dtcs)} DTCs:")
                for dtc in dtcs:
                    print(f"  DTC: {dtc.get('code')} - {dtc.get('description')}")
                    print(f"    Status: {dtc.get('status')}")
            else:
                print("No DTCs found")
            
            # Clear DTCs
            if dtc_result and dtc_result.get('dtcs'):
                clear_result = canoe.clear_dtc_information()
                print(f"DTCs cleared: {'✓' if clear_result else '✗'}")
            
            # Routine control
            print("\n--- Routine Control ---")
            routine_id = 0x1234  # Example routine
            routine_result = canoe.routine_control(routine_id, control_type=0x01)  # Start
            print(f"Routine 0x{routine_id:04X} started: {'✓' if routine_result else '✗'}")
            
            # Disconnect from ECU
            disconnect_result = canoe.disconnect_from_ecu(ecu_address)
            print(f"ECU disconnection: {'✓' if disconnect_result else '✗'}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        canoe.stop_measurement()
        canoe.disconnect()


def advanced_canoe_automation():
    """Advanced CANoe automation example."""
    print("\n=== Advanced CANoe Automation ===")
    
    # Custom configuration for advanced features
    config = ClientConfig(
        timeout=120.0,  # Longer timeout for complex operations
        extra_config={
            "auto_start": True,
            "logging_enabled": True,
            "log_level": "DEBUG"
        }
    )
    
    canoe = APIFactory.create_client(APIFactory.ClientType.CANOE_CLIENT, config)
    
    try:
        canoe.connect()
        
        # Batch configuration loading
        print("--- Batch Configuration ---")
        configurations = [
            "C:/CANoe_Configs/Config1.cfg",
            "C:/CANoe_Configs/Config2.cfg",
            "C:/CANoe_Configs/Config3.cfg"
        ]
        
        for i, config_path in enumerate(configurations, 1):
            print(f"Loading configuration {i}...")
            load_result = canoe.load_configuration(config_path)
            
            if load_result:
                # Run quick validation
                canoe.start_measurement()
                time.sleep(5)  # Let it run briefly
                
                # Check for errors
                errors = canoe.get_measurement_errors()
                if errors:
                    print(f"  Configuration {i}: {len(errors)} errors found")
                    for error in errors[:3]:  # Show first 3 errors
                        print(f"    - {error}")
                else:
                    print(f"  Configuration {i}: ✓ No errors")
                
                canoe.stop_measurement()
            else:
                print(f"  Configuration {i}: ✗ Failed to load")
            
            time.sleep(1)
        
        # Performance monitoring
        print("\n--- Performance Monitoring ---")
        
        # Load performance test configuration
        perf_config = "C:/CANoe_Configs/PerformanceTest.cfg"
        canoe.load_configuration(perf_config)
        canoe.start_measurement()
        
        # Monitor system performance
        start_time = time.time()
        performance_data = []
        
        for i in range(10):  # Monitor for 10 intervals
            perf_metrics = canoe.get_performance_metrics()
            
            performance_data.append({
                "timestamp": time.time() - start_time,
                "cpu_usage": perf_metrics.get("cpu_usage", 0),
                "memory_usage": perf_metrics.get("memory_usage", 0),
                "message_rate": perf_metrics.get("message_rate", 0)
            })
            
            print(f"  Interval {i+1}: CPU: {perf_metrics.get('cpu_usage', 0)}%, "
                  f"Memory: {perf_metrics.get('memory_usage', 0)}MB, "
                  f"Msg Rate: {perf_metrics.get('message_rate', 0)}/s")
            
            time.sleep(2)
        
        # Analyze performance data
        avg_cpu = sum(d["cpu_usage"] for d in performance_data) / len(performance_data)
        avg_memory = sum(d["memory_usage"] for d in performance_data) / len(performance_data)
        max_msg_rate = max(d["message_rate"] for d in performance_data)
        
        print(f"\nPerformance Summary:")
        print(f"  Average CPU: {avg_cpu:.1f}%")
        print(f"  Average Memory: {avg_memory:.1f}MB")
        print(f"  Peak Message Rate: {max_msg_rate}/s")
        
        # Automated reporting
        print("\n--- Automated Reporting ---")
        
        report_data = {
            "test_timestamp": time.time(),
            "configurations_tested": len(configurations),
            "performance_metrics": {
                "avg_cpu": avg_cpu,
                "avg_memory": avg_memory,
                "peak_message_rate": max_msg_rate
            }
        }
        
        report_result = canoe.generate_custom_report(report_data, 
                                                   template="automation_report.xml")
        print(f"Custom report generated: {'✓' if report_result else '✗'}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        canoe.stop_measurement()
        canoe.disconnect()


if __name__ == "__main__":
    print("VTA CANoe Client Examples")
    print("=========================")
    
    # Run all examples
    try:
        basic_canoe_operations()
        can_message_handling()
        test_automation_example()
        signal_monitoring_example()
        diagnosis_example()
        advanced_canoe_automation()
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    
    print("\nAll CANoe examples completed!")

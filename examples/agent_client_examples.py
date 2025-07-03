# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
Agent Client Usage Examples

This file demonstrates various usage patterns for the AgentClient,
which provides communication with VTA agent services for test automation.
"""

import time
from vta.api.factory import APIFactory
from vta.api.base import ClientConfig


def basic_agent_operations():
    """Basic agent operations example."""
    print("=== Basic Agent Operations ===")
    
    # Create agent client with default settings
    agent = APIFactory.create_agent_client(
        host="localhost",
        port=6666  # Default VTA agent port
    )
    
    try:
        # Connect to agent
        print("Connecting to VTA agent...")
        agent.connect()
        
        if agent.is_connected():
            print("✓ Agent connected successfully")
        
        # Get agent information
        print("\n--- Agent Information ---")
        agent_info = agent.get_agent_info()
        print(f"Agent Version: {agent_info.get('version', 'Unknown')}")
        print(f"Agent Status: {agent_info.get('status', 'Unknown')}")
        print(f"Uptime: {agent_info.get('uptime', 'Unknown')}")
        
        # Execute simple command
        print("\n--- Command Execution ---")
        result = agent.execute_command("get_status")
        print(f"Status Command Result: {result}")
        
        # Get available services
        print("\n--- Available Services ---")
        services = agent.get_services()
        print(f"Available services: {services}")
        
        # Ping agent
        print("\n--- Agent Ping ---")
        ping_result = agent.ping()
        print(f"Ping successful: {ping_result}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        agent.disconnect()


def test_execution_example():
    """Test execution through agent example."""
    print("\n=== Test Execution Example ===")
    
    agent = APIFactory.create_agent_client()
    
    try:
        agent.connect()
        
        # Submit test job
        print("--- Test Job Submission ---")
        test_config = {
            "test_suite": "smoke_tests",
            "environment": "staging",
            "parameters": {
                "timeout": 300,
                "retry_count": 3,
                "device_type": "android"
            }
        }
        
        job_id = agent.submit_test_job(test_config)
        print(f"Test job submitted with ID: {job_id}")
        
        # Monitor test execution
        print("\n--- Test Monitoring ---")
        start_time = time.time()
        timeout = 60  # Monitor for 1 minute
        
        while time.time() - start_time < timeout:
            status = agent.get_job_status(job_id)
            print(f"Job {job_id} status: {status.get('state', 'unknown')}")
            
            if status.get('state') in ['completed', 'failed', 'cancelled']:
                break
            
            time.sleep(5)
        
        # Get test results
        print("\n--- Test Results ---")
        results = agent.get_job_results(job_id)
        print(f"Test Results:")
        print(f"  Status: {results.get('status', 'unknown')}")
        print(f"  Tests Run: {results.get('tests_run', 0)}")
        print(f"  Tests Passed: {results.get('tests_passed', 0)}")
        print(f"  Tests Failed: {results.get('tests_failed', 0)}")
        print(f"  Duration: {results.get('duration', 0)}s")
        
        # Get logs
        print("\n--- Test Logs ---")
        logs = agent.get_job_logs(job_id, lines=20)
        for log_line in logs[-5:]:  # Show last 5 lines
            print(f"  {log_line}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        agent.disconnect()


def device_management_example():
    """Device management through agent example."""
    print("\n=== Device Management Example ===")
    
    agent = APIFactory.create_agent_client()
    
    try:
        agent.connect()
        
        # Get available devices
        print("--- Available Devices ---")
        devices = agent.get_devices()
        print(f"Found {len(devices)} devices:")
        
        for device in devices:
            print(f"  Device ID: {device.get('id')}")
            print(f"    Type: {device.get('type')}")
            print(f"    Status: {device.get('status')}")
            print(f"    Platform: {device.get('platform')}")
        
        # Reserve device for testing
        if devices:
            device_id = devices[0]['id']
            print(f"\n--- Device Reservation ---")
            print(f"Reserving device: {device_id}")
            
            reservation = agent.reserve_device(device_id, duration=300)  # 5 minutes
            print(f"Reservation ID: {reservation.get('reservation_id')}")
            print(f"Reserved until: {reservation.get('expires_at')}")
            
            # Perform device operations
            print("\n--- Device Operations ---")
            
            # Install application
            app_info = {
                "package": "com.example.testapp",
                "version": "1.0.0",
                "apk_path": "/path/to/app.apk"
            }
            install_result = agent.install_app(device_id, app_info)
            print(f"App installation: {'✓' if install_result else '✗'}")
            
            # Run device command
            cmd_result = agent.execute_device_command(device_id, "get_device_info")
            print(f"Device info: {cmd_result}")
            
            # Release device
            print("\n--- Device Release ---")
            release_result = agent.release_device(device_id)
            print(f"Device released: {'✓' if release_result else '✗'}")
        
        # Get device logs
        print("\n--- Device Logs ---")
        if devices:
            device_logs = agent.get_device_logs(devices[0]['id'], lines=10)
            for log_line in device_logs[-3:]:  # Show last 3 lines
                print(f"  {log_line}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        agent.disconnect()


def resource_monitoring_example():
    """Resource monitoring through agent example."""
    print("\n=== Resource Monitoring Example ===")
    
    agent = APIFactory.create_agent_client()
    
    try:
        agent.connect()
        
        # Monitor system resources
        print("--- System Resources ---")
        resources = agent.get_system_resources()
        
        print(f"CPU Usage: {resources.get('cpu_percent', 0)}%")
        print(f"Memory Usage: {resources.get('memory_percent', 0)}%")
        print(f"Disk Usage: {resources.get('disk_percent', 0)}%")
        print(f"Network I/O: {resources.get('network_io', {})}")
        
        # Monitor agent performance
        print("\n--- Agent Performance ---")
        performance = agent.get_performance_metrics()
        
        print(f"Active Jobs: {performance.get('active_jobs', 0)}")
        print(f"Queued Jobs: {performance.get('queued_jobs', 0)}")
        print(f"Completed Jobs: {performance.get('completed_jobs', 0)}")
        print(f"Average Job Duration: {performance.get('avg_duration', 0)}s")
        
        # Monitor for a period
        print("\n--- Resource Monitoring (30 seconds) ---")
        start_time = time.time()
        
        while time.time() - start_time < 30:
            current_resources = agent.get_system_resources()
            cpu = current_resources.get('cpu_percent', 0)
            memory = current_resources.get('memory_percent', 0)
            
            print(f"Time: {time.time() - start_time:.1f}s - "
                  f"CPU: {cpu}%, Memory: {memory}%")
            
            time.sleep(5)
        
        # Get resource history
        print("\n--- Resource History ---")
        history = agent.get_resource_history(duration=300)  # Last 5 minutes
        
        print(f"Resource samples: {len(history)}")
        if history:
            latest = history[-1]
            print(f"Latest sample: CPU: {latest.get('cpu')}%, "
                  f"Memory: {latest.get('memory')}%")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        agent.disconnect()


def configuration_management_example():
    """Configuration management through agent example."""
    print("\n=== Configuration Management Example ===")
    
    agent = APIFactory.create_agent_client()
    
    try:
        agent.connect()
        
        # Get current configuration
        print("--- Current Configuration ---")
        config = agent.get_configuration()
        
        print(f"Agent Name: {config.get('agent_name')}")
        print(f"Max Concurrent Jobs: {config.get('max_jobs')}")
        print(f"Device Pool Size: {config.get('device_pool_size')}")
        print(f"Log Level: {config.get('log_level')}")
        
        # Update configuration
        print("\n--- Configuration Update ---")
        new_config = {
            "max_jobs": 5,
            "log_level": "DEBUG",
            "timeout_default": 300
        }
        
        update_result = agent.update_configuration(new_config)
        print(f"Configuration updated: {'✓' if update_result else '✗'}")
        
        # Verify update
        updated_config = agent.get_configuration()
        print(f"Updated Max Jobs: {updated_config.get('max_jobs')}")
        print(f"Updated Log Level: {updated_config.get('log_level')}")
        
        # Get configuration schema
        print("\n--- Configuration Schema ---")
        schema = agent.get_configuration_schema()
        print("Available configuration options:")
        for option in schema.get('options', []):
            print(f"  {option.get('name')}: {option.get('description')}")
        
        # Validate configuration
        print("\n--- Configuration Validation ---")
        test_config = {
            "max_jobs": 10,
            "log_level": "INFO",
            "invalid_option": "should_fail"
        }
        
        validation = agent.validate_configuration(test_config)
        print(f"Validation result: {'✓' if validation.get('valid') else '✗'}")
        if not validation.get('valid'):
            print(f"Errors: {validation.get('errors', [])}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        agent.disconnect()


def advanced_agent_operations():
    """Advanced agent operations example."""
    print("\n=== Advanced Agent Operations Example ===")
    
    # Create agent client with custom configuration
    config = ClientConfig(
        host="localhost",
        port=6666,
        timeout=60.0,
        retry_count=3,
        extra_config={
            "authentication": True,
            "api_key": "your-api-key",
            "secure_connection": True
        }
    )
    
    agent = APIFactory.create_client(APIFactory.ClientType.AGENT_CLIENT, config)
    
    try:
        agent.connect()
        
        # Batch operations
        print("--- Batch Operations ---")
        
        # Submit multiple jobs
        job_configs = [
            {"test_suite": "unit_tests", "priority": "high"},
            {"test_suite": "integration_tests", "priority": "medium"},
            {"test_suite": "performance_tests", "priority": "low"}
        ]
        
        job_ids = []
        for i, job_config in enumerate(job_configs):
            job_id = agent.submit_test_job(job_config)
            job_ids.append(job_id)
            print(f"Submitted job {i+1}: {job_id}")
        
        # Monitor all jobs
        print("\n--- Batch Monitoring ---")
        completed_jobs = []
        
        while len(completed_jobs) < len(job_ids):
            for job_id in job_ids:
                if job_id not in completed_jobs:
                    status = agent.get_job_status(job_id)
                    if status.get('state') in ['completed', 'failed']:
                        completed_jobs.append(job_id)
                        print(f"Job {job_id} completed with status: {status.get('state')}")
            
            if len(completed_jobs) < len(job_ids):
                time.sleep(2)
        
        # Batch results
        print("\n--- Batch Results ---")
        for job_id in job_ids:
            results = agent.get_job_results(job_id)
            print(f"Job {job_id}: {results.get('tests_passed', 0)}/{results.get('tests_run', 0)} passed")
        
        # Agent maintenance
        print("\n--- Agent Maintenance ---")
        
        # Cleanup completed jobs
        cleanup_result = agent.cleanup_completed_jobs(older_than=3600)  # 1 hour
        print(f"Cleaned up jobs: {cleanup_result.get('cleaned_count', 0)}")
        
        # Get agent health
        health = agent.get_health_status()
        print(f"Agent Health: {health.get('status')}")
        print(f"Health Score: {health.get('score', 0)}/100")
        
        # Restart services if needed
        if health.get('score', 100) < 80:
            print("Health score low, restarting services...")
            restart_result = agent.restart_services()
            print(f"Services restarted: {'✓' if restart_result else '✗'}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        agent.disconnect()


def agent_clustering_example():
    """Agent clustering and load balancing example."""
    print("\n=== Agent Clustering Example ===")
    
    # Connect to multiple agents
    agent_configs = [
        {"host": "localhost", "port": 6666},
        {"host": "localhost", "port": 6667},
        {"host": "localhost", "port": 6668}
    ]
    
    agents = []
    
    try:
        # Connect to all agents
        print("--- Connecting to Agent Cluster ---")
        for i, config in enumerate(agent_configs):
            try:
                agent = APIFactory.create_agent_client(
                    host=config["host"],
                    port=config["port"]
                )
                agent.connect()
                if agent.is_connected():
                    agents.append(agent)
                    print(f"✓ Connected to agent {i+1} at {config['host']}:{config['port']}")
                else:
                    print(f"✗ Failed to connect to agent {i+1}")
            except Exception as e:
                print(f"✗ Error connecting to agent {i+1}: {e}")
        
        if not agents:
            print("No agents available for clustering example")
            return
        
        # Load balancing
        print(f"\n--- Load Balancing ({len(agents)} agents) ---")
        
        # Submit jobs across agents
        test_jobs = [
            {"test_suite": f"test_suite_{i}", "priority": "normal"}
            for i in range(len(agents) * 2)  # 2 jobs per agent
        ]
        
        submitted_jobs = []
        
        for i, job_config in enumerate(test_jobs):
            agent = agents[i % len(agents)]  # Round-robin distribution
            try:
                job_id = agent.submit_test_job(job_config)
                submitted_jobs.append((agent, job_id))
                print(f"Job {i+1} submitted to agent {(i % len(agents)) + 1}: {job_id}")
            except Exception as e:
                print(f"Failed to submit job {i+1}: {e}")
        
        # Monitor cluster status
        print("\n--- Cluster Status ---")
        for i, agent in enumerate(agents):
            try:
                resources = agent.get_system_resources()
                performance = agent.get_performance_metrics()
                
                print(f"Agent {i+1}:")
                print(f"  CPU: {resources.get('cpu_percent', 0)}%")
                print(f"  Active Jobs: {performance.get('active_jobs', 0)}")
                print(f"  Queue Size: {performance.get('queued_jobs', 0)}")
            except Exception as e:
                print(f"Agent {i+1}: Error getting status - {e}")
        
        # Cluster statistics
        print("\n--- Cluster Statistics ---")
        total_active = sum(agent.get_performance_metrics().get('active_jobs', 0) 
                          for agent in agents)
        total_queued = sum(agent.get_performance_metrics().get('queued_jobs', 0) 
                          for agent in agents)
        
        print(f"Total Active Jobs: {total_active}")
        print(f"Total Queued Jobs: {total_queued}")
        print(f"Average Load: {total_active / len(agents):.1f} jobs/agent")
        
    except Exception as e:
        print(f"Error in clustering: {e}")
    finally:
        # Cleanup all agent connections
        for i, agent in enumerate(agents):
            try:
                agent.disconnect()
                print(f"Disconnected from agent {i+1}")
            except Exception:
                pass


if __name__ == "__main__":
    print("VTA Agent Client Examples")
    print("=========================")
    
    # Run all examples
    try:
        basic_agent_operations()
        test_execution_example()
        device_management_example()
        resource_monitoring_example()
        configuration_management_example()
        advanced_agent_operations()
        agent_clustering_example()
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    
    print("\nAll agent examples completed!")

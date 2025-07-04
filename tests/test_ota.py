import pytest
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass
from typing import Dict, Any

from vta.tasks.ota.ota import (
    OTA, OTAConfig, VehicleMode, VehicleModeManager,
    OTAError, OTAConnectionError, OTAUpgradeError,
    create_ota_from_legacy_config
)


@pytest.fixture
def mock_serial_client():
    """Mock serial client for testing."""
    mock = Mock()
    mock.connect = Mock()
    mock.disconnect = Mock()
    mock.send_command = Mock()
    mock.execute_command = Mock(return_value=["100 /ota/bsw/log/subda.log"])
    mock.wait_for_trace = Mock(return_value=(True, ["A"]))
    return mock


@pytest.fixture
def mock_adb_controller():
    """Mock ADB controller for testing."""
    mock = Mock()
    mock.execute_adb_command = Mock()
    return mock


@pytest.fixture
def mock_tsmaster():
    """Mock TSMaster for testing."""
    mock = Mock()
    mock.set_signal_value = Mock()
    mock.get_signal_value = Mock(return_value=1.0)
    mock.disconnect = Mock()
    return mock


@pytest.fixture
def mock_android_automator():
    """Mock Android automator for testing."""
    mock = Mock()
    mock.connect = Mock()
    mock.disconnect = Mock()
    mock.check_text_exists = Mock(return_value=True)
    mock.click_text = Mock(return_value=True)
    return mock


@pytest.fixture
def ota_config():
    """Sample OTA configuration for testing."""
    return OTAConfig(
        putty_config={
            "putty_enabled": True,
            "putty_comport": "COM44",
            "putty_baudrate": 921600,
            "putty_username": "",
            "putty_password": "",
        },
        tsmaster_config={
            "app_name": "TSMaster",
            "dev_mode": "CAN",
            "auto_start_simulation": True
        },
        device_id="test_device_123"
    )


@pytest.fixture
def ota_instance(ota_config, mock_serial_client, mock_adb_controller, 
                mock_tsmaster, mock_android_automator):
    """Create OTA instance with mocked dependencies."""
    with patch('vta.tasks.ota.ota.countdown'):
        ota = OTA(
            config=ota_config,
            serial_client=mock_serial_client,
            adb_controller=mock_adb_controller,
            tsmaster=mock_tsmaster,
            android_automator=mock_android_automator
        )
    return ota


class TestOTAConfig:
    """Test OTA configuration."""
    
    def test_ota_config_creation(self):
        """Test OTAConfig creation with valid data."""
        config = OTAConfig(
            putty_config={"test": "value"},
            tsmaster_config={"app_name": "TSMaster"},
            device_id="test_device"
        )
        assert config.device_id == "test_device"
        assert config.signal_path.endswith("VehModMngtGlbSafe1UsgModSts")
        assert config.log_path == "/ota/bsw/log/subda.log"

    def test_ota_config_empty_device_id(self):
        """Test OTAConfig raises error with empty device_id."""
        with pytest.raises(ValueError, match="device_id cannot be empty"):
            OTAConfig(
                putty_config={},
                tsmaster_config={},
                device_id=""
            )

    def test_ota_config_from_dict(self):
        """Test creating OTAConfig from dictionary."""
        config_dict = {
            "putty_config": {"test": "value"},
            "tsmaster_config": {"app_name": "TSMaster"},
            "device_id": "test_device"
        }
        config = OTAConfig(**config_dict)
        assert config.device_id == "test_device"


class TestVehicleModeManager:
    """Test VehicleModeManager functionality."""
    
    @pytest.fixture
    def vehicle_mode_manager(self, mock_tsmaster):
        """Create VehicleModeManager with mocked TSMaster."""
        return VehicleModeManager(mock_tsmaster, "test/signal/path")

    def test_set_mode_success(self, vehicle_mode_manager, mock_tsmaster):
        """Test successful vehicle mode setting."""
        result = vehicle_mode_manager.set_mode(VehicleMode.DRIVING)
        assert result is True
        mock_tsmaster.set_signal_value.assert_called_once_with("test/signal/path", 13.0)

    def test_set_mode_with_string(self, vehicle_mode_manager, mock_tsmaster):
        """Test setting vehicle mode with string value."""
        result = vehicle_mode_manager.set_mode("driving")
        assert result is True
        mock_tsmaster.set_signal_value.assert_called_once_with("test/signal/path", 13.0)

    def test_set_mode_exception(self, vehicle_mode_manager, mock_tsmaster):
        """Test vehicle mode setting with exception."""
        mock_tsmaster.set_signal_value.side_effect = Exception("Test error")
        result = vehicle_mode_manager.set_mode(VehicleMode.DRIVING)
        assert result is False

    def test_get_current_mode_success(self, vehicle_mode_manager, mock_tsmaster):
        """Test successful current mode retrieval."""
        mock_tsmaster.get_signal_value.return_value = 13.0
        mode = vehicle_mode_manager.get_current_mode()
        assert mode == VehicleMode.DRIVING

    def test_get_current_mode_unknown_value(self, vehicle_mode_manager, mock_tsmaster):
        """Test current mode retrieval with unknown signal value."""
        mock_tsmaster.get_signal_value.return_value = 999.0
        mode = vehicle_mode_manager.get_current_mode()
        assert mode is None

    def test_get_current_mode_exception(self, vehicle_mode_manager, mock_tsmaster):
        """Test current mode retrieval with exception."""
        mock_tsmaster.get_signal_value.side_effect = Exception("Test error")
        mode = vehicle_mode_manager.get_current_mode()
        assert mode is None


class TestOTAInitialization:
    """Test OTA class initialization."""

    def test_ota_init_with_config(self, ota_config, mock_serial_client, 
                                 mock_adb_controller, mock_tsmaster, mock_android_automator):
        """Test OTA initialization with OTAConfig."""
        with patch('vta.tasks.ota.ota.countdown'):
            ota = OTA(
                config=ota_config,
                serial_client=mock_serial_client,
                adb_controller=mock_adb_controller,
                tsmaster=mock_tsmaster,
                android_automator=mock_android_automator
            )
        assert ota.config.device_id == "test_device_123"
        assert ota.putty == mock_serial_client
        assert ota.adb == mock_adb_controller

    def test_ota_init_with_dict(self, mock_serial_client, mock_adb_controller, 
                               mock_tsmaster, mock_android_automator):
        """Test OTA initialization with dictionary config."""
        config_dict = {
            "putty_config": {"test": "value"},
            "tsmaster_config": {"app_name": "TSMaster"},
            "device_id": "test_device"
        }
        with patch('vta.tasks.ota.ota.countdown'):
            ota = OTA(
                config=config_dict,
                serial_client=mock_serial_client,
                adb_controller=mock_adb_controller,
                tsmaster=mock_tsmaster,
                android_automator=mock_android_automator
            )
        assert ota.config.device_id == "test_device"

    def test_ota_init_connection_failure(self, ota_config, mock_serial_client, 
                                        mock_adb_controller, mock_tsmaster, mock_android_automator):
        """Test OTA initialization with connection failure."""
        mock_serial_client.connect.side_effect = Exception("Connection failed")
        
        with pytest.raises(OTAConnectionError, match="Failed to connect services"):
            with patch('vta.tasks.ota.ota.countdown'):
                OTA(
                    config=ota_config,
                    serial_client=mock_serial_client,
                    adb_controller=mock_adb_controller,
                    tsmaster=mock_tsmaster,
                    android_automator=mock_android_automator
                )


class TestOTAMethods:
    """Test OTA class methods."""

    def test_switch_vehicle_mode_success(self, ota_instance):
        """Test successful vehicle mode switching."""
        with patch.object(ota_instance.vehicle_mode_manager, 'set_mode', return_value=True), \
             patch.object(ota_instance.vehicle_mode_manager, 'wait_for_mode', return_value=True):
            result = ota_instance.switch_vehicle_mode(VehicleMode.DRIVING)
            assert result is True

    def test_switch_vehicle_mode_invalid_string(self, ota_instance):
        """Test vehicle mode switching with invalid string."""
        result = ota_instance.switch_vehicle_mode("invalid_mode")
        assert result is False

    def test_navigate_to_upgrade_page_success(self, ota_instance, mock_adb_controller):
        """Test successful navigation to upgrade page."""
        with patch('time.sleep'):
            result = ota_instance._navigate_to_upgrade_page()
            assert result is True
            mock_adb_controller.execute_adb_command.assert_called_once()

    def test_navigate_to_upgrade_page_failure(self, ota_instance, mock_adb_controller):
        """Test failed navigation to upgrade page."""
        mock_adb_controller.execute_adb_command.side_effect = Exception("ADB error")
        result = ota_instance._navigate_to_upgrade_page()
        assert result is False

    def test_get_current_ota_slot_success(self, ota_instance, mock_serial_client):
        """Test successful OTA slot retrieval."""
        mock_serial_client.wait_for_trace.return_value = (True, ["A"])
        slot = ota_instance._get_current_ota_slot()
        assert slot == "A"

    def test_get_current_ota_slot_failure(self, ota_instance, mock_serial_client):
        """Test failed OTA slot retrieval."""
        mock_serial_client.wait_for_trace.return_value = (False, None)
        slot = ota_instance._get_current_ota_slot()
        assert slot is None

    def test_is_upgrade_ready_true(self, ota_instance, mock_android_automator):
        """Test upgrade ready check returning True."""
        with patch.object(ota_instance, '_navigate_to_upgrade_page', return_value=True):
            mock_android_automator.check_text_exists.return_value = True
            result = ota_instance._is_upgrade_ready()
            assert result is True

    def test_is_upgrade_ready_false(self, ota_instance, mock_android_automator):
        """Test upgrade ready check returning False."""
        with patch.object(ota_instance, '_navigate_to_upgrade_page', return_value=True):
            mock_android_automator.check_text_exists.return_value = False
            result = ota_instance._is_upgrade_ready()
            assert result is False

    def test_get_log_line_count_success(self, ota_instance, mock_serial_client):
        """Test successful log line count retrieval."""
        mock_serial_client.execute_command.return_value = ["150 /ota/bsw/log/subda.log"]
        count = ota_instance._get_log_line_count()
        assert count == 150

    def test_get_log_line_count_failure(self, ota_instance, mock_serial_client):
        """Test failed log line count retrieval."""
        mock_serial_client.execute_command.return_value = []
        count = ota_instance._get_log_line_count()
        assert count == 0

    def test_trigger_upgrade_via_dhu_success(self, ota_instance, mock_android_automator):
        """Test successful upgrade trigger via DHU."""
        with patch.object(ota_instance, '_navigate_to_upgrade_page', return_value=True), \
             patch.object(ota_instance, '_is_upgrade_triggered', return_value=True), \
             patch('vta.tasks.ota.ota.wait_and_retry') as mock_retry:
            
            # Mock the retry decorator to return the original function
            mock_retry.return_value = lambda func: func
            mock_android_automator.click_text.return_value = True
            
            result = ota_instance.trigger_upgrade_via_dhu()
            assert result is True

    def test_is_ota_upgrade_successful_true(self, ota_instance):
        """Test successful OTA upgrade check."""
        with patch.object(ota_instance, '_get_current_ota_slot', return_value="B"):
            result = ota_instance._is_ota_upgrade_successful("A")
            assert result is True

    def test_is_ota_upgrade_successful_false(self, ota_instance):
        """Test failed OTA upgrade check."""
        with patch.object(ota_instance, '_get_current_ota_slot', return_value="A"):
            result = ota_instance._is_ota_upgrade_successful("A")
            assert result is False

    def test_is_ota_upgrade_successful_no_previous_slot(self, ota_instance):
        """Test OTA upgrade check with no previous slot."""
        result = ota_instance._is_ota_upgrade_successful("")
        assert result is False


class TestOTATestExecution:
    """Test OTA test execution."""

    def test_perform_ota_test_all_steps_skipped(self, ota_instance):
        """Test OTA test with all steps skipped."""
        with patch.object(ota_instance, '_get_current_ota_slot', return_value="A"):
            result = ota_instance.perform_ota_test(
                skip_download=True,
                skip_trigger_upgrade=True,
                skip_upgrade_monitor=True,
                skip_slot_check=True
            )
            assert result is True

    def test_perform_ota_test_download_step(self, ota_instance):
        """Test OTA test download step."""
        with patch.object(ota_instance, '_get_current_ota_slot', return_value="A"), \
             patch.object(ota_instance, '_is_upgrade_ready', return_value=False), \
             patch.object(ota_instance, '_perform_download_step'), \
             patch.object(ota_instance, '_perform_trigger_upgrade_step'), \
             patch.object(ota_instance, '_perform_upgrade_monitor_step'), \
             patch.object(ota_instance, '_perform_slot_check_step', return_value=True):
            
            result = ota_instance.perform_ota_test()
            assert result is True

    def test_perform_ota_test_no_previous_slot(self, ota_instance):
        """Test OTA test with no previous slot available."""
        with patch.object(ota_instance, '_get_current_ota_slot', return_value=None):
            with pytest.raises(OTAUpgradeError, match="Cannot get previous OTA slot"):
                ota_instance.perform_ota_test()

    def test_perform_download_step_success(self, ota_instance):
        """Test successful download step."""
        with patch.object(ota_instance, 'switch_vehicle_mode', return_value=True), \
             patch.object(ota_instance, '_is_downloading_in_progress', return_value=True), \
             patch.object(ota_instance, '_record_log_start_line'), \
             patch.object(ota_instance, 'monitor_download_status', return_value=True):
            
            ota_instance._perform_download_step()  # Should not raise

    def test_perform_download_step_mode_switch_failure(self, ota_instance):
        """Test download step with mode switch failure."""
        with patch.object(ota_instance, 'switch_vehicle_mode', return_value=False):
            with pytest.raises(OTAUpgradeError, match="Failed to switch to driving mode"):
                ota_instance._perform_download_step()


class TestOTACleanup:
    """Test OTA cleanup functionality."""

    def test_cleanup_success(self, ota_instance, mock_serial_client, mock_tsmaster, mock_android_automator):
        """Test successful cleanup."""
        ota_instance.cleanup()
        mock_serial_client.disconnect.assert_called_once()
        mock_tsmaster.disconnect.assert_called_once()
        mock_android_automator.disconnect.assert_called_once()

    def test_cleanup_with_exception(self, ota_instance, mock_serial_client):
        """Test cleanup with exception."""
        mock_serial_client.disconnect.side_effect = Exception("Cleanup error")
        # Should not raise exception
        ota_instance.cleanup()

    def test_context_manager(self, ota_config, mock_serial_client, mock_adb_controller, 
                           mock_tsmaster, mock_android_automator):
        """Test OTA as context manager."""
        with patch('vta.tasks.ota.ota.countdown'):
            with OTA(
                config=ota_config,
                serial_client=mock_serial_client,
                adb_controller=mock_adb_controller,
                tsmaster=mock_tsmaster,
                android_automator=mock_android_automator
            ) as ota:
                assert ota is not None
        
        # Cleanup should be called
        mock_serial_client.disconnect.assert_called()


class TestLegacyCompatibility:
    """Test legacy compatibility functions."""

    def test_create_ota_from_legacy_config(self):
        """Test creating OTA from legacy configuration."""
        putty_config = {"putty_enabled": True, "putty_comport": "COM44"}
        device_id = "test_device"
        tsmaster_config = {"app_name": "TSMaster"}
        
        with patch('vta.tasks.ota.ota.OTA') as mock_ota_class:
            create_ota_from_legacy_config(putty_config, device_id, tsmaster_config)
            
            # Verify OTA was called with correct configuration
            mock_ota_class.assert_called_once()
            call_args = mock_ota_class.call_args[0][0]
            assert call_args.device_id == device_id
            assert call_args.putty_config == putty_config


# Integration test fixtures and utilities
@pytest.fixture
def integration_config():
    """Configuration for integration tests."""
    return {
        "putty_config": {
            "putty_enabled": True,
            "putty_comport": "COM_TEST",
            "putty_baudrate": 921600,
        },
        "device_id": "integration_test_device",
        "tsmaster_config": {
            "app_name": "TSMaster",
            "dev_mode": "CAN",
        }
    }


@pytest.mark.integration
class TestOTAIntegration:
    """Integration tests for OTA (requires actual hardware)."""

    @pytest.mark.skip(reason="Requires actual hardware")
    def test_real_vehicle_mode_switch(self, integration_config):
        """Test real vehicle mode switching (requires hardware)."""
        ota = OTA(integration_config)
        try:
            current_mode = ota.vehicle_mode_manager.get_current_mode()
            assert current_mode is not None
        finally:
            ota.cleanup()

    @pytest.mark.skip(reason="Requires actual hardware")
    def test_real_ota_slot_query(self, integration_config):
        """Test real OTA slot query (requires hardware)."""
        ota = OTA(integration_config)
        try:
            slot = ota._get_current_ota_slot()
            assert slot in ["A", "B"] or slot is None
        finally:
            ota.cleanup()


# Parametrized tests
@pytest.mark.parametrize("mode,expected_value", [
    (VehicleMode.ABANDON, 0),
    (VehicleMode.INACTIVE, 1),
    (VehicleMode.ACTIVE, 11),
    (VehicleMode.DRIVING, 13),
])
def test_vehicle_mode_signal_mapping(mode, expected_value):
    """Test vehicle mode to signal value mapping."""
    assert VehicleModeManager.MODE_SIGNAL_MAP[mode] == expected_value


@pytest.mark.parametrize("slot_change,expected_result", [
    ("A", "B", True),
    ("B", "A", True),
    ("A", "A", False),
    ("B", "B", False),
])
def test_ota_upgrade_success_detection(slot_change, expected_result, ota_instance):
    """Test OTA upgrade success detection with different slot changes."""
    previous_slot, current_slot = slot_change
    with patch.object(ota_instance, '_get_current_ota_slot', return_value=current_slot):
        result = ota_instance._is_ota_upgrade_successful(previous_slot)
        assert result == expected_result


# Performance tests
@pytest.mark.performance
class TestOTAPerformance:
    """Performance tests for OTA operations."""

    def test_vehicle_mode_switch_performance(self, ota_instance):
        """Test vehicle mode switch performance."""
        import time
        
        with patch.object(ota_instance.vehicle_mode_manager, 'set_mode', return_value=True), \
             patch.object(ota_instance.vehicle_mode_manager, 'wait_for_mode', return_value=True):
            
            start_time = time.time()
            ota_instance.switch_vehicle_mode(VehicleMode.DRIVING)
            end_time = time.time()
            
            # Should complete within reasonable time
            assert (end_time - start_time) < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

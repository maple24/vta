from vta.api.AndroidClient import AndroidClient
from vta.api.PuttyClient import SerialConfig, PuttyClient
from vta.api.TSmasterAPI.TSRPC import TSMasterRPC, TSMasterConfig, DeviceMode
from vta.api.DeviceClient import DeviceClient
from vta.library.utility.decorators import timed_step, wait_and_retry
from vta.library.utility.timelord import countdown
from loguru import logger
import time
import re
from typing import Union, Dict, Any
from dataclasses import dataclass
from enum import Enum


class VehicleMode(Enum):
    """Enumeration for vehicle modes."""
    ABANDON = "abandon"
    INACTIVE = "inactive"
    ACTIVE = "active"
    DRIVING = "driving"


@dataclass
class OTAConfig:
    """Configuration for OTA operations."""
    putty_config: Union[Dict[str, Any], SerialConfig]
    tsmaster_config: Union[Dict[str, Any], TSMasterConfig]
    device_id: str
    signal_path: str = "0/ZCU_CANFD1/ZCUD/ZcudZCUCANFD1Fr10/VehModMngtGlbSafe1UsgModSts"
    log_path: str = "/ota/bsw/log/subda.log"
    upgrade_app_activity: str = "com.flyme.auto.update/.UpdateMainActivity"
    
    def __post_init__(self):
        # Convert dict configs to proper dataclasses
        if isinstance(self.putty_config, dict):
            self.putty_config = SerialConfig.from_dict(self.putty_config)
        if isinstance(self.tsmaster_config, dict):
            self.tsmaster_config = TSMasterConfig(**self.tsmaster_config)


class VehicleModeManager:
    """Helper class for managing vehicle modes."""
    
    MODE_SIGNAL_MAP = {
        VehicleMode.ABANDON: 0,
        VehicleMode.INACTIVE: 1,
        VehicleMode.ACTIVE: 11,
        VehicleMode.DRIVING: 13,
    }
    
    def __init__(self, tsmaster: TSMasterRPC, signal_path: str):
        self.tsmaster = tsmaster
        self.signal_path = signal_path
    
    def set_mode(self, mode: VehicleMode) -> bool:
        """Set vehicle mode."""
        try:
            if isinstance(mode, str):
                mode = VehicleMode(mode)
            
            value = float(self.MODE_SIGNAL_MAP[mode])
            self.tsmaster.set_signal_value(self.signal_path, value)
            logger.info(f"Set vehicle mode to {mode.value} (signal value: {value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set vehicle mode to {mode}: {e}")
            return False
    
    def get_current_mode(self) -> VehicleMode:
        """Get current vehicle mode."""
        try:
            value = int(self.tsmaster.get_signal_value(self.signal_path))
            for mode, signal_value in self.MODE_SIGNAL_MAP.items():
                if signal_value == value:
                    return mode
            logger.warning(f"Unknown vehicle mode signal value: {value}")
            return None
        except Exception as e:
            logger.error(f"Failed to get current vehicle mode: {e}")
            return None
    
    @wait_and_retry(timeout=10, interval=1)
    def wait_for_mode(self, expected_mode: VehicleMode) -> bool:
        """Wait until vehicle mode equals expected mode."""
        current = self.get_current_mode()
        return current == expected_mode


class OTA:
    def __init__(self, config: Union[OTAConfig, Dict[str, Any]]) -> None:
        """
        Initialize the OTA class with required tools.

        Args:
            config: OTA configuration object or dictionary
        """
        # Handle different config types
        if isinstance(config, dict):
            # Extract legacy parameters for backward compatibility
            putty_config = config.get("putty_config", {})
            device_id = config.get("device_id", "")
            tsmaster_config = config.get("tsmaster_config", {})
            
            self.config = OTAConfig(
                putty_config=putty_config,
                tsmaster_config=tsmaster_config,
                device_id=device_id
            )
        else:
            self.config = config
        
        # Initialize components
        self.putty = PuttyClient()
        self.adb = AndroidClient(device_id=self.config.device_id)
        self.tsmaster = TSMasterRPC(self.config.tsmaster_config)
        self.device = DeviceClient()
        self.vehicle_mode_manager = VehicleModeManager(
            self.tsmaster, 
            self.config.signal_path
        )
        
        # Connect to services
        self._connect_services()
        self._set_log_level()

    def _connect_services(self):
        """Connect to all required services."""
        try:
            self.putty.connect(self.config.putty_config)
            self.device.connect(device_id=self.config.device_id)
            logger.success("All services connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect services: {e}")
            raise

    def _set_log_level(self):
        """Send 'dmesg -n 1' command in Putty several times before starting OTA test."""
        try:
            logger.info("Preparing Putty: sending 'dmesg -n 1' multiple times")
            for _ in range(3):
                self.putty.send_command("dmesg -n 1")
                time.sleep(0.2)
        except Exception as e:
            logger.error(f"Failed to send 'dmesg -n 1' in Putty: {e}")

    def switch_vehicle_mode(self, mode: Union[str, VehicleMode]) -> bool:
        """
        Switch vehicle mode using the vehicle mode manager.

        Args:
            mode: Vehicle mode to switch to

        Returns:
            bool: True if mode switch was successful
        """
        if isinstance(mode, str):
            try:
                mode = VehicleMode(mode)
            except ValueError:
                logger.error(f"Invalid mode: {mode}")
                return False
        
        logger.info(f"Switching vehicle to {mode.value} mode")
        
        if not self.vehicle_mode_manager.set_mode(mode):
            return False
        
        # Wait for mode to be applied
        if not self.vehicle_mode_manager.wait_for_mode(mode):
            logger.error(f"Failed to confirm vehicle mode switch to {mode.value}")
            return False
        
        logger.success(f"Successfully switched to {mode.value} mode")
        return True

    def _navigate_to_upgrade_page(self) -> bool:
        """Navigate to the upgrade page via ADB."""
        try:
            logger.info("Navigating to the upgrade page")
            self.adb.execute_adb_command(
                f"am start -n {self.config.upgrade_app_activity}"
            )
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to upgrade page: {e}")
            return False

    @wait_and_retry(interval=1, retry_times=3)
    def _get_current_ota_slot(self) -> str:
        """Get the current OTA slot by searching for 'current slot is:' in Putty logs."""
        logger.info("Querying current OTA slot using 'ota_tool -g'")
        pattern = r"current slot is:([AB])"
        result, match = self.putty.wait_for_trace(
            pattern=pattern, 
            command="ota_tool -g", 
            timeout=10, 
            auto_login=False
        )
        if result and match and match[0]:
            slot = match[0]
            logger.info(f"Current OTA slot: {slot}")
            return slot
        else:
            logger.error("Failed to parse current OTA slot from output")
            return None

    def _is_ota_upgrade_successful(self, previous_slot: str) -> bool:
        """
        Check if OTA upgrade was successful by comparing OTA slots.

        Args:
            previous_slot: The OTA slot before upgrade.

        Returns:
            bool: True if the slot has changed, indicating a successful upgrade.
        """
        current_slot = self._get_current_ota_slot()
        if current_slot and previous_slot and current_slot != previous_slot:
            logger.success(f"OTA upgrade successful: slot changed from {previous_slot} to {current_slot}")
            return True
        else:
            logger.error(f"OTA upgrade failed: slot did not change (still {current_slot})")
            return False

    def _is_upgrade_ready(self) -> bool:
        """
        Check if the upgrade is ready by navigating to the upgrade page and verifying the upgrade text exists.

        Returns:
            bool: True if the upgrade text is found, False otherwise.
        """
        logger.info("Checking if upgrade is ready by navigating to the upgrade page")
        if not self._navigate_to_upgrade_page():
            logger.error("Failed to navigate to upgrade page")
            return False

        # Check if the upgrade text exists (e.g., "立即更新")
        if self.device.check_text_exists(self.config.device_id, "立即更新"):
            logger.success("Upgrade is ready: '立即更新' found on the page")
            return True
        else:
            logger.info("Upgrade is not ready: '立即更新' not found")
            return False

    def _is_upgrade_triggered(self):
        if self.device.check_text_exists(self.config.device_id, "取消更新"):
            logger.success("Upgrade is triggered, please wait for 2 mins.")
            return True
        else:
            logger.warning("Failed to trigger upgrade")
            return False

    @wait_and_retry(timeout=300, interval=10)
    def _is_downloading_in_progress(self) -> bool:
        """
        Check if the OTA package is currently downloading by navigating to the upgrade page
        and verifying if the 'downloading' text exists.

        Returns:
            bool: True if downloading is in progress, False otherwise.
        """
        logger.info("Checking if OTA downloading is in progress by navigating to the upgrade page")
        if not self._navigate_to_upgrade_page():
            logger.error("Failed to navigate to upgrade page")
            return False

        # Check for either "发现新版本" or "安装包下载中"
        if (
            self.device.check_text_exists(self.config.device_id, "发现新版本")
            or self.device.check_text_exists(self.config.device_id, "安装包下载中")
        ):
            logger.success("OTA downloading is in progress: '发现新版本' or '安装包下载中' found on the page")
            return True
        else:
            logger.info("OTA downloading is not in progress: neither '发现新版本' nor '安装包下载中' found")
            return False

    def _get_log_line_count(self, log_path: str = None) -> int:
        """Get the line count of a log file using the PuttyHelper API."""
        log_path = log_path or self.config.log_path
        
        try:
            traces = self.putty.execute_command(
                f"wc -l {log_path}", 
                wait_time=1.0, 
                auto_login=False
            )
            
            if traces:
                for line in traces:
                    # Clean up ANSI escape sequences and carriage returns
                    clean_line = re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", line)
                    clean_line = clean_line.replace("\r", "").strip()
                    match = re.match(r"^(\d+)", clean_line)
                    if match:
                        count = int(match.group(1))
                        logger.debug(f"Line count of {log_path}: {count}")
                        return count
                        
            logger.error("Unable to get line count!")
            return 0
            
        except Exception as e:
            logger.error(f"Error getting log line count: {e}")
            return 0

    @wait_and_retry(interval=1, retry_times=3)
    def trigger_upgrade_via_dhu(self) -> bool:
        """
        Interact with DHU to trigger the upgrade process.

        Returns:
            bool: True if the upgrade was successfully triggered
        """
        logger.info("Triggering upgrade via DHU")
        # Step 1: Navigate to the upgrade page (replace with actual navigation commands)
        if not self._navigate_to_upgrade_page():
            return False

        # Step 2: Click the upgrade text
        retry_click = wait_and_retry(timeout=10, interval=1)(self.device.click_text)
        if not retry_click(self.config.device_id, "立即更新"):
            logger.error("Do not found `立即更新`, unable to upgrade")
            return False
        if not self._is_upgrade_triggered():
            return False
        return True

    def _record_log_start_line(self, attr_name: str, log_path: str = None):
        """Record the current log line count for later delta checks."""
        log_path = log_path or self.config.log_path
        setattr(self, attr_name, self._get_log_line_count(log_path))

    def _check_restart_complete(self, timeout=150) -> bool:
        """
        Wait for the device to finish restarting by checking for the 'Starting kernel' prompt
        in Putty using wait_for_trace. If not found, check for 'map' text on the screen.

        Args:
            timeout: Maximum time to wait in seconds.

        Returns:
            bool: True if restart is complete, False otherwise.
        """
        logger.info("Waiting for device restart to complete (Putty 'Starting kernel')")
        login_pattern = r"Starting kernel"
        result, match = self.putty.wait_for_trace(
            pattern=login_pattern, 
            command="", 
            timeout=timeout, 
            auto_login=False
        )
        if result:
            logger.success("Detected 'Starting kernel' prompt in Putty. Please wait 30s.")
            countdown(30)
            self._set_log_level()
            return True

        logger.error("Timeout waiting for device restart to complete (no 'Starting kernel' detected).")
        return False

    @timed_step("download_duration")
    @wait_and_retry(timeout=1800, interval=2)
    def monitor_download_status(self) -> bool:
        """Monitor the OTA download status by polling only new log lines for key patterns."""
        patterns = {
            "completed": re.compile(r"DOWNLOAD-COMPLETED"),
        }
        logger.info("Polling OTA download status from subda.log (single check)")

        start_line = getattr(self, "_download_log_start_line", 0)
        current_line = self._get_log_line_count()
        num_new_lines = max(0, current_line - start_line)
        traces = []
        
        if num_new_lines > 0:
            setattr(self, "_download_log_start_line", current_line)
            try:
                traces = self.putty.execute_command(
                    f"tail -n +{start_line + 1} {self.config.log_path} | head -n {num_new_lines}", 
                    wait_time=1.0, 
                    auto_login=False
                )
            except Exception as e:
                logger.error(f"Error reading log lines: {e}")
                return False

        for line in traces:
            if patterns["completed"].search(line):
                logger.success("Package download completed successfully")
                return True

        logger.debug("Package download completion pattern not detected yet")
        return False

    @timed_step("upgrade_duration")
    @wait_and_retry(timeout=1800, interval=2)
    def monitor_upgrade_status(self) -> bool:
        """Monitor the OTA upgrade status by polling only new log lines for key patterns."""
        patterns = {
            "completed": re.compile(r"INSTALLATION-COMPLETED"),
        }
        logger.info("Polling OTA upgrade status from subda.log (single check)")

        start_line = getattr(self, "_upgrade_log_start_line", 0)
        current_line = self._get_log_line_count()
        num_new_lines = max(0, current_line - start_line)
        traces = []
        
        if num_new_lines > 0:
            setattr(self, "_upgrade_log_start_line", current_line)
            try:
                traces = self.putty.execute_command(
                    f"tail -n +{start_line + 1} {self.config.log_path} | head -n {num_new_lines}", 
                    wait_time=1.0, 
                    auto_login=False
                )
            except Exception as e:
                logger.error(f"Error reading log lines: {e}")
                return False

        for line in traces:
            if patterns["completed"].search(line):
                logger.success("Upgrade completed successfully")
                return True

        logger.debug("Upgrade completion pattern not detected yet")
        return False

    def perform_ota_test(
        self,
        skip_download: bool = False,
        skip_trigger_upgrade: bool = False,
        skip_upgrade_monitor: bool = False,
        skip_slot_check: bool = False,
    ) -> bool:
        """Execute a complete OTA test loop with dynamic step control."""
        try:
            logger.info("Starting dynamic OTA test loop")

            previous_slot = self._get_current_ota_slot()
            if not previous_slot:
                logger.error("Cannot get previous OTA slot, aborting test.")
                return False

            # If upgrade is already ready, skip download steps
            upgrade_ready = self._is_upgrade_ready()
            if upgrade_ready:
                logger.info("Upgrade is already ready, skipping download steps.")
                skip_download = True

            # Step 1: Download (if not skipped)
            if not skip_download:
                logger.info("Switching to driving mode for package delivery.")
                if not self.switch_vehicle_mode(VehicleMode.DRIVING):
                    logger.error("Failed to switch to driving mode")
                    return False
                if not self._is_downloading_in_progress():
                    return False
                # Record log start line before monitoring download
                self._record_log_start_line("_download_log_start_line")
                logger.info("Monitoring download status.")
                if not self.monitor_download_status():
                    logger.error("Download package failed.")
                    return False
            else:
                logger.warning("Download step skipped.")

            # Step 2: Trigger upgrade (if not skipped)
            if not skip_trigger_upgrade:
                if not self.switch_vehicle_mode(VehicleMode.INACTIVE):
                    logger.error("Failed to switch to inactive mode")
                    return False

                if not self.trigger_upgrade_via_dhu():
                    logger.error("Failed to trigger upgrade via DHU")
                    return False
                countdown(120)
            else:
                logger.warning("Trigger upgrade step skipped.")

            # Step 3: Monitor upgrade (if not skipped)
            if not skip_upgrade_monitor:
                # Record log start line before monitoring upgrade
                self._record_log_start_line("_upgrade_log_start_line")
                logger.info("Monitoring upgrade status.")
                if not self.monitor_upgrade_status():
                    logger.error("OTA test failed during upgrade process")
                    return False
                if not self._check_restart_complete():
                    return False
            else:
                logger.warning("Upgrade monitor step skipped.")

            # Step 4: Check slot switch (if not skipped)
            if not skip_slot_check:
                logger.info("Checking if OTA slot switched.")
                if self._is_ota_upgrade_successful(previous_slot):
                    logger.success("OTA test completed successfully and slot switched")
                    self._log_performance_metrics()
                    return True
                else:
                    logger.error("OTA test failed: slot did not switch")
                    return False
            else:
                logger.warning("Slot check step skipped.")
                logger.success("OTA test completed with selected steps skipped.")
                return True

        except Exception as e:
            logger.error(f"OTA test failed with exception: {e}")
            return False

    def _log_performance_metrics(self):
        """Log performance metrics if available."""
        if hasattr(self, "download_duration"):
            logger.success(f"Download duration: {self.download_duration:.2f} seconds")
        if hasattr(self, "upgrade_duration"):
            logger.success(f"Upgrade duration: {self.upgrade_duration:.2f} seconds")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def cleanup(self):
        """Clean up all resources."""
        try:
            logger.info("Cleaning up OTA resources")
            if hasattr(self, "putty") and self.putty:
                self.putty.disconnect()
            if hasattr(self, "tsmaster") and self.tsmaster:
                self.tsmaster.disconnect()
            if hasattr(self, "device") and self.device:
                self.device.disconnect(self.config.device_id)
        except Exception as e:
            logger.error(f"Error during OTA cleanup: {e}")

    def __del__(self):
        """Destructor for automatic cleanup."""
        self.cleanup()


# Legacy constructor function for backward compatibility
def create_ota_from_legacy_config(putty_config: dict, device_id: str, tsmaster_config: dict = None) -> OTA:
    """Create OTA instance from legacy configuration format."""
    config = OTAConfig(
        putty_config=putty_config,
        tsmaster_config=tsmaster_config or {},
        device_id=device_id
    )
    return OTA(config)


if __name__ == "__main__":
    # Example 1: Using new OTAConfig
    print("=== Example 1: New Configuration Format ===")
    
    config = OTAConfig(
        putty_config={
            "putty_enabled": True,
            "putty_comport": "COM44",
            "putty_baudrate": 921600,
            "putty_username": "",
            "putty_password": "",
        },
        tsmaster_config={
            "app_name": "TSMaster",
            "dev_mode": DeviceMode.CAN,
            "auto_start_simulation": True
        },
        device_id="2801750c52300030"
    )
    
    try:
        with OTA(config) as ota:
            # Test vehicle mode switching
            current_mode = ota.vehicle_mode_manager.get_current_mode()
            logger.info(f"Current vehicle mode: {current_mode}")
            
            # Run OTA test with all steps skipped for demo
            test_result = ota.perform_ota_test(
                skip_download=True,
                skip_slot_check=True,
                skip_trigger_upgrade=True,
                skip_upgrade_monitor=True,
            )
            
            if test_result:
                logger.success("OTA test executed successfully")
            else:
                logger.error("OTA test execution failed")
                
    except Exception as e:
        logger.error(f"OTA test failed: {e}")

    # Example 2: Legacy compatibility
    print("\n=== Example 2: Legacy Compatibility ===")
    
    legacy_putty_config = {
        "putty_enabled": True,
        "putty_comport": "COM44",
        "putty_baudrate": 921600,
        "putty_username": "",
        "putty_password": "",
    }
    
    try:
        ota_legacy = create_ota_from_legacy_config(
            putty_config=legacy_putty_config,
            device_id="2801750c52300030"
        )
        logger.info("Legacy OTA instance created successfully")
        ota_legacy.cleanup()
        
    except Exception as e:
        logger.error(f"Legacy OTA creation failed: {e}")

    print("\n=== All Examples Completed ===")

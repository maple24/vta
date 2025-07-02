from vta.api.PuttyHelper import PuttyHelper
from vta.api.ADBClient import ADBClient
from vta.api.TSmasterAPI.TSRPC import TSMasterRPC
from vta.api.DeviceClient import DeviceClient
from vta.library.utility.decorators import timed_step, wait_and_retry
from vta.library.utility.timelord import countdown
from loguru import logger
import time
import re


class OTA:
    def __init__(self, putty_config: dict, device_id: str) -> None:
        """
        Initialize the OTA class with required tools.

        Args:
            putty_config: Configuration parameters for PuttyHelper
            device_id: Device ID for ADB and DeviceClient
        """
        self.putty = PuttyHelper()
        self.adb: ADBClient = ADBClient(device_id=device_id)
        self.tsmaster = TSMasterRPC()
        self.device = DeviceClient()
        self.putty.connect(putty_config)
        self.device.connect(device_id=device_id)
        self._set_log_level()
        self.device_id = device_id

    def _set_log_level(self):
        """
        Send 'dmesg -n 1' command in Putty before starting OTA test.
        """
        try:
            logger.info("Preparing Putty: sending 'dmesg -n 1'")
            self.putty.send_command("dmesg -n 1")
        except Exception as e:
            logger.error(f"Failed to send 'dmesg -n 1' in Putty: {e}")

    def switch_vehicle_mode(self, mode: str) -> bool:
        """
        Switch vehicle between inactive and driving modes using set_signal_value.

        Args:
            mode: "inactive" or "driving"

        Returns:
            bool: True if mode switch was successful
        """
        logger.info(f"Switching vehicle to {mode} mode using set_signal_value")
        signal_path = "0/ZCU_CANFD1/ZCUD/ZcudZCUCANFD1Fr10/VehModMngtGlbSafe1UsgModSts"
        mode_signal_map = {
            "abandon": 0,
            "inactive": 1,
            "active": 11,
            "driving": 13,
        }
        if mode not in mode_signal_map:
            logger.error(f"Invalid mode: {mode}. Use 'inactive' or 'driving'")
            return False

        value = mode_signal_map[mode]
        self.tsmaster.set_signal_value(signal_path, value)
        logger.info(f"Set {signal_path} to {value} for mode {mode}")
        if not self._wait_signal_value(signal_path, value, timeout=3, interval=1):
            logger.error(f"Failed to set {signal_path} to {value} after retries")
            return False

        return True

    def _wait_signal_value(
        self,
        signal_path: str,
        expected_value,
        timeout=10,
        interval=1,
        retry_times=None,
    ) -> bool:
        """Wait until the signal value equals expected_value, with retry."""

        @wait_and_retry(timeout=timeout, interval=interval, retry_times=retry_times)
        def check():
            return self.tsmaster.get_signal_value(signal_path) == expected_value

        return check()

    def _navigate_to_upgrade_page(self) -> bool:
        """
        Private helper to navigate to the upgrade page via ADB.

        Returns:
            bool: True if navigation command was sent successfully
        """
        try:
            logger.info("Navigating to the upgrade page")
            self.adb.execute_adb_command("am start -n com.flyme.auto.update/.UpdateMainActivity")
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to upgrade page: {e}")
            return False

    def _get_current_ota_slot(self) -> str:
        """
        Get the current OTA slot by searching for 'current slot is:' in Putty logs.

        Returns:
            str: The current slot ('A' or 'B'), or None if not found.
        """
        logger.info("Querying current OTA slot using 'ota_tool -g'")
        pattern = r"current slot is:([AB])"
        result, match = self.putty.wait_for_trace(pattern=pattern, cmd="ota_tool -g", timeout=10, login=False)
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
        if self.device.check_text_exists(self.device_id, "立即更新"):
            logger.success("Upgrade is ready: '立即更新' found on the page")
            return True
        else:
            logger.info("Upgrade is not ready: '立即更新' not found")
            return False

    def _is_upgrade_triggered(self):
        if self.device.check_text_exists(self.device_id, "取消更新"):
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
            self.device.check_text_exists(self.device_id, "发现新版本")
            or self.device.check_text_exists(self.device_id, "安装包下载中")
        ):
            logger.success("OTA downloading is in progress: '发现新版本' or '安装包下载中' found on the page")
            return True
        else:
            logger.info("OTA downloading is not in progress: neither '发现新版本' nor '安装包下载中' found")
            return False

    def _get_log_line_count(self, log_path: str) -> int:
        traces = self.putty.send_command_and_return_traces(f"wc -l {log_path}", wait=1, login=False)
        if traces:
            for line in traces:
                clean_line = re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", line)
                clean_line = clean_line.replace("\r", "").strip()
                match = re.match(r"^(\d+)", clean_line)
                if match:
                    count = int(match.group(1))
                    logger.info(f"The line cound of subda.log is {count}")
                    return count
        logger.error("Unable to get line count!")
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
        if not retry_click(self.device_id, "立即更新"):
            logger.error("Do not found `立即更新`, unable to upgrade")
            return False
        if not self._is_upgrade_triggered():
            return False
        return True

    def _record_log_start_line(self, attr_name: str, log_path: str = "/ota/bsw/log/subda.log"):
        """
        Record the current log line count for later delta checks.
        Args:
            attr_name: The attribute name to store the start line (e.g., '_download_log_start_line').
            log_path: The log file path to check.
        """
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
        result, match = self.putty.wait_for_trace(pattern=login_pattern, cmd="", timeout=timeout, login=False)
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
        """
        Monitor the OTA download status by polling only new log lines for key patterns.
        Returns True if download completes, False otherwise.
        """
        log_path = "/ota/bsw/log/subda.log"
        patterns = {
            "completed": re.compile(r"DOWNLOAD-COMPLETED"),
        }
        logger.info("Polling OTA download status from subda.log (single check)")

        start_line = getattr(self, "_download_log_start_line", 0)
        current_line = self._get_log_line_count(log_path)
        num_new_lines = max(0, current_line - start_line)
        traces = []
        if num_new_lines > 0:
            setattr(self, "_download_log_start_line", current_line)
            traces = self.putty.send_command_and_return_traces(
                f"tail -n +{start_line + 1} {log_path} | head -n {num_new_lines}", wait=1, login=False
            )

        for line in traces:
            if patterns["completed"].search(line):
                logger.success("Package download completed successfully")
                return True

        logger.info("Package download completion pattern not detected yet")
        return False

    @timed_step("upgrade_duration")
    @wait_and_retry(timeout=1800, interval=2)
    def monitor_upgrade_status(self) -> bool:
        """
        Monitor the OTA upgrade status by polling only new log lines for key patterns.
        Returns True if upgrade completes, False otherwise.
        """
        log_path = "/ota/bsw/log/subda.log"
        patterns = {
            "completed": re.compile(r"INSTALLATION-COMPLETED"),
        }
        logger.info("Polling OTA upgrade status from subda.log (single check)")

        start_line = getattr(self, "_upgrade_log_start_line", 0)
        current_line = self._get_log_line_count(log_path)
        num_new_lines = max(0, current_line - start_line)
        traces = []
        if num_new_lines > 0:
            setattr(self, "_upgrade_log_start_line", current_line)
            traces = self.putty.send_command_and_return_traces(
                f"tail -n +{start_line + 1} {log_path} | head -n {num_new_lines}", wait=1, login=False
            )

        for line in traces:
            if patterns["completed"].search(line):
                logger.success("Upgrade completed successfully")
                return True

        logger.info("Upgrade completion pattern not detected yet")
        return False

    def perform_ota_test(
        self,
        skip_download: bool = False,
        skip_trigger_upgrade: bool = False,
        skip_upgrade_monitor: bool = False,
        skip_slot_check: bool = False,
    ) -> bool:
        """
        Execute a complete OTA test loop with dynamic step control.

        Args:
            skip_download: Skip the download monitoring step.
            skip_trigger_upgrade: Skip triggering the upgrade via DHU.
            skip_upgrade_monitor: Skip monitoring the upgrade status.
            skip_slot_check: Skip checking if the OTA slot switched.

        Returns:
            bool: True if the OTA test was successful.
        """
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
                if not self.switch_vehicle_mode("driving"):
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
                if not self.switch_vehicle_mode("inactive"):
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
                    if hasattr(self, "download_duration"):
                        logger.success(f"Download duration: {self.download_duration:.2f} seconds")
                    if hasattr(self, "upgrade_duration"):
                        logger.success(f"Upgrade duration: {self.upgrade_duration:.2f} seconds")
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

    def __del__(self):
        """
        Custom method to destroy the OTA instance and clean up resources.
        """
        try:
            logger.info("Destroying OTA instance and cleaning up resources")
            if hasattr(self, "putty") and self.putty:
                self.putty.disconnect()
            if hasattr(self, "tsmaster") and self.tsmaster:
                self.tsmaster.__del__()
            if hasattr(self, "ui") and self.device:
                self.device.disconnect()
        except Exception as e:
            logger.error(f"Error during OTA instance cleanup: {e}")


if __name__ == "__main__":
    # Putty configuration
    putty_config = {
        "putty_enabled": True,
        "putty_comport": "COM44",
        "putty_baudrate": 921600,
        "putty_username": "",
        "putty_password": "",
    }

    # ADB configuration
    device_id = "2801750c52300030"

    # Initialize OTA class with all components
    ota = OTA(putty_config=putty_config, device_id=device_id)

    # Run the complete OTA test
    test_result = ota.perform_ota_test(
        skip_download=True,
        skip_slot_check=True,
        skip_trigger_upgrade=True,
        skip_upgrade_monitor=True,
    )

    # Print final result
    if test_result:
        logger.success("OTA test executed successfully")
    else:
        logger.error("OTA test execution failed")

    """
    dmesg -n 1

    root@lynkco:~# ota_tool -g
    using ota partition /ota
    ota_dir /ota
    [OTA_INFO][hobot_ota_hl.c:491] current slot is:A

    root@lynkco:~# ota_tool -v
    using ota partition /ota
    ota_dir /ota
    OTA Library version is 1.0.1
    system version is 20250624-024856

    Find install progress from putty
    tail -f /ota/bsw/log/subda.log   板端查看下载及安装的进度
    DOWNLOAD-COMPLETED
    INSTALLATION-COMPLETED
    tail -f /ota/bsw/log/otaclient.log
    """

    """
    install packages
    logcat | grep OtaMaster
    logcat -d | grep OtaMaster | tail -n 1
    DOWNLOAD-COMPLETED
    OTAFunction send hmi download progress
    after installation, there will be a popup from 
    """

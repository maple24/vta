import subprocess
import re
import time
from pathlib import Path
from typing import Optional, List, Tuple, Union
from loguru import logger


class AdbCommandError(Exception):
    """Custom exception for ADB command failures."""
    pass


class AdbController:
    """Android Debug Bridge (ADB) controller for device automation."""
    
    # Key codes for common actions
    KEYCODE_BACK = 4
    KEYCODE_HOME = 3
    KEYCODE_MENU = 82
    KEYCODE_VOLUME_UP = 24
    KEYCODE_VOLUME_DOWN = 25
    KEYCODE_APP_SWITCH = 187
    
    # Audio stream types
    STREAM_VOICE_CALL = 0
    STREAM_SYSTEM = 1
    STREAM_RING = 2
    STREAM_MUSIC = 3
    STREAM_ALARM = 4
    STREAM_NOTIFICATION = 5

    def __init__(self, adb_path: str = "adb", device_id: Optional[str] = None) -> None:
        """
        Initialize the ADB Controller.
        
        Args:
            adb_path: Path to the adb executable (default assumes adb is in PATH)
            device_id: ID of the ADB device to target (optional)
        """
        self.adb_path = adb_path
        self.device_id = device_id

    def _build_command(self, command: str, shell: bool = True) -> str:
        """
        Build the full ADB command string.
        
        Args:
            command: The command to execute
            shell: Whether this is a shell command
            
        Returns:
            Complete ADB command string
        """
        base_cmd = f"{self.adb_path}"
        if self.device_id:
            base_cmd += f" -s {self.device_id}"
        
        if shell:
            return f"{base_cmd} shell {command}"
        return f"{base_cmd} {command}"

    def execute_adb_command(self, command: str, shell: bool = True) -> Optional[str]:
        """
        Execute an ADB command.
        
        Args:
            command: The ADB command to execute
            shell: Whether this is a shell command
            
        Returns:
            Command output or None if failed
            
        Raises:
            AdbCommandError: If command execution fails
        """
        try:
            full_command = self._build_command(command, shell)
            result = subprocess.check_output(
                full_command, 
                shell=True, 
                stderr=subprocess.STDOUT,
                text=True
            )
            return result.strip()
        except subprocess.CalledProcessError as e:
            error_msg = f"ADB command failed: {e.output}"
            logger.error(error_msg)
            raise AdbCommandError(error_msg) from e

    # Touch and gesture methods
    def click_coordinates(self, x: int, y: int) -> None:
        """
        Simulate a touch action at specific screen coordinates.
        
        Args:
            x: X-coordinate
            y: Y-coordinate
        """
        command = f"input tap {x} {y}"
        self.execute_adb_command(command)
        logger.info(f"Simulated touch at coordinates ({x}, {y})")

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 500) -> None:
        """
        Simulate a swipe action from one point to another.
        
        Args:
            x1: Starting X-coordinate
            y1: Starting Y-coordinate
            x2: Ending X-coordinate
            y2: Ending Y-coordinate
            duration: Duration of the swipe in milliseconds
        """
        command = f"input swipe {x1} {y1} {x2} {y2} {duration}"
        self.execute_adb_command(command)
        logger.info(f"Simulated swipe from ({x1}, {y1}) to ({x2}, {y2}) with duration {duration}ms")

    def long_press(self, x: int, y: int, duration: int = 2000) -> None:
        """
        Simulate a long press at specific screen coordinates.
        
        Args:
            x: X-coordinate
            y: Y-coordinate
            duration: Duration of the long press in milliseconds
        """
        command = f"input swipe {x} {y} {x} {y} {duration}"
        self.execute_adb_command(command)
        logger.info(f"Simulated long press at coordinates ({x}, {y}) for {duration}ms")

    def multi_touch(self, points: List[Tuple[int, int]], duration: int = 500) -> None:
        """
        Simulate multi-touch gestures.
        
        Args:
            points: List of tuples representing touch points
            duration: Duration of the gesture in milliseconds
        """
        if len(points) < 2:
            raise ValueError("Multi-touch requires at least two points")

        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            command = f"input swipe {x1} {y1} {x2} {y2} {duration}"
            self.execute_adb_command(command)
            logger.info(f"Simulated multi-touch gesture: {command}")

    # Screen and UI methods
    def get_screen_dimensions(self) -> Optional[Tuple[int, int]]:
        """
        Retrieve the screen dimensions of the connected device.
        
        Returns:
            Tuple of (width, height) or None if failed
        """
        try:
            output = self.execute_adb_command("wm size")
            if output:
                dimensions_str = output.split(":")[1].strip()
                width, height = map(int, dimensions_str.split("x"))
                logger.info(f"Screen dimensions: width={width}, height={height}")
                return width, height
        except (IndexError, ValueError) as e:
            logger.error(f"Failed to parse screen dimensions: {e}")
        return None

    def click_text(self, text: str) -> bool:
        """
        Simulate a touch action on a UI element containing specific text.
        
        Args:
            text: Text of the UI element to click
            
        Returns:
            True if successful, False otherwise
        """
        dump_file = Path("window_dump.xml")
        
        try:
            # Dump UI and pull XML file
            dump_cmd = "uiautomator dump /sdcard/window_dump.xml"
            pull_cmd = "pull /sdcard/window_dump.xml ."
            
            self.execute_adb_command(dump_cmd)
            self.execute_adb_command(pull_cmd, shell=False)

            if not dump_file.exists():
                logger.error("Failed to retrieve UI dump")
                return False

            content = dump_file.read_text(encoding="utf-8")
            
            if text not in content:
                logger.warning(f"Text '{text}' not found in UI dump")
                return False

            # Extract bounds for the element containing the text
            pattern = rf'text="{re.escape(text)}".*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
            match = re.search(pattern, content)
            
            if not match:
                logger.warning(f"Failed to extract coordinates for text '{text}'")
                return False

            x1, y1, x2, y2 = map(int, match.groups())
            center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
            
            self.click_coordinates(center_x, center_y)
            logger.info(f"Clicked on text '{text}' at coordinates ({center_x}, {center_y})")
            return True
            
        except Exception as e:
            logger.error(f"Error clicking text '{text}': {e}")
            return False
        finally:
            # Clean up the dump file
            if dump_file.exists():
                dump_file.unlink()

    def input_text(self, text: str) -> None:
        """
        Simulate typing text into a focused input field.
        
        Args:
            text: Text to input
        """
        # Escape special characters for shell
        escaped_text = text.replace(' ', '%s').replace('&', '\\&')
        command = f"input text '{escaped_text}'"
        self.execute_adb_command(command)
        logger.info(f"Input text: {text}")

    # App management methods
    def launch_activity(self, package: str, activity: Optional[str] = None) -> Optional[str]:
        """
        Launch an application or specific activity.
        
        Args:
            package: Package name of the application
            activity: Activity name (optional)
            
        Returns:
            Command output or None if failed
        """
        if activity:
            command = f"am start -n {package}/{activity}"
        else:
            command = f"monkey -p {package} -c android.intent.category.LAUNCHER 1"
        
        result = self.execute_adb_command(command)
        logger.info(f"Launched activity: {package}/{activity or 'default'}")
        return result

    def force_stop_app(self, package_name: str) -> Optional[str]:
        """
        Force stop an application.
        
        Args:
            package_name: Package name of the application to stop
            
        Returns:
            Command output
        """
        command = f"am force-stop {package_name}"
        result = self.execute_adb_command(command)
        logger.info(f"Force stopped application: {package_name}")
        return result

    def is_app_installed(self, package_name: str) -> bool:
        """
        Check if an application is installed.
        
        Args:
            package_name: Package name to check
            
        Returns:
            True if installed, False otherwise
        """
        command = f"pm list packages | grep {package_name}"
        result = self.execute_adb_command(command)
        is_installed = result is not None and package_name in result
        logger.info(f"App {package_name} installed: {is_installed}")
        return is_installed

    def get_installed_packages(self) -> List[str]:
        """
        Get a list of all installed package names.
        
        Returns:
            List of package names
        """
        result = self.execute_adb_command("pm list packages")
        if result:
            packages = [line.replace("package:", "") for line in result.split("\n") if line.startswith("package:")]
            logger.info(f"Found {len(packages)} installed packages")
            return packages
        return []

    def get_app_version(self, package_name: str) -> Optional[str]:
        """
        Get the version of an installed application.
        
        Args:
            package_name: Package name to check
            
        Returns:
            Version string or None if not found
        """
        command = f"dumpsys package {package_name} | grep versionName"
        result = self.execute_adb_command(command)
        if result:
            try:
                version = result.split("=")[1].strip()
                logger.info(f"App {package_name} version: {version}")
                return version
            except (IndexError, ValueError):
                logger.error(f"Failed to parse version for {package_name}")
        return None

    def is_app_in_foreground(self, package_name: str) -> bool:
        """
        Check if a specific app is in the foreground.
        
        Args:
            package_name: Package name to check
            
        Returns:
            True if in foreground, False otherwise
        """
        result = self.execute_adb_command("dumpsys window windows | grep -E 'mCurrentFocus'")
        is_foreground = result is not None and package_name in result
        logger.info(f"App {package_name} {'is' if is_foreground else 'is NOT'} in foreground")
        return is_foreground

    def get_focused_app(self) -> Optional[str]:
        """
        Get the currently focused app/activity.
        
        Returns:
            Current focus information
        """
        result = self.execute_adb_command("dumpsys window | grep mCurrentFocus")
        logger.info(f"Current focus: {result}")
        return result

    def clear_app_data(self, package_name: str) -> Optional[str]:
        """
        Clear data for a specific app.
        
        Args:
            package_name: Package name of the app
            
        Returns:
            Command output
        """
        command = f"pm clear {package_name}"
        result = self.execute_adb_command(command)
        logger.info(f"Cleared data for {package_name}")
        return result

    # System navigation methods
    def press_key(self, keycode: int) -> None:
        """
        Press a key using keycode.
        
        Args:
            keycode: Android keycode constant
        """
        command = f"input keyevent {keycode}"
        self.execute_adb_command(command)
        logger.info(f"Pressed key with code {keycode}")

    def press_back(self) -> None:
        """Press the back button."""
        self.press_key(self.KEYCODE_BACK)
        logger.info("Pressed back button")

    def press_home(self) -> None:
        """Press the home button."""
        self.press_key(self.KEYCODE_HOME)
        logger.info("Pressed home button")

    def press_menu(self) -> None:
        """Press the menu button."""
        self.press_key(self.KEYCODE_MENU)
        logger.info("Pressed menu button")

    def open_recent_apps(self) -> None:
        """Open the recent apps screen."""
        self.press_key(self.KEYCODE_APP_SWITCH)
        logger.info("Opened recent apps")

    def open_notifications(self) -> None:
        """Open notification panel."""
        dimensions = self.get_screen_dimensions()
        if dimensions:
            width, height = dimensions
            self.swipe(width // 2, 0, width // 2, height // 2, 500)
            logger.info("Opened notification panel")
        else:
            logger.error("Failed to open notifications - couldn't get screen dimensions")

    def open_quick_settings(self) -> None:
        """Open quick settings panel."""
        dimensions = self.get_screen_dimensions()
        if dimensions:
            width, height = dimensions
            # First swipe to open notifications
            self.swipe(width // 2, 0, width // 2, height // 2, 300)
            time.sleep(0.3)
            # Second swipe to expand to quick settings
            self.swipe(width // 2, height // 4, width // 2, height // 2, 300)
            logger.info("Opened quick settings panel")
        else:
            logger.error("Failed to open quick settings - couldn't get screen dimensions")

    # Volume and media controls
    def set_volume(self, level: int, stream_type: int = STREAM_MUSIC) -> Optional[str]:
        """
        Set device volume to specific level.
        
        Args:
            level: Volume level to set
            stream_type: Audio stream type
            
        Returns:
            Command output
        """
        command = f"media volume --stream {stream_type} --set {level}"
        result = self.execute_adb_command(command)
        logger.info(f"Set volume to {level} for stream {stream_type}")
        return result

    def volume_up(self) -> None:
        """Increase volume."""
        self.press_key(self.KEYCODE_VOLUME_UP)
        logger.info("Volume up")

    def volume_down(self) -> None:
        """Decrease volume."""
        self.press_key(self.KEYCODE_VOLUME_DOWN)
        logger.info("Volume down")

    # Screenshot and utility methods
    def take_screenshot(self, output_path: Union[str, Path] = "screenshot.png") -> Path:
        """
        Take a screenshot and save it to the specified path.
        
        Args:
            output_path: Path to save the screenshot
            
        Returns:
            Path to the saved screenshot
        """
        output_path = Path(output_path)
        remote_path = "/sdcard/screenshot.png"
        
        self.execute_adb_command(f"screencap -p {remote_path}")
        self.execute_adb_command(f"pull {remote_path} {output_path}", shell=False)
        
        logger.info(f"Screenshot saved to {output_path}")
        return output_path

    # Car-specific launcher methods (keeping your existing functionality)
    def launch_car_launcher(self) -> Optional[str]:
        """Launch the Car Launcher interface."""
        return self.launch_activity("com.android.car.carlauncher", "CarLauncher")

    def launch_files(self) -> Optional[str]:
        """Launch the Files/Documents app."""
        return self.launch_activity("com.android.documentsui", "LauncherActivity")

    def launch_engineering_mode(self) -> Optional[str]:
        """Launch Engineering Mode app."""
        return self.launch_activity("com.bosch.apps.engineeringmode", "MainActivity")

    def launch_bluetooth_settings(self) -> Optional[str]:
        """Launch Bluetooth Settings."""
        command = "am start -a android.settings.BLUETOOTH_SETTINGS"
        result = self.execute_adb_command(command)
        logger.info("Launched Bluetooth Settings")
        return result

    def launch_wifi_settings(self) -> Optional[str]:
        """Launch WiFi Settings."""
        command = "am start -a android.settings.WIFI_SETTINGS"
        result = self.execute_adb_command(command)
        logger.info("Launched WiFi Settings")
        return result

    def launch_settings(self) -> Optional[str]:
        """Launch main Settings app."""
        command = "am start -a android.settings.SETTINGS"
        result = self.execute_adb_command(command)
        logger.info("Launched Settings")
        return result


if __name__ == "__main__":
    # Example usage
    controller = AdbController(device_id="DEVICE_ID_HERE")
    
    try:
        controller.click_coordinates(500, 500)
        controller.swipe(100, 100, 400, 400)
        controller.long_press(300, 300)
        controller.multi_touch([(100, 100), (200, 200), (300, 300)])
        
        dimensions = controller.get_screen_dimensions()
        print(f"Screen dimensions: {dimensions}")
        
        controller.click_text("Settings")
        controller.input_text("Hello World")
        
    except AdbCommandError as e:
        logger.error(f"ADB operation failed: {e}")
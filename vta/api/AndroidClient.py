import subprocess
from loguru import logger


class AndroidClient:
    def __init__(self, adb_path="adb", device_id=None):
        """
        Initialize the ADBClient class.
        :param adb_path: Path to the adb executable (default assumes adb is in PATH).
        :param device_id: ID of the ADB device to target (optional).
        """
        self.adb_path = adb_path
        self.device_id = device_id

    def execute_adb_command(self, command):
        """
        Execute an ADB shell command.
        :param command: The ADB shell command to execute.
        :return: Output of the command.
        """
        try:
            if self.device_id:
                full_command = f"{self.adb_path} -s {self.device_id} shell {command}"
            else:
                full_command = f"{self.adb_path} shell {command}"
            result = subprocess.check_output(full_command, shell=True, stderr=subprocess.STDOUT)
            return result.decode("utf-8").strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"ADB command failed: {e.output.decode('utf-8')}")
            return None

    def click_coordinates(self, x, y):
        """
        Simulate a touch action at specific screen coordinates.
        :param x: X-coordinate.
        :param y: Y-coordinate.
        """
        command = f"input tap {x} {y}"
        self.execute_adb_command(command)
        logger.info(f"Simulated touch at coordinates ({x}, {y})")

    def swipe(self, x1, y1, x2, y2, duration=500):
        """
        Simulate a swipe action from one point to another.
        :param x1: Starting X-coordinate.
        :param y1: Starting Y-coordinate.
        :param x2: Ending X-coordinate.
        :param y2: Ending Y-coordinate.
        :param duration: Duration of the swipe in milliseconds.
        """
        command = f"input swipe {x1} {y1} {x2} {y2} {duration}"
        self.execute_adb_command(command)
        logger.info(f"Simulated swipe from ({x1}, {y1}) to ({x2}, {y2}) with duration {duration}ms")

    def long_press(self, x, y, duration=2000):
        """
        Simulate a long press at specific screen coordinates.
        :param x: X-coordinate.
        :param y: Y-coordinate.
        :param duration: Duration of the long press in milliseconds.
        """
        command = f"input swipe {x} {y} {x} {y} {duration}"
        self.execute_adb_command(command)
        logger.info(f"Simulated long press at coordinates ({x}, {y}) for {duration}ms")

    def multi_touch(self, points, duration=500):
        """
        Simulate multi-touch gestures.
        :param points: List of tuples [(x1, y1), (x2, y2), ...] representing touch points.
        :param duration: Duration of the gesture in milliseconds.
        """
        if len(points) < 2:
            logger.error("Multi-touch requires at least two points.")
            return

        # Construct the command for multi-touch using `input swipe` for each pair of points
        commands = []
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            commands.append(f"input swipe {x1} {y1} {x2} {y2} {duration}")

        for command in commands:
            self.execute_adb_command(command)
            logger.info(f"Simulated multi-touch gesture: {command}")

    def get_screen_dimensions(self):
        """
        Retrieve the screen dimensions of the connected device.
        :return: Tuple (width, height) of the screen.
        """
        command = "wm size"
        output = self.execute_adb_command(command)
        if output:
            try:
                dimensions = output.split(":")[1].strip().split("x")
                width, height = int(dimensions[0]), int(dimensions[1])
                logger.info(f"Screen dimensions: width={width}, height={height}")
                return width, height
            except (IndexError, ValueError):
                logger.error("Failed to parse screen dimensions.")
        return None

    def click_text(self, text):
        """
        Simulate a touch action on a UI element containing specific text.
        :param text: Text of the UI element to click.
        """
        # Dump the UI hierarchy and pull the XML file
        command = f"uiautomator dump /sdcard/window_dump.xml && {self.adb_path} pull /sdcard/window_dump.xml ."
        if self.device_id:
            command = f"{self.adb_path} -s {self.device_id} shell uiautomator dump /sdcard/window_dump.xml && {self.adb_path} -s {self.device_id} pull /sdcard/window_dump.xml ."
        self.execute_adb_command(command)

        try:
            with open("window_dump.xml", "r", encoding="utf-8") as file:
                content = file.read()
                if text in content:
                    logger.info(f"Found text '{text}' in UI dump.")

                    # Extract the bounds attribute for the element containing the text
                    import re

                    match = re.search(rf'text="{text}".*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', content)
                    if match:
                        x1, y1, x2, y2 = map(int, match.groups())
                        # Calculate the center of the bounds
                        x = (x1 + x2) // 2
                        y = (y1 + y2) // 2
                        self.click_coordinates(x, y)
                        logger.info(f"Clicked on text '{text}' at coordinates ({x}, {y})")
                    else:
                        logger.warning(f"Failed to extract coordinates for text '{text}'")
                else:
                    logger.warning(f"Text '{text}' not found in UI dump.")
        except FileNotFoundError:
            logger.error("Failed to retrieve UI dump.")

    def input_text(self, text):
        """
        Simulate typing text into a focused input field.
        :param text: Text to input.
        """
        command = f"input text {text}"
        self.execute_adb_command(command)
        logger.info(f"Input text: {text}")

    def launch_activity(self, package, activity=None):
        """
        Launch an application or specific activity.
        :param package: Package name of the application.
        :param activity: Activity name (optional, launches default activity if None).
        """
        if activity:
            command = f"am start -n {package}/{activity}"
        else:
            command = f"am start -n {package}"
        result = self.execute_adb_command(command)
        logger.info(f"Launched activity: {package}/{activity if activity else ''}")
        return result

    def launch_car_launcher(self):
        """Launch the Car Launcher interface"""
        return self.launch_activity("com.android.car.carlauncher", ".CarLauncher")

    def launch_files(self):
        """Launch the Files/Documents app"""
        return self.launch_activity("com.android.documentsui", ".LauncherActivity")

    def launch_engineering_mode(self):
        """Launch Engineering Mode app"""
        return self.launch_activity("com.bosch.apps.engineeringmode", ".MainActivity")

    def launch_bluetooth_settings(self):
        """Launch Bluetooth Settings"""
        command = "am start -a android.settings.BLUETOOTH_SETTINGS"
        result = self.execute_adb_command(command)
        logger.info("Launched Bluetooth Settings")
        return result

    def launch_wifi_settings(self):
        """Launch WiFi Settings"""
        command = "am start -a android.settings.WIFI_SETTINGS"
        result = self.execute_adb_command(command)
        logger.info("Launched WiFi Settings")
        return result

    def launch_settings(self):
        """Launch main Settings app"""
        command = "am start -a android.settings.SETTINGS"
        result = self.execute_adb_command(command)
        logger.info("Launched Settings")
        return result

    def launch_maps(self):
        """Launch Maps/Navigation application"""
        return self.launch_activity("com.google.android.apps.maps", ".MapsActivity")

    def launch_media(self):
        """Launch Media player application"""
        return self.launch_activity("com.android.car.media", ".MediaActivity")

    def launch_phone(self):
        """Launch Phone/Dialer application"""
        return self.launch_activity("com.android.car.dialer", ".DialerActivity")

    def launch_vehicle_settings(self):
        """Launch Vehicle-specific settings"""
        return self.launch_activity("com.android.car.settings", ".CarSettings")

    def launch_climate_control(self):
        """Launch Climate Control interface"""
        return self.launch_activity("com.android.car.hvac", ".HvacController")

    def force_stop_app(self, package_name):
        """
        Force stop an application.
        :param package_name: Package name of the application to stop.
        """
        command = f"am force-stop {package_name}"
        result = self.execute_adb_command(command)
        logger.info(f"Force stopped application: {package_name}")
        return result

    def check_if_app_installed(self, package_name):
        """
        Check if an application is installed.
        :param package_name: Package name to check.
        :return: True if installed, False otherwise.
        """
        command = f"pm list packages | grep {package_name}"
        result = self.execute_adb_command(command)
        is_installed = result is not None and package_name in result
        logger.info(f"App {package_name} installed: {is_installed}")
        return is_installed

    def list_installed_apps(self):
        """
        Get a list of all installed applications.
        :return: List of package names.
        """
        command = "pm list packages"
        result = self.execute_adb_command(command)
        if result:
            packages = [line.replace("package:", "") for line in result.split("\n")]
            logger.info(f"Found {len(packages)} installed packages")
            return packages
        return []

    def get_app_version(self, package_name):
        """
        Get the version of an installed application.
        :param package_name: Package name to check.
        :return: Version string or None if not found.
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

    def open_recent_apps(self):
        """Open the recent apps screen"""
        command = "input keyevent KEYCODE_APP_SWITCH"
        self.execute_adb_command(command)
        logger.info("Opened recent apps")

    def open_notifications(self):
        """Open notification panel"""
        # Get screen dimensions
        dimensions = self.get_screen_dimensions()
        if dimensions:
            width, height = dimensions
            # Swipe from top center of screen down
            self.swipe(width // 2, 0, width // 2, height // 2, 500)
            logger.info("Opened notification panel")
        else:
            logger.error("Failed to open notifications - couldn't get screen dimensions")

    def open_quick_settings(self):
        """Open quick settings panel (two swipes from top)"""
        # Get screen dimensions
        dimensions = self.get_screen_dimensions()
        if dimensions:
            width, height = dimensions
            # First swipe to open notifications
            self.swipe(width // 2, 0, width // 2, height // 2, 300)
            # Second swipe to expand to quick settings
            self.swipe(width // 2, height // 4, width // 2, height // 2, 300)
            logger.info("Opened quick settings panel")
        else:
            logger.error("Failed to open quick settings - couldn't get screen dimensions")

    def start_split_screen(self):
        """
        Activate split screen mode for the current app
        Note: Must be in an app that supports split screen
        """
        # First open recent apps
        self.open_recent_apps()
        # Wait for animation
        import time

        time.sleep(1)
        # Long press on app icon or title bar (position may vary)
        dimensions = self.get_screen_dimensions()
        if dimensions:
            width, height = dimensions
            self.long_press(width // 2, height // 6, 1000)
            # Find and tap "Split screen" option (may need UI dump to locate)
            self.click_text("Split screen")
            logger.info("Activated split screen mode")
        else:
            logger.error("Failed to activate split screen - couldn't get screen dimensions")

    def is_app_in_foreground(self, package_name):
        """
        Check if a specific app is in the foreground.
        :param package_name: Package name to check.
        :return: True if in foreground, False otherwise.
        """
        command = "dumpsys window windows | grep -E 'mCurrentFocus'"
        result = self.execute_adb_command(command)
        if result and package_name in result:
            logger.info(f"App {package_name} is in foreground")
            return True
        logger.info(f"App {package_name} is NOT in foreground")
        return False

    def get_all_running_activities(self):
        """
        Get a list of all running activities.
        :return: Text output of running activities.
        """
        command = "dumpsys activity activities"
        result = self.execute_adb_command(command)
        logger.info("Retrieved running activities")
        return result

    def navigate_to_car_home(self):
        """Navigate to the car home screen"""
        self.press_home()
        logger.info("Navigated to car home screen")

    def change_volume(self, stream_type="3", volume_level=None, direction=None):
        """
        Change device volume. Stream types:
        0=voice call, 1=system, 2=ring, 3=music, 4=alarm, 5=notification

        :param stream_type: Audio stream type (default: 3 for media)
        :param volume_level: Specific volume level to set
        :param direction: "up" or "down" to adjust relative to current
        """
        if volume_level is not None:
            command = f"media volume --stream {stream_type} --set {volume_level}"
        elif direction == "up":
            command = "input keyevent 24"  # KEYCODE_VOLUME_UP
        elif direction == "down":
            command = "input keyevent 25"  # KEYCODE_VOLUME_DOWN
        else:
            logger.error("Must specify either volume_level or direction")
            return None

        result = self.execute_adb_command(command)
        logger.info(f"Changed volume: {command}")
        return result

    def take_screenshot(self, output_path="screenshot.png"):
        """
        Take a screenshot and save it to the specified path
        :param output_path: Path to save the screenshot
        """
        remote_path = "/sdcard/screenshot.png"
        self.execute_adb_command(f"screencap -p {remote_path}")

        # Pull the screenshot from the device
        if self.device_id:
            pull_command = f"{self.adb_path} -s {self.device_id} pull {remote_path} {output_path}"
        else:
            pull_command = f"{self.adb_path} pull {remote_path} {output_path}"

        subprocess.run(pull_command, shell=True)
        logger.info(f"Screenshot saved to {output_path}")
        return output_path

    def clear_app_data(self, package_name):
        """
        Clear data for a specific app
        :param package_name: Package name of the app
        """
        command = f"pm clear {package_name}"
        result = self.execute_adb_command(command)
        logger.info(f"Cleared data for {package_name}")
        return result

    def get_focused_app(self):
        """Get the currently focused app/activity"""
        command = "dumpsys window | grep mCurrentFocus"
        result = self.execute_adb_command(command)
        logger.info(f"Current focus: {result}")
        return result

    def press_back(self):
        """Press the back button"""
        command = "input keyevent 4"  # KEYCODE_BACK
        self.execute_adb_command(command)
        logger.info("Pressed back button")

    def press_home(self):
        """Press the home button"""
        command = "input keyevent 3"  # KEYCODE_HOME
        self.execute_adb_command(command)
        logger.info("Pressed home button")

    def press_menu(self):
        """Press the menu button"""
        command = "input keyevent 82"  # KEYCODE_MENU
        self.execute_adb_command(command)
        logger.info("Pressed menu button")

    def toggle_car_mode(self, enable=True):
        """
        Toggle car mode on/off
        :param enable: True to enable car mode, False to disable
        """
        state = "enable" if enable else "disable"
        command = f"settings put secure ui_night_mode {1 if enable else 0}"
        self.execute_adb_command(command)
        logger.info(f"Car mode {state}d")


if __name__ == "__main__":
    # Specify the device ID if multiple devices are connected
    screen_controller = AndroidClient(device_id="DEVICE_ID_HERE")
    screen_controller.click_coordinates(500, 500)  # Example: Click at (500, 500)
    screen_controller.swipe(100, 100, 400, 400)  # Example: Swipe from (100, 100) to (400, 400)
    screen_controller.long_press(300, 300)  # Example: Long press at (300, 300)
    screen_controller.multi_touch([(100, 100), (200, 200), (300, 300)])  # Example: Multi-touch gesture
    screen_controller.get_screen_dimensions()  # Example: Retrieve screen dimensions
    screen_controller.click_text("Settings")  # Example: Click on text "Settings"
    screen_controller.input_text("Hello World")  # Example: Input text "Hello World"

    """
    How to find the current focused activity?
    adb shell dumpsys window | findstr "mCurrentFocus mFocusedApp"
    >>  mCurrentFocus=Window{4adcfc2 u10 com.ecarx.hud/com.ecarx.hud.view.MainActivity}
    >>  mFocusedApp=ActivityRecord{5a41581 u10 com.ecarx.hud/.view.MainActivity t1000479}
    >>  mCurrentFocus=Window{f437091 u10 com.flyme.auto.update/com.flyme.auto.update.UpdateMainActivity}
    >>  mFocusedApp=ActivityRecord{1334ba5 u10 com.flyme.auto.update/.UpdateMainActivity t1000487}
    adb shell am start -n com.flyme.auto.update/.UpdateMainActivity
    """
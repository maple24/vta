import subprocess
from loguru import logger


class ADBController:
    def __init__(self, adb_path="adb", device_id=None):
        """
        Initialize the ScreenController class.
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


if __name__ == "__main__":
    # Specify the device ID if multiple devices are connected
    screen_controller = ADBController(device_id="DEVICE_ID_HERE")
    screen_controller.click_coordinates(500, 500)  # Example: Click at (500, 500)
    screen_controller.swipe(100, 100, 400, 400)  # Example: Swipe from (100, 100) to (400, 400)
    screen_controller.long_press(300, 300)  # Example: Long press at (300, 300)
    screen_controller.multi_touch([(100, 100), (200, 200), (300, 300)])  # Example: Multi-touch gesture
    screen_controller.get_screen_dimensions()  # Example: Retrieve screen dimensions
    screen_controller.click_text("Settings")  # Example: Click on text "Settings"
    screen_controller.input_text("Hello World")  # Example: Input text "Hello World"
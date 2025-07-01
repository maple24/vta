import os
import time
import subprocess
from typing import Optional, Tuple, List
import uiautomator2 as u2
from loguru import logger

class DeviceClient:
    """Class operations to android w/ uiautomator2"""

    def __init__(self):
        self.adb_obj_container = {}
        logger.info(f"{self.__class__.__name__} initialized.")

    def _get_device(self, device_id: str) -> Optional[u2.Device]:
        device_id = (device_id or "").strip()
        if not device_id:
            logger.warning("No device id provided.")
            return None
        if device_id not in self.adb_obj_container:
            try:
                dev_obj = u2.connect(device_id)
                self.adb_obj_container[device_id] = dev_obj
                logger.info(f"Connected to device '{device_id}'.")
            except Exception as e:
                logger.error(f"Failed to connect to device '{device_id}': {e}")
                return None
        return self.adb_obj_container[device_id]

    def connect(self, device_id: str) -> bool:
        device_id = device_id.strip()
        try:
            dev_obj = u2.connect(device_id)
            self.adb_obj_container[device_id] = dev_obj
            logger.info(f"Connected to device '{device_id}'.")
            return True
        except Exception as e:
            logger.error(f"Error connecting to device '{device_id}': {e}")
            return False

    def install_apk(self, device_id: str, apk_path: str) -> bool:
        if not os.path.exists(apk_path):
            logger.error(f"APK not found: {apk_path}")
            return False
        dev = self._get_device(device_id)
        if not dev:
            return False
        try:
            dev.app_install(apk_path)
            logger.info(f"Installed APK: {apk_path}")
            return True
        except Exception as e:
            logger.error(f"Error installing APK: {e}")
            return False

    def get_screendump(self, device_id: str, out_path: str) -> bool:
        dev = self._get_device(device_id)
        if not dev:
            return False
        try:
            dev.screenshot(out_path)
            logger.info(f"Screenshot saved to {out_path}")
            return True
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return False

    def get_view_info(self, device_id: str) -> Tuple[bool, List[str]]:
        dev = self._get_device(device_id)
        if not dev:
            return False, []
        try:
            info = dev.info
            pkg = info.get("currentPackageName", "")
            activity = info.get("currentActivity", "")
            logger.info(f"pkg='{pkg}', activity='{activity}'")
            return True, [pkg, activity]
        except Exception as e:
            logger.error(f"Error getting view info: {e}")
            return False, []

    def push_file(self, device_id: str, file_path: str, remote_path: str) -> bool:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
        dev = self._get_device(device_id)
        if not dev:
            return False
        try:
            dev.push(file_path, remote_path)
            logger.info(f"Pushed {file_path} to {remote_path}")
            return True
        except Exception as e:
            logger.error(f"Error pushing file: {e}")
            return False

    def turn_on_off_screen(self, device_id: str, operation: str = "on") -> bool:
        dev = self._get_device(device_id)
        if not dev:
            return False
        try:
            if operation.lower() == "on":
                dev.screen_on()
            elif operation.lower() == "off":
                dev.screen_off()
            else:
                logger.error(f"Unknown operation: {operation}")
                return False
            logger.info(f"Set device '{device_id}' screen to '{operation}'")
            return True
        except Exception as e:
            logger.error(f"Error turning screen {operation}: {e}")
            return False

    def press_key(self, device_id: str, keyname: str, delaytime: int = 1) -> bool:
        dev = self._get_device(device_id)
        if not dev:
            return False
        try:
            dev.press(keyname)
            logger.info(f"Pressed key '{keyname}' on {device_id}")
            time.sleep(delaytime)
            return True
        except Exception as e:
            logger.error(f"Error pressing key: {e}")
            return False

    def click_xy(self, device_id: str, x: int, y: int, delaytime: int = 1) -> bool:
        dev = self._get_device(device_id)
        if not dev:
            return False
        try:
            dev.click(int(x), int(y))
            logger.info(f"Clicked at ({x},{y}) on {device_id}")
            time.sleep(delaytime)
            return True
        except Exception as e:
            logger.error(f"Error clicking at ({x},{y}): {e}")
            return False

    def double_click_xy(self, device_id: str, x: int, y: int, click_duration: float = 0.1, delaytime: int = 1) -> bool:
        dev = self._get_device(device_id)
        if not dev:
            return False
        try:
            dev.double_click(x, y, click_duration)
            logger.info(f"Double clicked at ({x},{y}) with duration {click_duration} on {device_id}")
            time.sleep(delaytime)
            return True
        except Exception as e:
            logger.error(f"Error double clicking at ({x},{y}): {e}")
            return False

    def long_click_xy(self, device_id: str, x: int, y: int, click_duration: int = 1, delaytime: int = 1) -> bool:
        dev = self._get_device(device_id)
        if not dev:
            return False
        try:
            dev.long_click(x, y, click_duration)
            logger.info(f"Long clicked at ({x},{y}) with duration {click_duration} on {device_id}")
            time.sleep(delaytime)
            return True
        except Exception as e:
            logger.error(f"Error long clicking at ({x},{y}): {e}")
            return False

    def swipe_ext(self, device_id: str, cmd: str, delaytime: int = 1) -> bool:
        dev = self._get_device(device_id)
        if not dev:
            return False
        try:
            dev.swipe_ext(cmd)
            logger.info(f"Swiped {cmd} on {device_id}")
            time.sleep(delaytime)
            return True
        except Exception as e:
            logger.error(f"Error swiping {cmd}: {e}")
            return False

    def swipe_xy(self, device_id: str, x1: int, y1: int, x2: int, y2: int, swipe_time: float = 0.1, delaytime: int = 1) -> bool:
        dev = self._get_device(device_id)
        if not dev:
            return False
        try:
            dev.swipe(int(x1), int(y1), int(x2), int(y2), swipe_time)
            logger.info(f"Swiped from ({x1},{y1}) to ({x2},{y2}) on {device_id}")
            time.sleep(delaytime)
            return True
        except Exception as e:
            logger.error(f"Error swiping from ({x1},{y1}) to ({x2},{y2}): {e}")
            return False

    def swipe_to_find_text(self, device_id: str, text_to_find: str, swipe_method: str = "swipe_ext", cmd: str = "up", xy: list = [], max_retrial: int = 10) -> bool:
        dev = self._get_device(device_id)
        if not dev:
            return False
        for i in range(max_retrial):
            if dev(text=text_to_find).exists:
                logger.info(f"Found text '{text_to_find}' after {i} swipes.")
                return True
            logger.info(f"Text '{text_to_find}' not found, swiping {cmd} (attempt {i+1})")
            if swipe_method == "swipe_ext":
                self.swipe_ext(device_id, cmd, delaytime=1)
            elif swipe_method == "swipe_xy" and len(xy) == 4:
                self.swipe_xy(device_id, xy[0], xy[1], xy[2], xy[3], swipe_time=1, delaytime=1)
            else:
                logger.error(f"Unknown swipe method or invalid xy: {swipe_method}, {xy}")
                return False
        logger.warning(f"Text '{text_to_find}' not found after {max_retrial} swipes.")
        return False

    def get_ui_hierarchy(self, device_id: str, out_path: str) -> Tuple[bool, Optional[str]]:
        dev = self._get_device(device_id)
        if not dev:
            return False, None
        try:
            xml_content = dev.dump_hierarchy()
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(xml_content)
            logger.info(f"UI hierarchy saved to {out_path}")
            return True, out_path
        except Exception as e:
            logger.error(f"Error dumping UI hierarchy: {e}")
            return False, None

    def unlock(self, device_id: str) -> bool:
        dev = self._get_device(device_id)
        if not dev:
            return False
        try:
            dev.unlock()
            logger.info(f"Device '{device_id}' unlocked.")
            return True
        except Exception as e:
            logger.error(f"Error unlocking device: {e}")
            return False

    def set_shell(self, device_id: str, cmd: str, timeout: int = 5, log_print: bool = True, delaytime: int = 1) -> Tuple[bool, Optional[str]]:
        dev = self._get_device(device_id)
        if not dev:
            return False, None
        try:
            out, exit_code = dev.shell(cmd, stream=False, timeout=timeout)
            if log_print:
                logger.info(f"Shell command '{cmd}' result: {out}")
            time.sleep(delaytime)
            return True, out
        except Exception as e:
            logger.error(f"Error running shell command: {e}")
            return False, None

    def logcat_capturer(self, device_id: str, file_path: str, timeout: int = 60, print2console: bool = False) -> bool:
        dev = self._get_device(device_id)
        if not dev:
            return False
        if os.path.isdir(file_path):
            file_path = os.path.join(file_path, "logcat.log")
        if os.path.exists(file_path):
            os.remove(file_path)
        r = dev.shell("logcat -b all", stream=True)
        deadline = time.time() + timeout
        try:
            for line in r.iter_lines():
                if time.time() > deadline:
                    break
                try:
                    line = line.decode('utf-8', errors='ignore')
                except Exception as err:
                    line = line[:err.start].decode('utf-8', errors='ignore')
                with open(file_path, 'ab+') as f:
                    text = line + "\n"
                    f.write(text.encode('utf-8'))
                    f.flush()
                if print2console:
                    logger.info(f"logcat: {line}")
            logger.info(f"Logcat captured to {file_path}")
            return True
        except Exception as err:
            logger.error(f"Error! Logcat capturer !\n{err}")
            return False
        finally:
            r.close()

    def click_item(self, device_id: str, item_type: str = "text", options: list = []) -> bool:
        dev = self._get_device(device_id)
        if not dev or not options:
            logger.error("Device not found or options empty.")
            return False
        item_type = item_type.lower()
        try:
            for idx, opt in enumerate(options):
                if item_type == "text" and dev(text=opt).exists:
                    dev(text=opt).click()
                    logger.info(f"Clicked text '{opt}'")
                    return True
                elif item_type == "description" and dev(description=opt).exists:
                    dev(description=opt).click()
                    logger.info(f"Clicked description '{opt}'")
                    return True
                elif item_type in ("resource_id", "res_id") and dev(resourceId=opt).exists:
                    dev(resourceId=opt).click()
                    logger.info(f"Clicked resourceId '{opt}'")
                    return True
                elif item_type in ("class_name", "classname") and dev(className=opt).exists:
                    dev(className=opt).click()
                    logger.info(f"Clicked className '{opt}'")
                    return True
            logger.warning(f"No {item_type} found in options {options}")
            return False
        except Exception as e:
            logger.error(f"Error in click_item: {e}")
            return False

    def click_text(self, device_id: str, text: str, exists_timeout: int = 2, delaytime: int = 2) -> bool:
        dev = self._get_device(device_id)
        if not dev or not text:
            logger.error("Device not found or text not provided.")
            return False
        try:
            result = dev(text=text).click_exists(timeout=exists_timeout)
            if result:
                logger.info(f"Clicked text '{text}' on device '{device_id}'")
            else:
                logger.info(f"Text '{text}' not found on device '{device_id}'")
            time.sleep(delaytime)
            return result
        except Exception as e:
            logger.error(f"Error in click_text: {e}")
            return False

    def click_resource_id(self, device_id: str, resid: str, delaytime: int = 2) -> bool:
        dev = self._get_device(device_id)
        if not dev or not resid:
            logger.error("Device not found or resource id not provided.")
            return False
        try:
            if dev(resourceId=resid).exists:
                result = dev(resourceId=resid).click_exists(timeout=2)
                logger.info(f"Clicked resourceId '{resid}' on device '{device_id}'")
                time.sleep(delaytime)
                return result
            else:
                logger.warning(f"ResourceId '{resid}' not found on device '{device_id}'")
                return False
        except Exception as e:
            logger.error(f"Error in click_resource_id: {e}")
            return False

    def click_class_name(self, device_id: str, class_name: str, delaytime: int = 2) -> bool:
        dev = self._get_device(device_id)
        if not dev or not class_name:
            logger.error("Device not found or class name not provided.")
            return False
        try:
            if dev(className=class_name).exists:
                result = dev(className=class_name).click_exists(timeout=2)
                logger.info(f"Clicked className '{class_name}' on device '{device_id}'")
                time.sleep(delaytime)
                return result
            else:
                logger.warning(f"ClassName '{class_name}' not found on device '{device_id}'")
                return False
        except Exception as e:
            logger.error(f"Error in click_class_name: {e}")
            return False

    def click_description(self, device_id: str, text: str, delaytime: int = 2) -> bool:
        dev = self._get_device(device_id)
        if not dev or not text:
            logger.error("Device not found or description not provided.")
            return False
        try:
            if dev(description=text).exists:
                result = dev(description=text).click_exists(timeout=2)
                logger.info(f"Clicked description '{text}' on device '{device_id}'")
                time.sleep(delaytime)
                return result
            else:
                logger.warning(f"Description '{text}' not found on device '{device_id}'")
                return False
        except Exception as e:
            logger.error(f"Error in click_description: {e}")
            return False

    def click_xpath(self, device_id: str, str_xpath: str, delaytime: int = 2) -> bool:
        dev = self._get_device(device_id)
        if not dev or not str_xpath:
            logger.error("Device not found or xpath not provided.")
            return False
        try:
            if dev.xpath(str_xpath).exists:
                result = dev.xpath(str_xpath).click_exists()
                logger.info(f"Clicked xpath '{str_xpath}' on device '{device_id}'")
                time.sleep(delaytime)
                return result
            else:
                logger.warning(f"XPath '{str_xpath}' not found on device '{device_id}'")
                return False
        except Exception as e:
            logger.error(f"Error in click_xpath: {e}")
            return False

    def click_index(self, device_id: str, index: int = 0) -> bool:
        dev = self._get_device(device_id)
        if not dev:
            logger.error("Device not found.")
            return False
        try:
            result = dev(index=index).click()
            logger.info(f"Clicked index '{index}' on device '{device_id}'")
            return result
        except Exception as e:
            logger.error(f"Error in click_index: {e}")
            return False

    def check_resource_id_exists(self, device_id: str, resid: str) -> bool:
        dev = self._get_device(device_id)
        if not dev or not resid:
            logger.error("Device not found or resource id not provided.")
            return False
        try:
            exists = dev(resourceId=resid).exists
            logger.info(f"ResourceId '{resid}' exists: {exists}")
            return exists
        except Exception as e:
            logger.error(f"Error checking resource id existence: {e}")
            return False

    def check_text_exists(self, device_id: str, text: str) -> bool:
        dev = self._get_device(device_id)
        if not dev or not text:
            logger.error("Device not found or text not provided.")
            return False
        try:
            exists = dev(text=text).exists
            logger.info(f"Text '{text}' exists: {exists}")
            return exists
        except Exception as e:
            logger.error(f"Error checking text existence: {e}")
            return False

    def get_widget_text(self, device_id: str, text_wd: Optional[str] = None, resid: Optional[str] = None) -> Tuple[bool, str]:
        dev = self._get_device(device_id)
        if not dev:
            logger.error("Device not found.")
            return False, ""
        try:
            if resid:
                context = dev(resourceId=resid).get_text()
                logger.info(f"Got text from resourceId '{resid}': {context}")
            elif text_wd:
                context = dev(text=text_wd).get_text()
                logger.info(f"Got text from text widget '{text_wd}': {context}")
            else:
                logger.error("No text or resourceId provided.")
                return False, ""
            return True, context
        except Exception as e:
            logger.error(f"Error getting widget text: {e}")
            return False, ""

    def set_widget_text(self, device_id: str, resid: str, text_to_set: str = "", delaytime: int = 2) -> bool:
        dev = self._get_device(device_id)
        if not dev or not resid:
            logger.error("Device not found or resource id not provided.")
            return False
        try:
            dev(resourceId=resid).set_text(text_to_set)
            logger.info(f"Set text '{text_to_set}' for resourceId '{resid}'")
            time.sleep(delaytime)
            return True
        except Exception as e:
            logger.error(f"Error setting widget text: {e}")
            return False

    def check_widget_value(self, device_id: str, resid: str, exp_val: str = "", min_val: str = "", max_val: str = "") -> bool:
        dev = self._get_device(device_id)
        if not dev or not resid:
            logger.error("Device not found or resource id not provided.")
            return False
        try:
            ok, str_content = self.get_widget_text(device_id, resid=resid)
            if not ok:
                logger.error(f"Failed to get text from widget '{resid}'")
                return False
            if exp_val:
                if str_content.strip() == exp_val.strip():
                    logger.info(f"Found expected string '{exp_val}'")
                    return True
                else:
                    logger.info(f"Not found expected, but found '{str_content}'")
                    return False
            else:
                if min_val == "" or max_val == "":
                    logger.error("Parameter 'min_val' or 'max_val' invalid!")
                    return False
                min_val_f = float(min_val)
                max_val_f = float(max_val)
                real_val = float(str_content.strip().replace(",", "."))
                if min_val_f <= real_val <= max_val_f:
                    logger.info(f"Found value {real_val} inside the range between {min_val_f} and {max_val_f}")
                    return True
                else:
                    logger.info(f"Found value {real_val} outside range {min_val_f} ~ {max_val_f}")
                    return False
        except Exception as e:
            logger.error(f"Error checking widget value: {e}")
            return False

    def scroll_to_find_text(self, device_id: str, text_to_find: str, recover_resid: str, max_retrial: int = 10) -> bool:
        dev = self._get_device(device_id)
        if not dev:
            logger.error("Device not found.")
            return False
        for i in range(max_retrial):
            if dev(text=text_to_find).exists:
                logger.info(f"Found text '{text_to_find}' after {i} scrolls.")
                return True
            logger.info(f"Text '{text_to_find}' not found, pressing '{recover_resid}' (attempt {i+1})")
            self.click_resource_id(device_id, resid=recover_resid, delaytime=2)
        logger.warning(f"Text '{text_to_find}' not found after {max_retrial} scrolls.")
        return False

    def set_shell_and_fetch_trace(self, device_id: str, scmd: str, max_timeout: int = 10, end_trace: str = "\n") -> Tuple[bool, List[str]]:
        logger.info(f"Sending shell cmd: {scmd}")
        p = subprocess.Popen(f"adb -s {device_id} shell", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        p.stdin.write(f"{scmd}\n".encode('utf-8'))
        p.stdin.flush()
        time.sleep(2)
        start_time = time.time()
        shell_trace = []
        while True:
            if time.time() - start_time > max_timeout:
                logger.info("Timeout for shell cmd, return trace!")
                break
            out = p.stdout.readline()
            out = out.decode('utf-8').strip()
            if not out:
                continue
            if end_trace in out:
                logger.info(f"Found trace {end_trace}, return")
                return True, shell_trace
            shell_trace.append(out)
        return False, shell_trace
    
    def disconnect(self, device_id: str):
        """Remove the device from the container (optional cleanup)."""
        if device_id in self.adb_obj_container:
            del self.adb_obj_container[device_id]
            logger.info(f"Disconnected device '{device_id}'.")


if __name__ == '__main__':
    # Initialize the client
    client = DeviceClient()

    # Device ID (replace with your actual device serial)
    device_id = "2801750c52300030"

    # Connect to device
    if client.connect(device_id):
        print("Connected!")

    # Install an APK
    # apk_path = r"C:\path\to\your.apk"
    # if client.install_apk(device_id, apk_path):
    #     print("APK installed.")

    # Take a screenshot
    # if client.get_screendump(device_id, r"C:\tmp\screenshot.png"):
    #     print("Screenshot saved.")

    # # Get current package and activity
    # ok, info = client.get_view_info(device_id)
    # if ok:
    #     print("Current package:", info[0])
    #     print("Current activity:", info[1])

    # # Push a file to device
    # if client.push_file(device_id, r"C:\tmp\file.txt", "/sdcard/file.txt"):
    #     print("File pushed.")

    # # Turn screen on
    # client.turn_on_off_screen(device_id, "on")

    # # Press the HOME key
    # client.press_key(device_id, "home")

    # # Click at coordinates (100, 200)
    # client.click_xy(device_id, 100, 200)

    # # Double click at coordinates (100, 200)
    # client.double_click_xy(device_id, 100, 200)

    # # Long click at coordinates (100, 200)
    # client.long_click_xy(device_id, 100, 200)

    # # Swipe up
    # client.swipe_ext(device_id, "up")

    # # Swipe from (100,200) to (300,400)
    # client.swipe_xy(device_id, 100, 200, 300, 400)

    # # Swipe to find text
    # client.swipe_to_find_text(device_id, "Settings")

    # # Dump UI hierarchy to file
    # ok, path = client.get_ui_hierarchy(device_id, r"C:\tmp\ui.xml")
    # if ok:
    #     print("UI hierarchy saved to:", path)

    # # Unlock device
    # client.unlock(device_id)

    # # Run a shell command
    # ok, output = client.set_shell(device_id, "ls /sdcard")
    # if ok:
    #     print("Shell output:", output)

    # # Capture logcat
    # client.logcat_capturer(device_id, r"C:\tmp\logcat.log", timeout=10)

    # Click a UI element by text
    # client.click_text(device_id, "OK")

    # # Click a UI element by resource id
    # client.click_resource_id(device_id, "com.example:id/button1")

    # Check if text exists
    if client.check_text_exists(device_id, "Welcome"):
        print("Text found!")

    # # Set text in a widget
    # client.set_widget_text(device_id, "com.example:id/input", "Hello World")

    # # Get text from a widget
    # ok, text = client.get_widget_text(device_id, resid="com.example:id/input")
    # if ok:
    #     print("Widget text:", text)
import os
import time
import subprocess
from typing import Optional, Tuple, List, Callable, Any
import uiautomator2 as u2
from loguru import logger


def _with_device(func: Callable) -> Callable:
    """
    Decorator to automatically get a device instance based on device_id.
    If the device cannot be fetched, the function returns a failure value:
     - For methods starting with "get_" or returning a tuple, returns (False, None) or (False, [])
     - Otherwise returns False.
    """

    def wrapper(self, device_id: str, *args, **kwargs) -> Any:
        dev = self._get_device(device_id)
        if not dev:
            # Determine error return type based on function name
            if func.__name__.startswith("get_"):
                return False, None
            elif func.__name__ in ("get_view_info",):
                return False, []
            else:
                return False
        try:
            return func(self, dev, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            # Match return based on type of expected result.
            if func.__name__.startswith("get_"):
                return False, None
            elif func.__name__ in ("get_view_info",):
                return False, []
            else:
                return False

    return wrapper


class AndroidAutomator:
    """Class operations to control Android via uiautomator2."""

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

    @_with_device
    def install_apk(self, dev: u2.Device, apk_path: str) -> bool:
        if not os.path.exists(apk_path):
            logger.error(f"APK not found: {apk_path}")
            return False
        try:
            dev.app_install(apk_path)
            logger.info(f"Installed APK: {apk_path}")
            return True
        except Exception as e:
            logger.error(f"Error installing APK: {e}")
            return False

    @_with_device
    def get_screendump(self, dev: u2.Device, out_path: str) -> bool:
        try:
            dev.screenshot(out_path)
            logger.info(f"Screenshot saved to {out_path}")
            return True
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return False

    @_with_device
    def get_view_info(self, dev: u2.Device) -> Tuple[bool, List[str]]:
        try:
            info = dev.info
            pkg = info.get("currentPackageName", "")
            activity = info.get("currentActivity", "")
            logger.info(f"pkg='{pkg}', activity='{activity}'")
            return True, [pkg, activity]
        except Exception as e:
            logger.error(f"Error getting view info: {e}")
            return False, []

    @_with_device
    def push_file(self, dev: u2.Device, file_path: str, remote_path: str) -> bool:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
        try:
            dev.push(file_path, remote_path)
            logger.info(f"Pushed {file_path} to {remote_path}")
            return True
        except Exception as e:
            logger.error(f"Error pushing file: {e}")
            return False

    @_with_device
    def turn_on_off_screen(self, dev: u2.Device, operation: str = "on") -> bool:
        try:
            op = operation.lower()
            if op == "on":
                dev.screen_on()
            elif op == "off":
                dev.screen_off()
            else:
                logger.error(f"Unknown operation: {operation}")
                return False
            logger.info(f"Set device screen to '{operation}'")
            return True
        except Exception as e:
            logger.error(f"Error turning screen {operation}: {e}")
            return False

    @_with_device
    def press_key(self, dev: u2.Device, keyname: str, delaytime: int = 1) -> bool:
        try:
            dev.press(keyname)
            logger.info(f"Pressed key '{keyname}'")
            time.sleep(delaytime)
            return True
        except Exception as e:
            logger.error(f"Error pressing key: {e}")
            return False

    @_with_device
    def click_xy(self, dev: u2.Device, x: int, y: int, delaytime: int = 1) -> bool:
        try:
            dev.click(int(x), int(y))
            logger.info(f"Clicked at ({x},{y})")
            time.sleep(delaytime)
            return True
        except Exception as e:
            logger.error(f"Error clicking at ({x},{y}): {e}")
            return False

    @_with_device
    def double_click_xy(self, dev: u2.Device, x: int, y: int, click_duration: float = 0.1, delaytime: int = 1) -> bool:
        try:
            dev.double_click(x, y, click_duration)
            logger.info(f"Double clicked at ({x},{y}) with duration {click_duration}")
            time.sleep(delaytime)
            return True
        except Exception as e:
            logger.error(f"Error double clicking at ({x},{y}): {e}")
            return False

    @_with_device
    def long_click_xy(self, dev: u2.Device, x: int, y: int, click_duration: int = 1, delaytime: int = 1) -> bool:
        try:
            dev.long_click(x, y, click_duration)
            logger.info(f"Long clicked at ({x},{y}) with duration {click_duration}")
            time.sleep(delaytime)
            return True
        except Exception as e:
            logger.error(f"Error long clicking at ({x},{y}): {e}")
            return False

    @_with_device
    def swipe_ext(self, dev: u2.Device, cmd: str, delaytime: int = 1) -> bool:
        try:
            dev.swipe_ext(cmd)
            logger.info(f"Swiped {cmd}")
            time.sleep(delaytime)
            return True
        except Exception as e:
            logger.error(f"Error swiping {cmd}: {e}")
            return False

    @_with_device
    def swipe_xy(
        self, dev: u2.Device, x1: int, y1: int, x2: int, y2: int, swipe_time: float = 0.1, delaytime: int = 1
    ) -> bool:
        try:
            dev.swipe(int(x1), int(y1), int(x2), int(y2), swipe_time)
            logger.info(f"Swiped from ({x1},{y1}) to ({x2},{y2})")
            time.sleep(delaytime)
            return True
        except Exception as e:
            logger.error(f"Error swiping from ({x1},{y1}) to ({x2},{y2}): {e}")
            return False

    @_with_device
    def swipe_to_find_text(
        self,
        dev: u2.Device,
        text_to_find: str,
        swipe_method: str = "swipe_ext",
        cmd: str = "up",
        xy: list = [],
        max_retrial: int = 10,
    ) -> bool:
        for i in range(max_retrial):
            if dev(text=text_to_find).exists:
                logger.info(f"Found text '{text_to_find}' after {i} swipes.")
                return True
            logger.info(f"Text '{text_to_find}' not found, swiping {cmd} (attempt {i + 1})")
            if swipe_method == "swipe_ext":
                self.swipe_ext(dev, cmd, delaytime=1)
            elif swipe_method == "swipe_xy" and len(xy) == 4:
                self.swipe_xy(dev, xy[0], xy[1], xy[2], xy[3], swipe_time=1, delaytime=1)
            else:
                logger.error(f"Unknown swipe method or invalid xy: {swipe_method}, {xy}")
                return False
        logger.warning(f"Text '{text_to_find}' not found after {max_retrial} swipes.")
        return False

    @_with_device
    def get_ui_hierarchy(self, dev: u2.Device, out_path: str) -> Tuple[bool, Optional[str]]:
        try:
            xml_content = dev.dump_hierarchy()
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(xml_content)
            logger.info(f"UI hierarchy saved to {out_path}")
            return True, out_path
        except Exception as e:
            logger.error(f"Error dumping UI hierarchy: {e}")
            return False, None

    @_with_device
    def unlock(self, dev: u2.Device) -> bool:
        try:
            dev.unlock()
            logger.info("Device unlocked.")
            return True
        except Exception as e:
            logger.error(f"Error unlocking device: {e}")
            return False

    @_with_device
    def set_shell(
        self, dev: u2.Device, cmd: str, timeout: int = 5, log_print: bool = True, delaytime: int = 1
    ) -> Tuple[bool, Optional[str]]:
        try:
            out, exit_code = dev.shell(cmd, stream=False, timeout=timeout)
            if log_print:
                logger.info(f"Shell command '{cmd}' result: {out}")
            time.sleep(delaytime)
            return True, out
        except Exception as e:
            logger.error(f"Error running shell command: {e}")
            return False, None

    @_with_device
    def logcat_capturer(self, dev: u2.Device, file_path: str, timeout: int = 60, print2console: bool = False) -> bool:
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
                    line = line.decode("utf-8", errors="ignore")
                except Exception as err:
                    line = line[: err.start].decode("utf-8", errors="ignore")
                with open(file_path, "ab+") as f:
                    text = line + "\n"
                    f.write(text.encode("utf-8"))
                    f.flush()
                if print2console:
                    logger.info(f"logcat: {line}")
            logger.info(f"Logcat captured to {file_path}")
            return True
        except Exception as err:
            logger.error(f"Error capturing logcat: {err}")
            return False
        finally:
            r.close()

    @_with_device
    def click_item(self, dev: u2.Device, item_type: str = "text", options: list = []) -> bool:
        if not options:
            logger.error("Options empty.")
            return False
        item_type = item_type.lower()
        try:
            for opt in options:
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

    @_with_device
    def click_text(self, dev: u2.Device, text: str, exists_timeout: int = 2, delaytime: int = 2) -> bool:
        if not text:
            logger.error("Text not provided.")
            return False
        try:
            result = dev(text=text).click_exists(timeout=exists_timeout)
            if result:
                logger.info(f"Clicked text '{text}'")
            else:
                logger.info(f"Text '{text}' not found")
            time.sleep(delaytime)
            return result
        except Exception as e:
            logger.error(f"Error in click_text: {e}")
            return False

    @_with_device
    def click_resource_id(self, dev: u2.Device, resid: str, delaytime: int = 2) -> bool:
        if not resid:
            logger.error("Resource id not provided.")
            return False
        try:
            if dev(resourceId=resid).exists:
                result = dev(resourceId=resid).click_exists(timeout=2)
                logger.info(f"Clicked resourceId '{resid}'")
                time.sleep(delaytime)
                return result
            else:
                logger.warning(f"ResourceId '{resid}' not found")
                return False
        except Exception as e:
            logger.error(f"Error in click_resource_id: {e}")
            return False

    @_with_device
    def click_class_name(self, dev: u2.Device, class_name: str, delaytime: int = 2) -> bool:
        if not class_name:
            logger.error("Class name not provided.")
            return False
        try:
            if dev(className=class_name).exists:
                result = dev(className=class_name).click_exists(timeout=2)
                logger.info(f"Clicked className '{class_name}'")
                time.sleep(delaytime)
                return result
            else:
                logger.warning(f"ClassName '{class_name}' not found")
                return False
        except Exception as e:
            logger.error(f"Error in click_class_name: {e}")
            return False

    @_with_device
    def click_description(self, dev: u2.Device, text: str, delaytime: int = 2) -> bool:
        if not text:
            logger.error("Description not provided.")
            return False
        try:
            if dev(description=text).exists:
                result = dev(description=text).click_exists(timeout=2)
                logger.info(f"Clicked description '{text}'")
                time.sleep(delaytime)
                return result
            else:
                logger.warning(f"Description '{text}' not found")
                return False
        except Exception as e:
            logger.error(f"Error in click_description: {e}")
            return False

    @_with_device
    def click_xpath(self, dev: u2.Device, str_xpath: str, delaytime: int = 2) -> bool:
        if not str_xpath:
            logger.error("XPath not provided.")
            return False
        try:
            if dev.xpath(str_xpath).exists:
                result = dev.xpath(str_xpath).click_exists()
                logger.info(f"Clicked xpath '{str_xpath}'")
                time.sleep(delaytime)
                return result
            else:
                logger.warning(f"XPath '{str_xpath}' not found")
                return False
        except Exception as e:
            logger.error(f"Error in click_xpath: {e}")
            return False

    @_with_device
    def click_index(self, dev: u2.Device, index: int = 0) -> bool:
        try:
            result = dev(index=index).click()
            logger.info(f"Clicked index '{index}'")
            return result
        except Exception as e:
            logger.error(f"Error in click_index: {e}")
            return False

    @_with_device
    def check_resource_id_exists(self, dev: u2.Device, resid: str) -> bool:
        if not resid:
            logger.error("Resource id not provided.")
            return False
        try:
            exists = dev(resourceId=resid).exists
            logger.info(f"ResourceId '{resid}' exists: {exists}")
            return exists
        except Exception as e:
            logger.error(f"Error checking resource id existence: {e}")
            return False

    @_with_device
    def check_text_exists(self, dev: u2.Device, text: str) -> bool:
        if not text:
            logger.error("Text not provided.")
            return False
        try:
            exists = dev(text=text).exists
            logger.info(f"Text '{text}' exists: {exists}")
            return exists
        except Exception as e:
            logger.error(f"Error checking text existence: {e}")
            return False

    @_with_device
    def get_widget_text(
        self, dev: u2.Device, text_wd: Optional[str] = None, resid: Optional[str] = None
    ) -> Tuple[bool, str]:
        if resid:
            try:
                context = dev(resourceId=resid).get_text()
                logger.info(f"Got text from resourceId '{resid}': {context}")
                return True, context
            except Exception as e:
                logger.error(f"Error getting text from resourceId '{resid}': {e}")
                return False, ""
        elif text_wd:
            try:
                context = dev(text=text_wd).get_text()
                logger.info(f"Got text from text widget '{text_wd}': {context}")
                return True, context
            except Exception as e:
                logger.error(f"Error getting text from text widget '{text_wd}': {e}")
                return False, ""
        else:
            logger.error("No text or resourceId provided.")
            return False, ""

    @_with_device
    def set_widget_text(self, dev: u2.Device, resid: str, text_to_set: str = "", delaytime: int = 2) -> bool:
        if not resid:
            logger.error("Resource id not provided.")
            return False
        try:
            dev(resourceId=resid).set_text(text_to_set)
            logger.info(f"Set text '{text_to_set}' for resourceId '{resid}'")
            time.sleep(delaytime)
            return True
        except Exception as e:
            logger.error(f"Error setting widget text: {e}")
            return False

    @_with_device
    def check_widget_value(
        self, dev: u2.Device, resid: str, exp_val: str = "", min_val: str = "", max_val: str = ""
    ) -> bool:
        if not resid:
            logger.error("Resource id not provided.")
            return False
        try:
            ok, str_content = self.get_widget_text(device_id="", resid=resid)
            if not ok:
                logger.error(f"Failed to get text from widget '{resid}'")
                return False
            if exp_val:
                if str_content.strip() == exp_val.strip():
                    logger.info(f"Found expected string '{exp_val}'")
                    return True
                else:
                    logger.info(f"Not found expected, but got '{str_content}'")
                    return False
            else:
                if min_val == "" or max_val == "":
                    logger.error("Parameter 'min_val' or 'max_val' invalid!")
                    return False
                min_val_f = float(min_val)
                max_val_f = float(max_val)
                real_val = float(str_content.strip().replace(",", "."))
                if min_val_f <= real_val <= max_val_f:
                    logger.info(f"Value {real_val} is within range {min_val_f} - {max_val_f}")
                    return True
                else:
                    logger.info(f"Value {real_val} is outside range {min_val_f} - {max_val_f}")
                    return False
        except Exception as e:
            logger.error(f"Error checking widget value: {e}")
            return False

    @_with_device
    def scroll_to_find_text(self, dev: u2.Device, text_to_find: str, recover_resid: str, max_retrial: int = 10) -> bool:
        try:
            for i in range(max_retrial):
                if dev(text=text_to_find).exists:
                    logger.info(f"Found text '{text_to_find}' after {i} scrolls.")
                    return True
                logger.info(f"Text '{text_to_find}' not found, pressing '{recover_resid}' (attempt {i + 1})")
                self.click_resource_id(device_id="", resid=recover_resid, delaytime=2)
            logger.warning(f"Text '{text_to_find}' not found after {max_retrial} scrolls.")
            return False
        except Exception as e:
            logger.error(f"Error in scroll_to_find_text: {e}")
            return False

    def set_shell_and_fetch_trace(
        self, device_id: str, scmd: str, max_timeout: int = 10, end_trace: str = "\n"
    ) -> Tuple[bool, List[str]]:
        logger.info(f"Sending shell cmd: {scmd}")
        p = subprocess.Popen(f"adb -s {device_id} shell", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        p.stdin.write(f"{scmd}\n".encode("utf-8"))
        p.stdin.flush()
        time.sleep(2)
        start_time = time.time()
        shell_trace = []
        while True:
            if time.time() - start_time > max_timeout:
                logger.info("Timeout for shell cmd, returning trace!")
                break
            out = p.stdout.readline()
            out = out.decode("utf-8").strip()
            if not out:
                continue
            if end_trace in out:
                logger.info(f"Found trace delimiter {end_trace}, returning trace")
                return True, shell_trace
            shell_trace.append(out)
        return False, shell_trace

    def disconnect(self, device_id: str):
        """Remove the device from the container (optional cleanup)."""
        if device_id in self.adb_obj_container:
            del self.adb_obj_container[device_id]
            logger.info(f"Disconnected device '{device_id}'.")


if __name__ == "__main__":
    # Initialize the client
    client = AndroidAutomator()
    device_id = "2801750c52300030"  # replace with your device serial

    if client.connect(device_id):
        print("Connected!")

    # Example usage:
    if client.check_text_exists(device_id, "Welcome"):
        print("Text found!")

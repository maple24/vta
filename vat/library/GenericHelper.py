import time
import psutil
import subprocess
from typing import Tuple, Optional
import re
from loguru import logger
import os
import socket
import win32api
import win32con
import win32file

ROOT = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-3])


class GenericHelper:
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self) -> None:
        self.ODiffBin = os.path.join(ROOT, "vat", "bin", "ODiffBin.exe")

    @staticmethod
    def get_hostname() -> str:
        return socket.gethostname()

    @staticmethod
    def get_username() -> str:
        return os.getlogin()

    @staticmethod
    def get_removable_drives() -> str:
        drives = [i for i in win32api.GetLogicalDriveStrings().split("\x00") if i]
        rdrives = [
            d for d in drives if win32file.GetDriveType(d) == win32con.DRIVE_REMOVABLE
        ]
        if len(rdrives) == 0:
            logger.error("No removable drives found!")
        return rdrives[0]

    @staticmethod
    def terminate(process: subprocess.Popen) -> None:
        parent = psutil.Process(process.pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
        if process.poll() is None:
            logger.info("Process is terminated.")
        else:
            logger.error("Fail to terminate process!")

    @staticmethod
    def prompt_command(cmd: str, timeout: float = 5.0) -> list:
        data = []
        start = time.time()
        logger.info("[{stream}] - {message}", stream="PromptTx", message=cmd)
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
        )
        out = process.stdout
        while time.time() - start < timeout:
            if process.poll() is not None:
                break
            line = out.readline().decode("utf-8").strip()
            if line:
                data.append(line)
                logger.debug("[{stream}] - {message}", stream="PromptRx", message=line)
        try:
            GenericHelper.terminate(process)
        except psutil.NoSuchProcess:
            logger.info("Process not exist.")
            pass
        return data

    @staticmethod
    def match_string(pattern: str, data: list) -> Tuple[bool, Optional[list]]:
        """
        match_string("(.+)\s+device\s+$", data)
        """
        matched = []
        for string in data:
            if type(string) == bytes:
                string = string.decode()
            match = re.search(pattern, string)
            if match:
                match_data = match.groups()
                logger.success(f"Regex matches: {match_data}")
                matched.append(match_data)
        if matched:
            return True, matched
        logger.warning(f"Not matched pattern {pattern}")
        return False, None

    def image_diff(
        self, image1: str, image2: str, output: Optional[str] = None, thre: float = 0.0
    ) -> Optional[bool]:
        if not os.path.exists(self.ODiffBin):
            logger.error(f"ODiffBin not found in {self.ODiffBin}!")
            return
        if not os.path.exists(image1) or not os.path.exists(image2):
            logger.error(f"Image not found!")
            return
        if output:
            cmd = f"{self.ODiffBin} {image1} {image2} {output}"
        else:
            cmd = f"{self.ODiffBin} {image1} {image2}"
        out = GenericHelper.prompt_command(cmd)
        result, _ = GenericHelper.match_string(pattern="(Success)", data=out)
        if result:
            logger.success(f"{image1} and {image2} are exactly the same!")
            return True
        result, diff = GenericHelper.match_string(
            pattern="Different pixels:\s.+\s\((.+)%\)", data=out
        )
        if result:
            diff_rate = round(float(diff[0][0]), 2)
            if diff_rate > thre:
                logger.info(
                    f"Image difference rate {diff_rate} is larger than threshold {thre}"
                )
                return False
            else:
                logger.info(
                    f"Image difference rate {diff_rate} is less than threshold {thre}"
                )
                return True


if __name__ == "__main__":
    # logger.info(GenericHelper.get_hostname())
    cmd = r"C:\Users\ZIU7WX\Desktop\doc\personal\project\rubbish\vat\vat\bin\ODiffBin.exe C:\Users\ZIU7WX\Desktop\doc\personal\project\rubbish\vat\tmp\3.png C:\Users\ZIU7WX\Desktop\doc\personal\project\rubbish\vat\tmp\4.png"
    # data = GenericHelper.prompt_command(cmd)
    # GenericHelper.match_string(pattern="Different pixels:\s.+\s\((.+)%\)", data=data)
    # GenericHelper.match_string(pattern='Different pixels:\s\d+\s\((.+)%\)', data=['Different pixels: 64526 (18.393065%)'])
    # print(re.search(pattern='Different pixels:\s.+\s\((.+)%\)', string='Different pixels: \x1b[1m\x1b[31m64526 (18.393065%)\x1b[22m\x1b[39m'))
    image1 = r"C:\Users\ZIU7WX\Desktop\doc\personal\project\rubbish\vat\tmp\4.png"
    image2 = r"C:\Users\ZIU7WX\Desktop\doc\personal\project\rubbish\vat\tmp\3.png"
    g = GenericHelper()
    a = g.image_diff(image1, image2)

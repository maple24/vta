import time
import psutil
import subprocess
from typing import Tuple, Optional
import re
from loguru import logger
import os
import socket
import serial
import win32api
import win32con
import win32file


class GenericHelper:
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

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
    def serial_command(
        cmd, comport: str, username="root", password="root", timeout=5.0
    ) -> list:
        with serial.Serial(comport, baudrate=115200, timeout=2) as ser:
            logger.info(f"Opening port {comport}...")
            ser.write("\n".encode())
            res = ser.readlines()
            if len(res) == 0:
                logger.error(f"Fail to open port {comport}!")
                exit(1)
            if GenericHelper.match_string("(login:.*)", res)[0]:
                logger.info(f"Enter username is {username}")
                ser.write((username + "\n").encode())
                if GenericHelper.match_string("(Password:.*)", ser.readlines())[0]:
                    logger.info(f"Enter password is {password}")
                    ser.write((password + "\n").encode())
                if not GenericHelper.match_string(
                    "(Logging in with home .*)", ser.readlines()
                )[0]:
                    logger.info("Fail to login!")
                    exit(1)
            logger.info("[{stream}] - {message}", stream="PuttyTx", message=cmd)
            if isinstance(cmd, list):
                for i in cmd:
                    ser.write((i + "\n").encode())
            else:
                ser.write((cmd + "\n").encode())
            data = []
            start = time.time()
            while time.time() - start < timeout:
                line = ser.readline().decode()
                if not line:
                    break
                data.append(line)
                logger.debug("[{stream}] - {message}", stream="PuttyRx", message=line)
            return data

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
                logger.info(f"Regex matches: {match_data}")
                matched.append(match_data)
        if matched:
            return True, matched
        logger.info(f"Not matched pattern {pattern}")
        return False, None


if __name__ == "__main__":
    logger.info(GenericHelper.get_hostname())

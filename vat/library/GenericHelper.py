import time
import psutil
import subprocess
from typing import Tuple, Optional
import re
from loguru import logger
import os
import socket


class GenericHelper:
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    @staticmethod
    def get_hostname():
        return socket.gethostname()

    @staticmethod
    def get_username():
        return os.getlogin()

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
                logger.trace("[{stream}] - {message}", stream="PromptRx", message=line)
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
                print("Regex matches: ", match_data)
                matched.append(match_data)
        if matched:
            return True, matched
        print("Not matched raw string:", data)
        return False, None


if __name__ == "__main__":
    print(GenericHelper.get_hostname())

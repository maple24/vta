import os
from typing import Optional
from loguru import logger
import time
import serial
from GenericHelper import GenericHelper


class SystemHelper:
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

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
    def get_adb_devices() -> Optional[list]:
        data = GenericHelper.prompt_command(cmd="adb devices")
        res, matched = GenericHelper.match_string("(.+)\s+device$", data)
        if not res:
            logger.warning("No adb devices found!")
            return False
        devices = [x[0] for x in matched]
        logger.info(f"Get adb devices list: {devices}")
        return devices

    @staticmethod
    def is_adb_available(deviceID: str = "1234567") -> bool:
        data = GenericHelper.prompt_command(cmd="adb devices")
        res, matched = GenericHelper.match_string("(.+)\s+device$", data)
        if not res:
            logger.warning("No adb devices found!")
            return False
        if deviceID in [x[0] for x in matched]:
            logger.success(f"ADB {deviceID} is available!")
            return True
        logger.error(f"ADB {deviceID} is not available!")
        return False

    @staticmethod
    def android_screencapture(
        deviceID: str = "1234567", name: str = "screencap", localPath: str = "."
    ) -> None:
        cmd = f"adb -s {deviceID} shell screencap -p /sdcard/{name}.png && adb pull /sdcard/{name}.png {localPath}"
        GenericHelper.prompt_command(cmd)

    @staticmethod
    def PC2Android(localPath: str, remotePath: str, deviceID: str = "1234567") -> None:
        if not SystemHelper.is_adb_available(deviceID):
            return
        cmd = f"adb -s {deviceID} push {localPath} {remotePath}"
        GenericHelper.prompt_command(cmd)

    @staticmethod
    def Android2PC(
        remotePath: str, localPath: str = ".", deviceID: str = "1234567"
    ) -> None:
        if not SystemHelper.is_adb_available(deviceID):
            return
        cmd = f"adb -s {deviceID} pull {remotePath} {localPath}"
        GenericHelper.prompt_command(cmd)

    @staticmethod
    def PC2QNX(
        comport: str,
        localPath: str,
        remotePath: Optional[str] = None,
        deviceID: str = "1234567",
        username: str = "root",
        password: str = "root",
    ) -> None:
        if not os.path.exists(localPath):
            logger.error("File does not exist in local PC!")
        filename = os.path.basename(localPath)
        remotePath = "/data/nfs/nfs_share"
        SystemHelper.PC2Android(localPath, remotePath, deviceID)
        if remotePath is not None:
            cmd = f"cp /data/share/{filename} {remotePath}"
            GenericHelper.serial_command(cmd, comport, username, password)

    @staticmethod
    def QNX2PC(
        comport: str,
        remotePath: str,
        localPath: str = ".",
        deviceID: str = "1234567",
        username: str = "root",
        password: str = "root",
    ) -> None:
        filename = remotePath.split("/")[-1]
        logger.info(f"Target file is {filename}")
        cmd = f"cp {remotePath} /data/share/"
        GenericHelper.serial_command(cmd, comport, username, password)
        remotePath = f"/data/nfs/nfs_share/{filename}"
        SystemHelper.Android2PC(localPath, remotePath, deviceID)


if __name__ == "__main__":
    SystemHelper.get_adb_devices()

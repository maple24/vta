import os
from typing import Optional
from loguru import logger
import time
import serial
from GenericHelper import GenericHelper


class SystemHelper:
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    disk_mapping = {"qnx": "/mnt/nfs_share", "android": "/data/vendor/nfs/mount"}

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
            return
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
        deviceID: str = "1234567", name: str = "screencap.png", localPath: str = "."
    ) -> str:
        cmd = f"adb -s {deviceID} shell screencap -p /sdcard/{name} && adb pull /sdcard/{name} {localPath}"
        GenericHelper.prompt_command(cmd)
        return os.path.join(localPath, name)

    @staticmethod
    def PC2Android(localPath: str, androidPath: str, deviceID: str = "1234567") -> None:
        if not SystemHelper.is_adb_available(deviceID):
            return
        GenericHelper.prompt_command(f"adb -s {deviceID} root")
        cmd = f"adb -s {deviceID} push {localPath} {androidPath}"
        GenericHelper.prompt_command(cmd)

    @staticmethod
    def Android2PC(
        androidPath: str, localPath: str = ".", deviceID: str = "1234567"
    ) -> None:
        if not SystemHelper.is_adb_available(deviceID):
            return
        GenericHelper.prompt_command(f"adb -s {deviceID} root")
        cmd = f"adb -s {deviceID} pull {androidPath} {localPath}"
        GenericHelper.prompt_command(cmd)

    @staticmethod
    def PC2QNX(
        comport: str,
        localPath: str,
        qnxPath: Optional[str] = None,
        deviceID: str = "1234567",
        username: str = "root",
        password: str = "root",
    ) -> None:
        if not os.path.exists(localPath):
            logger.error("File does not exist in local PC!")
        filename = os.path.basename(localPath)
        androidPath = SystemHelper.disk_mapping.get("android", "/data/nfs/nfs_share")
        SystemHelper.PC2Android(localPath, androidPath, deviceID)
        if qnxPath is not None:
            cmd = f"cp {os.path.join(SystemHelper.disk_mapping.get('qnx', '/data/share/'), filename)} {qnxPath}"
            SystemHelper.serial_command(cmd, comport, username, password)

    @staticmethod
    def QNX2PC(
        comport: str,
        qnxPath: str,
        localPath: str = ".",
        deviceID: str = "1234567",
        username: str = "root",
        password: str = "root",
    ) -> None:
        filename = os.path.basename(qnxPath)
        logger.info(f"Target file is {filename}")
        cmd = f"cp {qnxPath} {SystemHelper.disk_mapping.get('qnx', '/data/share/')}"
        SystemHelper.serial_command(cmd, comport, username, password)
        androidPath = os.path.join(
            SystemHelper.disk_mapping.get("android", "/data/nfs/nfs_share/"), filename
        )
        SystemHelper.Android2PC(androidPath, localPath, deviceID)


if __name__ == "__main__":
    SystemHelper.get_adb_devices()

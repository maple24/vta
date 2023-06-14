from typing import Optional
import os
from loguru import logger
from GenericHelper import GenericHelper


class FileManager:
    @staticmethod
    def list_files(path: str) -> list:
        if not os.path.exists(path):
            print("Path does not exist!")
            raise
        return os.listdir(path)

    @staticmethod
    def is_adb_available(deviceID: str = "1234567") -> bool:
        data = GenericHelper.prompt_command(cmd="adb devices")
        res, matched = GenericHelper.match_string("(.+)\s+device\s+$", data)
        if not res:
            logger.warning("No adb devices found!")
            return False
        if deviceID in matched:
            logger.success(f"ADB {deviceID} is available!")
            return True
        logger.error(f"ADB {deviceID} is not available!")
        return False

    @staticmethod
    def Android_screencapture(deviceID: str = "1234567", localPath: str = "."):
        cmd = f"adb -s {deviceID} shell screencap -p /sdcard/screencap.png && adb pull /sdcard/screencap.png {localPath}"
        GenericHelper.prompt_command(cmd)

    @staticmethod
    def PC2Android(localPath: str, remotePath: str, deviceID: str = "1234567") -> None:
        if not FileManager.is_adb_available(deviceID):
            return
        cmd = f"adb -s {deviceID} push {localPath} {remotePath}"
        GenericHelper.prompt_command(cmd)

    @staticmethod
    def Android2PC(
        remotePath: str, localPath: str = ".", deviceID: str = "1234567"
    ) -> None:
        if not FileManager.is_adb_available(deviceID):
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
        FileManager.PC2Android(localPath, remotePath, deviceID)
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
        FileManager.Android2PC(localPath, remotePath, deviceID)


if __name__ == "__main__":
    print(FileManager.list_files("."))
    FileManager.is_adb_available()

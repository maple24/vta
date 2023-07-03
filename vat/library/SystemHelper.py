import os
from typing import Optional
from loguru import logger
from GenericHelper import GenericHelper


class SystemHelper:
        
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
    def android_screencapture(deviceID: str = "1234567", name: str = 'screencap', localPath: str = ".") -> None:
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
        

if __name__ == '__main__':
    SystemHelper.get_adb_devices()
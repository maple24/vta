from typing import Optional, Tuple
import os
import shutil
from loguru import logger
from GenericHelper import GenericHelper


class FileManager:
    def copy_file(self, source: str, destination: str) -> None:
        try:
            logger.info("Start copying, Please wait...")
            shutil.copyfile(source, destination)
        except shutil.Error:
            logger.error("Shutil error!")
        except Exception as e:
            logger.error(f"Unexpected error {e}")
        else:
            logger.success(f"Copied file from {source} to {destination}.")

    def copy_directory(self, source: str, destination: str) -> None:
        source, destination = self._prepare_copy_and_move_directory(source, destination)
        try:
            shutil.copytree(source, destination)
        except shutil.Error:
            logger.error("Shutil error!")
        except Exception as e:
            logger.error(f"Unexpected error {e}")
        else:
            logger.success(f"Copied directory from {source} to {destination}.")

    def move_directory(self, source: str, destination: str) -> None:
        source, destination = self._prepare_copy_and_move_directory(source, destination)
        try:
            shutil.move(source, destination)
        except shutil.Error:
            logger.error("Shutil error!")
        except Exception as e:
            logger.error(f"Unexpected error {e}")
        else:
            logger.success(f"Moved directory from {source} to {destination}.")

    def _prepare_copy_and_move_directory(
        self, source: str, destination: str
    ) -> Tuple[str, str]:
        source = self._absnorm(source)
        destination = self._absnorm(destination)
        if not os.path.exists(source):
            logger.warning("Source '%s' does not exist." % source)
        if not os.path.isdir(source):
            logger.warning("Source '%s' is not a directory." % source)
        if os.path.exists(destination) and not os.path.isdir(destination):
            logger.warning("Destination '%s' is not a directory." % destination)
        if os.path.exists(destination):
            base = os.path.basename(source)
            destination = os.path.join(destination, base)
        else:
            parent = os.path.dirname(destination)
            if not os.path.exists(parent):
                os.makedirs(parent)
        return source, destination

    def _absnorm(self, path: str) -> str:
        path = self._normalize_path(path)
        try:
            return self._abspath(path)
        except ValueError:
            return path

    def _normalize_path(self, path: str, case_normalize: bool = False) -> str:
        path = os.path.normpath(os.path.expanduser(path.replace("/", os.sep)))
        if case_normalize:
            path = os.path.normcase(path)
        return path or "."

    def _abspath(self, path: str, case_normalize: bool = False) -> str:
        path = self._normpath(path, case_normalize)
        return path

    def _normpath(self, path: str, case_normalize: bool = False) -> str:
        path = os.path.normpath(path)
        if case_normalize:
            path = path.lower()
        if len(path) == 2 and path[1] == ":":
            return path + "\\"
        return path

    @staticmethod
    def list_files(path: str) -> list:
        if not os.path.exists(path):
            logger.error("Path does not exist!")
            return
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
    def Android_screencapture(deviceID: str = "1234567", localPath: str = ".") -> None:
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

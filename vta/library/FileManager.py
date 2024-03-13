# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

import os
import shutil
from typing import Tuple

from loguru import logger


class FileManager:
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

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


if __name__ == "__main__":
    print(FileManager.list_files("."))
    FileManager.is_adb_available()

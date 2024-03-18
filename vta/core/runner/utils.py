# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

import os
import shutil
import time
from pathlib import Path
from typing import Optional

from loguru import logger


def rotate_folder(folder_path: str, days: int = 7) -> None:
    current_time = time.time()
    days_in_seconds = days * 24 * 60 * 60

    for root, dirs, files in os.walk(folder_path):
        for directory in dirs:
            folder = os.path.join(root, directory)
            folder_time = os.path.getmtime(folder)

            if (current_time - folder_time) > days_in_seconds:
                # Delete the folder and its contents
                shutil.rmtree(folder)
                logger.warning(
                    f"Delete folder {folder} which is created `{days}days` ago!"
                )


def find_file(directory: Path, file_name: str) -> Optional[Path]:
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == file_name:
                return Path(root) / file_name
    return None


if __name__ == "__main__":
    folder_path = r"C:\Users\ZIU7WX\Desktop\doc\personal\project\rubbish\vta\log"

    rotate_folder(folder_path)

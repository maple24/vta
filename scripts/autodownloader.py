import sys
import os
import re
import shutil
import time
import schedule
from loguru import logger

sys.path.append(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2]))
from vta.api.ArtifaHelper import ArtifaHelper

mylogger = logger.add(
    os.path.join(os.path.dirname(__file__), "downloads.log"),
    backtrace=True,
    diagnose=False,
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    rotation="1 week",
    level="DEBUG",
)


def main(credentials, destination):
    autodownloader = ArtifaHelper(**credentials)
    api = "api/storage/" + credentials.get("repo")

    for file in autodownloader.get_all_files(api):
        uri = file["downloadUri"]
        filename = os.path.basename(uri)
        filepath = os.path.join(autodownloader.dstfolder, filename)
        if re.search(credentials.get("pattern"), uri):
            if not os.path.exists(os.path.join(destination, filename)):
                autodownloader.download(uri)
                try:
                    shutil.move(filepath, destination)
                except shutil.Error:
                    logger.exception("Shutil error!")
                except Exception as e:
                    logger.exception(f"Unexpected error {e}")
                else:
                    logger.success(f"Moved directory from {filepath} to {destination}.")
            else:
                logger.warning(f"File {filename} already exists.")


if __name__ == "__main__":
    destination = r"\\SZHVM00556.APAC.BOSCH.COM\01_Project\BinaryExchange\Zeekr\System test\Temp_Version"
    credentials = {
        "repo": "zeekr/8295_ZEEKR/daily_cx1e/",
        "pattern": "qfil_.*",
        "server": "https://hw-snc-jfrog-dmz.zeekrlife.com/artifactory/",
        "auth": ("bosch-gitauto", "Bosch-gitauto@123"),
        "multithread": True,
    }

    main(credentials, destination)
    schedule.every().hour.do(main, credentials, destination)

    while True:
        schedule.run_pending()
        time.sleep(1)

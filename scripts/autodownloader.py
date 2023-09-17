import sys
import os
import re
import shutil
import time
import schedule
from rich.console import Console
sys.path.append(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2]))
from vta.api.ArtifaHelper import ArtifaHelper
console = Console()

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
                    console.log("Shutil error!")
                except Exception as e:
                    console.log(f"Unexpected error {e}")
                else:
                    console.log(f"Moved directory from {filepath} to {destination}.")
            else:
                console.log(f"File {filename} already exists.")


if __name__ == '__main__':
    destination = r"\\SZHVM00556.APAC.BOSCH.COM\01_Project\BinaryExchange\Zeekr\System test\Temp_Version"
    credentials = {
        "repo":"zeekr/8295_ZEEKR/daily_cx1e/",
        "pattern":"qfil_.*",
        "server":"https://hw-snc-jfrog-dmz.zeekrlife.com/artifactory/",
        "auth":("bosch-gitauto", "Bosch-gitauto@123"),
        "multithread": True
    }

    main(credentials, destination)
    schedule.every().hour.do(main, credentials, destination)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

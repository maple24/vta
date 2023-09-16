import sys
import os
import re
from rich.console import Console
from rich.pretty import pprint
sys.path.append(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2]))
from vta.api.ArtifaHelper import ArtifaHelper
console = Console()

def is_file_exist(folder: str, filename: str) -> bool:
    if os.path.exists(os.path.join(folder, filename)):
        return True
    return False

if __name__ == '__main__':
    credentials = {
        "dstfolder": r"C:\Users\ZIU7WX\Desktop\doc\personal\project\rubbish\vta\downloads",
        "repo":"zeekr/8295_ZEEKR/daily_cx1e/",
        "pattern":"qfil_.*",
        "server":"https://hw-snc-jfrog-dmz.zeekrlife.com/artifactory/",
        "auth":("bosch-gitauto", "Bosch-gitauto@123"),
        "multithread": True
    }

    autodownloader = ArtifaHelper(**credentials)
    api = "api/storage/" + credentials.get("repo")

    for file in autodownloader.get_all_files(api):
        uri = file["downloadUri"]
        filename = os.path.basename(uri)
        if re.search(credentials.get("pattern"), uri):
            if not is_file_exist(credentials.get("dstfolder"), filename):
                autodownloader.download(uri)
            else:
                console.log(f"File {filename} already exists.")
from artifactory import ArtifactoryPath
import sys
import requests
from requests.adapters import HTTPAdapter
import urllib3
import json
import re
import os
import time
from datetime import datetime
import pytz
from loguru import logger
from typing import Optional
from collections.abc import Callable
import tarfile
import zipfile
from tqdm import tqdm

urllib3.disable_warnings()
ROOT = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-3])


class ArtifaHelper:
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(
        self,
        repo: str = "zeekr-dhu-repos/builds/rb-zeekr-dhu_hqx424-fc_main_dev/daily/",
        pattern: str = "_userdebug.tgz$",
        server: str = "https://rb-cmbinex-szh-p1.apac.bosch.com/artifactory/",
        auth: tuple = ("ets1szh", "estbangbangde6"),
        dstfolder: str = "downloads",
    ) -> None:
        self.server = server
        self.repo = repo
        self.pattern = pattern
        self.auth = auth
        self.dstfolder = os.path.join(ROOT, dstfolder)

        if not os.path.exists(self.dstfolder):
            os.mkdir(self.dstfolder)

    def _get_url(self, package) -> str:
        return self.server + self.repo + package

    def get_root(self) -> str:
        return self.dstfolder

    def get_swpath(self, name: str = "all_images_8295") -> str:
        return os.path.join(self.dstfolder, name)

    def connection_test(self) -> None:
        path = ArtifactoryPath(self.server + self.repo, auth=self.auth, verify=False)
        try:
            path.touch()
        except RuntimeError as e:
            logger.error(e)
        except:
            raise

    def download(self, url: str) -> str:
        chunk_size = 1024 * 1024
        t_s = time.time()
        arti_path = ArtifactoryPath(url, auth=self.auth, verify=False)
        local_file = os.path.join(self.dstfolder, os.path.basename(arti_path))
        file_size = round(ArtifactoryPath.stat(arti_path).size / 1024 / 1024, 2)
        logger.info(f"The file size is: {file_size} MB")
        count = 0
        try:
            fi = arti_path.open()
            fo = open(local_file, "wb")
            logger.info(f"Downloading the file- {local_file}")
            while True:
                piece = fi.read(chunk_size)
                if piece:
                    fo.write(piece)
                    fo.flush()
                    count += 1
                    logger.debug(f"Downloading progress - [{count}MB/{file_size}MB]")
                else:
                    logger.success(f"OK!Download file success - {local_file}")
                    break
        except Exception as e:
            logger.error(f"Error occurs in downloading: {e}")
        t_e = time.time()
        logger.success("Finish->time cost: ", t_e - t_s)
        return os.path.join(self.dstfolder, url.split("/")[-1])

    def monitor(self, thres: int, callback: Optional[Callable] = None) -> bool:
        f_lastModified = self.get_latest()
        tz = pytz.timezone("Asia/Shanghai")
        now = datetime.now(tz)
        t = datetime.strptime(f_lastModified["lastModified"], "%Y-%m-%dT%H:%M:%S.%f%z")
        diff_hrs = (now - t).total_seconds() / 60 / 60
        if diff_hrs < thres:
            logger.info(
                f"The latest version {f_lastModified} was built within {thres} hrs."
            )
            if callback:
                callback()
            return True
        else:
            logger.info(
                f"No actifacts found in {thres} hrs. The latest version was built {diff_hrs} hrs ago."
            )
            return False

    def get_latest(self) -> Optional[dict]:
        session = requests.Session()
        session.mount("http://", HTTPAdapter(max_retries=3))
        session.mount("https://", HTTPAdapter(max_retries=3))
        session.keep_alive = True
        logger.info("Requesting Artifactory server, please wait...")
        api = (
            "api/storage/"
            + self.repo
            + "?list&deep=1&listFolders=0&mdTimestamps=0&includeRootPath=0"
        )
        try:
            response = session.get(
                self.server + api, auth=self.auth, verify=False, timeout=60
            )
        except urllib3.exceptions.ReadTimeoutError:
            logger.error("Request time out!")
            sys.exit(1)
        except requests.exceptions.ProxyError:
            logger.error("Proxy is required!")
            sys.exit(1)
        else:
            logger.info("Done request successfully.")
            data = json.loads(response.text)

        t_lastModified = ""
        f_lastModified = ""
        if "files" not in data:
            logger.error("Make sure your pattern and repo are correct.")
            sys.exit(1)
        for file in data["files"]:
            if file["lastModified"] > t_lastModified and re.search(
                self.pattern, file["uri"]
            ):
                t_lastModified = file["lastModified"]
                f_lastModified = file

        if not f_lastModified:
            logger.error("Response is empty!!")
            sys.exit(1)
        f_lastModified["url"] = self._get_url(f_lastModified["uri"])
        logger.success(f"Get latest version {f_lastModified['url']}")
        return f_lastModified

    @staticmethod
    def unzip(
        dsfile: str, dcfolder: Optional[str] = None, members: Optional[list] = None
    ) -> None:
        """
        Extracts `tar_file` and puts the `members` to `path`.
        If members is None, all members on `tar_file` will be extracted.
        """
        if not os.path.exists(dsfile):
            logger.error("File not Exist!")
            sys.exit(1)

        if not dcfolder:
            dcfolder = os.path.dirname(dsfile)

        if dsfile.split(".")[-1] == "tgz":
            tar = tarfile.open(dsfile, mode="r:gz")
            logger.info(f"Start uncompressing tgz: {dsfile}")
            if members is None:
                members = tar.getmembers()
            progress = tqdm(members)
            for member in progress:
                tar.extract(member, path=dcfolder)
                progress.set_description(f"Extracting {member.name}")
            tar.close()
            logger.success(f"Done uncompressing")
        elif dsfile.split(".")[-1] == "zip":
            zip = zipfile.ZipFile(dsfile, "r")
            logger.info(f"Start uncompressing zip: {dsfile}")
            if members is None:
                members = zip.namelist()
            progress = tqdm(members)
            for member in progress:
                zip.extract(member, path=dcfolder)
                progress.set_description(f"Extracting {member}")
            zip.close()
            logger.success(f"Done uncompressing")
        else:
            logger.error("File type is not supported to decompress.")
            sys.exit(1)

    def __str__(self) -> str:
        return f"Tool to download from Artifactory."

    def __repr__(self) -> str:
        return f"ArtifaHelper({self.server}, {self.auth}, {self.dstfolder})"


if __name__ == "__main__":
    ar = ArtifaHelper(
        repo="zeekr-dhu-repos/builds/rb-zeekr-dhu_hqx424-fc_main_dev/daily/",
        pattern="_userdebug.tgz$",
    )
    f_lastModified = ar.get_latest()
    # monitor

    # package = ar.download(f_lastModified["url"])
    # ArtifaHelper.unzip(package)

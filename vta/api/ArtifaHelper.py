# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

import hashlib
import json
import os
import re
import sys
import tarfile
import zipfile
from collections.abc import Callable
from datetime import datetime
from typing import Optional, Tuple

import pytz
import requests
import urllib3
from artifactory import ArtifactoryPath
from loguru import logger
from tqdm import tqdm

from vta.api.utility.Downloader import (
    Multiple_Thread_Downloader,
    Single_Thread_Downloader,
)

urllib3.disable_warnings()
ROOT = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-3])


class ArtifaHelper:
    def __init__(
        self,
        repo: str = "zeekr-dhu-repos/builds/rb-zeekr-dhu_hqx424-fc_main_dev/daily/",
        pattern: str = "_userdebug.tgz$",
        server: str = "https://rb-cmbinex-szh-p1.apac.bosch.com/artifactory/",
        auth: tuple = ("ets1szh", "estbangbangde6"),
        dstfolder: str = "downloads",
        multithread: bool = True,
        pro: bool = True,
    ) -> None:
        self.server = server
        self.repo = repo
        self.pattern = pattern
        self.auth = auth
        self.multithread = multithread
        self.pro = pro
        self.dstfolder = os.path.join(ROOT, dstfolder)

        if not os.path.exists(self.dstfolder):
            os.mkdir(self.dstfolder)

    def _get_url(self, package) -> str:
        return self.server + self.repo + package

    def get_root(self) -> str:
        return self.dstfolder

    def get_swpath(self, name: str = "all_images_8295") -> str:
        all_images_path = os.path.join(self.dstfolder, name)
        host_all_images_path = os.path.join(self.dstfolder, "HOST", name)
        if os.path.exists(all_images_path):
            return all_images_path
        elif os.path.exists(host_all_images_path):
            return host_all_images_path
        else:
            logger.warning(f"No path Found! {name}")
            return

    def connection_test(self) -> None:
        path = ArtifactoryPath(self.server + self.repo, auth=self.auth, verify=False)
        try:
            path.touch()
        except RuntimeError as e:
            logger.error(e)
        except:
            raise

    def fetch_url(self, api: str) -> None:
        logger.info("Requesting Artifactory server, please wait...")
        try:
            response = requests.get(
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
        return data

    def checksum(self, filepath, origin) -> bool:
        with open(filepath, "rb") as f:
            sha1 = hashlib.sha1()
            while True:
                chunk = f.read(16 * 1024)
                if not chunk:
                    break
                sha1.update(chunk)
        if sha1.hexdigest() == origin:
            return True
        return False

    def download(self, url: str) -> str:
        if self.multithread:
            downloader = Multiple_Thread_Downloader()
        else:
            downloader = Single_Thread_Downloader()
        downloader.start(url, self.auth, self.dstfolder)
        return os.path.join(self.dstfolder, url.split("/")[-1])

    def get_latest(self) -> Optional[dict]:
        api = "api/storage/" + self.repo

        t_lastModified = ""
        f_lastModified = ""
        try:
            for data in self.get_all_files(api):
                if data["lastModified"] > t_lastModified and re.search(
                    self.pattern, data["downloadUri"]
                ):
                    t_lastModified = data["lastModified"]
                    f_lastModified = data
        except KeyError as e:
            logger.exception(e)
            sys.exit(1)

        f_lastModified["url"] = f_lastModified["downloadUri"]
        f_lastModified["sha1"] = f_lastModified["checksums"]["sha1"]
        logger.success(f"Get latest version {f_lastModified['url']}")
        return f_lastModified

    def get_latest_pro(self) -> Optional[dict]:
        # only works for artifactory pro
        api = (
            "api/storage/"
            + self.repo
            + "?list&deep=1&listFolders=0&mdTimestamps=0&includeRootPath=0"
        )

        t_lastModified = ""
        f_lastModified = ""
        try:
            for file in self.fetch_url(api)["files"]:
                if file["lastModified"] > t_lastModified and re.search(
                    self.pattern, file["uri"]
                ):
                    t_lastModified = file["lastModified"]
                    f_lastModified = file
        except KeyError as e:
            logger.exception(e)
            sys.exit(1)

        f_lastModified["url"] = self._get_url(f_lastModified["uri"])
        logger.success(f"Get latest version {f_lastModified['url']}")
        return f_lastModified

    def get_all_files(self, initial_api: str):
        data = self.fetch_url(initial_api)
        if data is not None:
            if "children" in data:
                for child_url in data["children"]:
                    yield from self.get_all_files(initial_api + child_url["uri"])
            else:
                yield data

    def monitor(
        self, thres: int, callback: Optional[Callable] = None
    ) -> Tuple[bool, str]:
        if self.pro:
            f_lastModified = self.get_latest_pro()
        else:
            f_lastModified = self.get_latest()
        tz = pytz.timezone("Asia/Shanghai")
        now = datetime.now(tz)
        t = datetime.strptime(f_lastModified["lastModified"], "%Y-%m-%dT%H:%M:%S.%f%z")
        diff_hrs = (now - t).total_seconds() / 60 / 60
        if diff_hrs < thres:
            logger.success(
                f"The latest version {f_lastModified['uri']} was built within {thres} hrs."
            )
            if callback:
                callback()
            return True, f_lastModified["uri"]
        else:
            logger.info(
                f"No actifacts found in {thres} hrs. The latest version was built {diff_hrs} hrs ago."
            )
            return False, f_lastModified["uri"]

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
        # server="https://rb-cmbinex-fe-p1.de.bosch.com/artifactory/",
        # repo="zeekr-dhu-repos/builds/rb-zeekr-dhu_hqx424-pcs01_main_dev/daily/",
        repo="zeekr-dhu-repos/builds/rb-zeekr-dhu_hqx424-pcs01_main_dev_zeekr_dhu_r1_release/daily/",
        pattern="_userdebug.tgz$",
        multithread=True,
        pro=True,
    )
    f_lastModified = ar.monitor(thres=24)

    # ar = ArtifaHelper(
    #     repo="zeekr/8295_ZEEKR/daily_cx1e/",
    #     pattern="qfil_.*",
    #     server="https://hw-snc-jfrog-dmz.zeekrlife.com/artifactory/",
    #     auth=("bosch-gitauto", "Bosch-gitauto@123"),
    #     multithread=True
    # )
    # f_lastModified = ar.fetch_url(api=f"api/storage/{ar.repo}")
    # f_lastModified = ar.fetch_url(api=f"/api/download?repoKey=zeekr&path=8295_ZEEKR/daily_cx1e/20230916_POSTCS/CX1E00CNTDB0916DEV0135/qfil_CX1E00CNTDB0916DEV0135.zip")
    # print(f_lastModified)
    # f_lastModified = ar.get_latest()
    # from rich.pretty import pprint

    # pprint(f_lastModified)
    # ar.monitor(thres=33, callback=func)
    # monitor

    # package = ar.download(f_lastModified["url"])
    # package = ar.download("https://hw-snc-jfrog-dmz.zeekrlife.com/artifactory/zeekr/8295_ZEEKR/daily_cx1e/20230918_POSTCS_TMP/CX1E00CNTDB0918DEVTMP1/qfil_CX1E00CNTDB0918DEVTMP1.zip")
    # ArtifaHelper.unzip(package)

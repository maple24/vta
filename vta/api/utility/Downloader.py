# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

import os
import sys
import threading
import time
from contextlib import closing

import requests.adapters
from artifactory import ArtifactoryPath
from loguru import logger
from requests.adapters import HTTPAdapter


class Single_Thread_Downloader:
    def __init__(self, chunk_size=1024 * 1024) -> None:
        self.chunk_size = chunk_size
        self.__content_size = 0

    def __establish_connect(self, url, auth):
        artiPath = ArtifactoryPath(url, auth=auth, verify=False)
        hrd = artiPath.open()
        self.__content_size = int(hrd.headers["Content-Length"])
        logger.success("Connection established.")
        return artiPath

    def start(self, url: str, auth: tuple, dstfolder: str) -> str:
        t_s = time.time()
        arti_path = self.__establish_connect(url, auth)
        local_file = os.path.join(dstfolder, os.path.basename(arti_path))
        count = 0
        try:
            fi = arti_path.open()
            fo = open(local_file, "wb")
            logger.info(f"Downloading the file- {local_file}")
            while True:
                piece = fi.read(self.chunk_size)
                if piece:
                    fo.write(piece)
                    fo.flush()
                    count += 1
                    logger.debug(
                        f"Downloading progress - [{count * self.chunk_size / 1024 / 1024}MB/{self.__content_size / 1024 / 1024:.2f}MB]"
                    )
                else:
                    logger.success(f"OK!Download file success - {local_file}")
                    break
        except Exception as e:
            logger.exception(f"Error occurs in downloading: {e}")
        t_e = time.time()
        logger.success(f"Finish->time cost: {t_e - t_s}")


class Multiple_Thread_Downloader:
    """
    usage:
    downloader=Downloader()
    downloader.start(
        deployPath="http://file.example.com/somedir/filename.ext",
        auth=('admin', 'password')
        target_file="/path/to/file.ext")
    """

    def __init__(
        self, threads_num=20, chunk_size=1024 * 1024, timeout=60, max_retries=5
    ):
        """
        initialization
        :param threads_num=5: number of threads created, 5 by default
        :param chunk_size=1024*1024: the chunk size of the stream get request each time
        :param timeout=60: the maximum time waiting, unit is second
        """
        self.threads_num = threads_num
        self.chunk_size = chunk_size
        self.timeout = timeout if timeout != 0 else threads_num
        self.max_retries = max_retries

        self.__content_size = 0
        self.__file_lock = threading.Lock()
        self.__threads_status = {}
        self.__crash_event = threading.Event()

        self.session = requests.Session()
        self.session.mount("http://", HTTPAdapter(max_retries=self.max_retries))
        self.session.mount("https://", HTTPAdapter(max_retries=self.max_retries))

    def __establish_connect(self, deployPath, auth):
        """
        connection establishment
        :param deployPath: the file path in artifactory
        :param apikey: the verification of the user generated by artifactory
        """
        artiPath = ArtifactoryPath(deployPath, auth=auth, verify=False)
        hrd = artiPath.open()
        self.__content_size = int(hrd.headers["Content-Length"])
        logger.success("Connection established.")
        return artiPath

    def __page_dispatcher(self):
        """
        dispatch the size for each thread to download
        """
        basic_page_size = self.__content_size // self.threads_num
        start_pos = 0
        while start_pos + basic_page_size < self.__content_size:
            yield {"start_pos": start_pos, "end_pos": start_pos + basic_page_size}
            start_pos += basic_page_size + 1
        # the last part remained
        yield {"start_pos": start_pos, "end_pos": self.__content_size - 1}

    def __download(self, deployPath, auth, file, page):
        """
        download method
        :param deployPath: the file path in artifactory
        :param file: the path for local storage
        :param page: dict for indication of the start and end position
        description: for each thread, pointer moves according to size of every patches; for each patch, pointer moves 1 chunksize a time
        """
        # the byte range for the current thread responsible for
        retry_count = 0
        while retry_count < self.max_retries:
            headers = {"Range": f"bytes={page['start_pos']}-{page['end_pos']}"}
            thread_name = threading.current_thread().name
            # initialize the thread status
            self.__threads_status[thread_name] = {
                "page_size": page["end_pos"] - page["start_pos"],
                "page": page,
                "status": 0,
            }
            try:
                with closing(
                    self.session.get(
                        url=deployPath,
                        auth=auth,
                        verify=False,
                        headers=headers,
                        stream=True,
                        timeout=self.timeout,
                    )
                ) as response:
                    chunk_num = 0
                    for data in response.iter_content(chunk_size=self.chunk_size):
                        # write the chunk size bytes to the target file and needs Rlock here
                        with self.__file_lock:
                            # seek the start position to write from
                            file.seek(page["start_pos"])
                            # write datd
                            file.write(data)
                            chunk_num += 1
                            if self.__threads_status[thread_name]["status"] == 0:
                                if page["start_pos"] < page["end_pos"]:
                                    logger.debug(
                                        f"{thread_name}  Downloaded: {chunk_num * self.chunk_size / 1024 / 1024}MB / {self.__threads_status[thread_name]['page_size'] / 1024 / 1024:.2f}MB"
                                    )
                                else:
                                    logger.success(f"{thread_name} Finished.")
                            elif self.__threads_status[thread_name]["status"] == 1:
                                logger.warning(f"{thread_name} Crushed.")
                        # the pointer moves forward along withe the writing execution
                        page["start_pos"] += len(data)
                        self.__threads_status[thread_name]["page"] = page
                    break
            except requests.RequestException as exception:
                logger.exception(f"{exception}")
                retry_count += 1
                if retry_count < self.max_retries:
                    logger.info(f"{thread_name} Retrying (attempt {retry_count})...")
        if retry_count == self.max_retries:
            logger.error(f"Max retry attempts reached. {thread_name} Download failed.")
            self.__threads_status[thread_name]["status"] = 1
            self.__crash_event.set()
        else:
            logger.success(f"{thread_name} Finish download")

    def __run(self, deployPath, auth, dstfolder):
        """
        run the download thread
        :param deployPath: the file path in artifactory
        :param apikey: the verification of the user generated by artifactory
        :param target_file: the path for local storage including the extension
        :param urlhandler: handler for url including redirction or non-exist
        """
        arti_path = self.__establish_connect(deployPath, auth)
        target_file = os.path.join(dstfolder, os.path.basename(arti_path))
        self.__threads_status["url"] = deployPath
        self.__threads_status["target_file"] = target_file
        self.__threads_status["content_size"] = self.__content_size
        self.__crash_event.clear()
        logger.info(
            f"The file meta information \nURL: {self.__threads_status['url']}\nFile Name: {self.__threads_status['target_file']}\nSize: {self.__threads_status['content_size'] / 1024 / 1024 / 1024:.2f}GB"
        )
        with open(target_file, "wb+") as file:
            thread_poll = []
            for page in self.__page_dispatcher():
                thd = threading.Thread(
                    target=self.__download, args=(deployPath, auth, file, page)
                )
                thread_poll.append(thd)
                thd.start()
            for download_thread in thread_poll:
                download_thread.join()

        # if crash in downloading
        if self.__crash_event.is_set():
            logger.exception("Error for downloading!!!")
            sys.exit()
        logger.success("Download finished")

    def start(self, url, auth, dstfolder):
        """
        start method for running the program
        :param deployPath: the file path in artifactory
        :param apikey: the verification of the user generated by artifactory
        :param target_file the path for local storage including the extension
        :param urlhandler: handler for url including redirction or non-exist
        """
        # the start time
        start_time = time.time()
        self.__run(url, auth, dstfolder)

        # total tme used for downloading
        span = time.time() - start_time
        logger.info(
            f"Downloading finished, total time used:{span - 0.5}s, average speed:{self.__content_size / 1024 / (span - 0.5):.2f}KB/s"
        )

import time
import psutil
import subprocess
from loguru import logger

class GenericHelper:

    @staticmethod
    def terminate(process):
        parent = psutil.Process(process.pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
        if process.poll() is None:
            logger.info("Process is terminated.")
        else:
            logger.error("Fail to terminate process!")

    @staticmethod
    def prompt_command(cmd: str, timeout: float = 5.0) -> list:
        data = []
        start = time.time()
        logger.info("[{stream}] - {message}", stream="PromptTx", message=cmd)
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
        )
        out = process.stdout
        while time.time() - start < timeout:
            if process.poll() is not None:
                break
            line = out.readline().decode("utf-8").strip()
            if line:
                data.append(line)
                logger.trace("[{stream}] - {message}", stream="PromptRx", message=line)
        try:
            GenericHelper.terminate(process)
        except psutil.NoSuchProcess:
            logger.info("Process not exist.")
            pass
        return data


if __name__ == '__main__':
    data = GenericHelper.prompt_command("dir")
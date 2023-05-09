from library.PuttyHelper import PuttyHelper
from library.GenericHelper import GenericHelper
from loguru import logger


def startup(mputty: PuttyHelper, n: int = 3):
    mputty.login()
    for i in range(n):
        res, _ = mputty.wait_for_trace("", cmd="bosch_reset", timeout=20)
        if not res:
            logger.error(f"Start up test fail in round {i}")


if __name__ == "__main__":
    # mputty = putty_helper()
    dputty = {
        "putty_enabled": True,
        "putty_comport": "COM9",
        "putty_baudrate": 115200,
        "putty_username": "root",
        "putty_password": "6679836772",
    }
    # mputty.connect(dputty)
    # startup(mputty)
    # mputty.disconnect()
    GenericHelper.prompt_command("dir")

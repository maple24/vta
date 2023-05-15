from loguru import logger


class DBHelper:
    def __init__(self) -> None:
        pass

    def test(self, msg):
        print("hello")
        logger.info(f"update {msg}")

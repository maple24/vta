# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================
import time
from functools import wraps


def wait_and_retry(timeout: int = 10, interval: float = 1.0, retry_times: int = None):
    """
    Retry calling the decorated function until it returns a truthy value,
    or retry_times is exceeded (if set), otherwise until timeout.
    Args:
        timeout (int): Total time to keep retrying (seconds).
        interval (float): Wait time between retries (seconds).
        retry_times (int, optional): Maximum number of retries. If set, ignore timeout.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if retry_times is not None:
                for _ in range(retry_times):
                    result = func(*args, **kwargs)
                    if result:
                        return result
                    time.sleep(interval)
                return False
            else:
                end_time = time.time() + timeout
                while time.time() < end_time:
                    result = func(*args, **kwargs)
                    if result:
                        return result
                    time.sleep(interval)
                return False

        return wrapper

    return decorator


def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kwagrs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwagrs)
        return _instance[cls]

    return _singleton


"""
Demo class
"""


class Demo:
    def __init__(self):
        self.counter = 0

    @wait_and_retry(timeout=5, interval=1, retry_times=3)
    def count_times(self):
        self.counter += 1
        print(f"Attempt {self.counter}")
        # Only return True on the third attempt
        return self.counter >= 3

    @wait_and_retry(timeout=5, interval=0.1)
    def simple_method(self):
        self.counter += 1
        print(f"Attempt {self.counter}")


def hello():
    print("hello world")


if __name__ == "__main__":
    # demo = Demo()
    # result = demo.simple_method()
    # print("Result:", result)
    retry_hello = wait_and_retry(timeout=2, interval=1)(hello)
    retry_hello()

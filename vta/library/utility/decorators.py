# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================
import time
from functools import wraps
from loguru import logger
from rich.console import Console

console = Console()


def timed_step(attr_name):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            start = time.time()
            result = func(self, *args, **kwargs)
            if result:
                duration = time.time() - start
                setattr(self, attr_name, duration)
                logger.info(f"{func.__name__} completed in {duration:.2f} seconds")
            return result

        return wrapper

    return decorator


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
            func_name = func.__name__
            if retry_times is not None:
                console.rule(f"[bold cyan]wait_and_retry: {func_name} (max {retry_times} attempts)")
                for attempt in range(1, retry_times + 1):
                    console.log(f"[yellow]Attempt {attempt}/{retry_times} for [bold]{func_name}[/]")
                    result = func(*args, **kwargs)
                    if result:
                        console.log(f"[green]'{func_name}' succeeded on attempt {attempt}[/]")
                        return result
                    time.sleep(interval)
                console.log(f"[red]'{func_name}' failed after {retry_times} attempts[/]")
                return False
            else:
                console.rule(f"[bold cyan]wait_and_retry: {func_name} (timeout {timeout}s)")
                end_time = time.time() + timeout
                attempt = 1
                while time.time() < end_time:
                    elapsed = timeout - (end_time - time.time())
                    console.log(f"[yellow]Time elapsed: {elapsed:.2f}s for [bold]{func_name}[/] (timeout mode)")
                    result = func(*args, **kwargs)
                    if result:
                        console.log(f"[green]'{func_name}' succeeded after {elapsed:.2f}s[/]")
                        return result
                    time.sleep(interval)
                    attempt += 1
                console.log(f"[red]'{func_name}' failed after timeout ({timeout}s)[/]")
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
        if self.counter >= 3:
            return True
        else:
            return False

    @wait_and_retry(timeout=5, interval=0.1)
    def simple_method(self):
        self.counter += 1
        print(f"Attempt {self.counter}")


def hello():
    print("hello world")

@wait_and_retry(retry_times=3, interval=1)
def greet():
    print("greet")


if __name__ == "__main__":
    greet()
    # demo = Demo()
    # result = demo.simple_method()
    # print("Result:", result)
    # retry_hello = wait_and_retry(timeout=2, interval=1)(hello)
    # retry_hello()

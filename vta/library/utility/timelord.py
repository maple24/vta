# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

import datetime
from rich.progress import Progress
import time


def get_day_abbreviation():
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    today = datetime.datetime.today()  # Get today's date and time
    day_of_week = (
        today.weekday()
    )  # Get the day of the week as an integer (0 = Monday, 1 = Tuesday, etc.)
    return days[day_of_week]  # Get the abbreviation for the day of the week

def countdown(seconds: int):
    """
    Displays a countdown timer with a progress bar for the given number of seconds.
    """
    with Progress() as progress:
        task = progress.add_task("[cyan]Counting down...", total=seconds)
        for remaining in range(seconds, 0, -1):
            progress.update(task, completed=seconds - remaining)
            time.sleep(1)
        progress.update(task, completed=seconds)


if __name__ == "__main__":

    # get current datetime
    dt = datetime.datetime.now()
    print("Datetime is:", dt)

    # get weekday name
    print("day Name:", dt.strftime("%A"))

    # Example usage of countdown with rich progress bar
    countdown(5)

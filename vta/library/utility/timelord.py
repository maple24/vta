# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

import datetime


def get_day_abbreviation():
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    today = datetime.datetime.today()  # Get today's date and time
    day_of_week = (
        today.weekday()
    )  # Get the day of the week as an integer (0 = Monday, 1 = Tuesday, etc.)
    return days[day_of_week]  # Get the abbreviation for the day of the week


if __name__ == "__main__":
    from datetime import datetime

    # get current datetime
    dt = datetime.now()
    print("Datetime is:", dt)

    # get weekday name
    print("day Name:", dt.strftime("%A"))

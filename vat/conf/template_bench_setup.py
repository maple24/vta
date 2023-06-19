"""
bench setups
"""
import os
from loguru import logger

ROOT = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-3])
# enable database
DATABASE = False
CREDENTIAL = {"drivername": "sqlite", "database": "database.db"}
# CREDENTIAL = {
#     "drivername": "mysql",
#     "username": "root",
#     "password": "Boschets123",
#     "host": "10.178.227.22",
#     "database": "gmw_v3.5"
# }
# enable mail
MAIL = False
SLOT_1 = {
    # putty channel
    "dputty": {
        "putty_enabled": True,
        "putty_comport": "COM9",
        "putty_baudrate": 115200,
        "putty_username": "zeekr",
        "putty_password": "Aa123123",
    },
    # programming power supply
    "dpps": {
        "pps_enabled": False,
        "pps_analog": False,
        "pps_comport": "COM16",
        "pps_baudrate": 9600,
        "pps_channel_used": 1,
    },
    # relay
    "drelay": {
        "relay_enabled": False,
        "multiplexer": {"enabled": False, "comport": "COM6"},
        "xinke": {"enabled": True, "comport": "COM16", "channel": "2"},
    },
    "dtsmaster": {
        "tsmaster_enabled": True,
        "tsmaster_rbs": "C:\\Users\\EZO1SGH\\Desktop\\Vehicle_test\\RBS_projects\\Tosun_Wakeup\\Tosun",
        "tsmaster_channel_vgm": 0,
        "tsmaster_channel_vddm": 1,
    },
}

SLOT_2 = {
    # putty channel
    "dputty": {
        "putty_enabled": False,
        "putty_comport": "COM9",
        "putty_baudrate": 115200,
        "putty_username": "zeekr",
        "putty_password": "Aa123123",
    },
    # programming power supply
    "dpps": {
        "pps_enabled": False,
        "pps_analog": False,
        "pps_comport": "COM16",
        "pps_baudrate": 9600,
        "pps_channel_used": 1,
    },
    # relay
    "drelay": {
        "relay_enabled": False,
        "multiplexer": {"enabled": False, "comport": "COM6"},
        "xinke": {"enabled": True, "comport": "COM16", "channel": "2"},
    },
    "dtsmaster": {
        "tsmaster_enabled": True,
        "tsmaster_rbs": "C:\\Users\\EZO1SGH\\Desktop\\Vehicle_test\\RBS_projects\\Tosun_Wakeup\\Tosun",
        "tsmaster_channel_vgm": 0,
        "tsmaster_channel_vddm": 1,
    },
}

"""
bench setups
"""
import os
from loguru import logger

ROOT = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-3])
# enable database
DATABASE = False
DB_CREDENTIAL = {"drivername": "sqlite", "database": "database.db"}
# DB_CREDENTIAL = {
#     "drivername": "mysql",
#     "username": "ets1szh",
#     "password": "estbangbangde",
#     "host": "10.161.224.58",
#     "database": "zeekr"
# }
# enable mail
MAIL = False
MAIL_CREDENTIAL = {
    "sender": "Test.EST@cn.bosch.com",
    "username": "ets1szh",
    "password": "estbangbangde6",
    "recepients": ["Test.EST@bcn.bosch.com", "jin.zhu5@cn.bosch.com"],
}
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

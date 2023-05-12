"""
bench setups
"""
import os

ROOT = "\\".join(os.path.abspath(__file__).split("\\")[:-3])

SLOT_1 = {
    # putty channel
    "dputty": {
        "putty_enabled": True,
        "putty_comport": "COM9",
        "putty_baudrate": 115200,
        "putty_username": "root",
        "putty_password": "6679836772",
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
        "multiplexer": {"enabled": "False", "comport": "COM6"},
        "cleware": {"enabled": "False", "dev_id": "710452"},
        "xinke": {"enabled": "False", "comport": "COM10"},
        "mcube": {"enabled": "False", "comport": "COM16", "run_mode": "2*4"},
    },
}

SLOT_2 = {
    # putty channel
    "dputty": {
        "putty_enabled": False,
        "putty_comport": "COM9",
        "putty_baudrate": 115200,
        "putty_username": "root",
        "putty_password": "6679836772",
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
        "multiplexer": {"enabled": "False", "comport": "COM6"},
        "cleware": {"enabled": "False", "dev_id": "710452"},
        "xinke": {"enabled": "False", "comport": "COM10"},
        "mcube": {"enabled": "False", "comport": "COM16", "run_mode": "2*4"},
    },
}

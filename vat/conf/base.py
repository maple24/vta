"""
bench setups
"""
from loguru import logger
import os
import time
ROOT = "\\".join(os.path.abspath(__file__).split("\\")[:-3])
SLOT = 1

logger.add(
    f"{ROOT}\\log\\log_{time.strftime('%m%d%Y_%H%M%S')}_SLOT{SLOT}.log",
    backtrace=True,
    diagnose=False,
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    rotation="1 week",
    level="TRACE",
)

# putty channel
dputty = {
    "putty_enabled": True,
    "putty_comport": "COM9",
    "putty_baudrate": 115200,
    "putty_username": "root",
    "putty_password": "6679836772",
}

# programming power supply
dpps = {
    "pps_enabled": False,
    "pps_analog": False,
    "pps_comport": "COM16",
    "pps_baudrate": 9600,
    "pps_channel_used": 1,
}

# relay
drelay = {
    "relay_enabled": False,
    "multiplexer": {"enabled": "False", "comport": "COM6"},
    "cleware": {"enabled": "False", "dev_id": "710452"},
    "xinke": {"enabled": "False", "comport": "COM10"},
    "mcube": {"enabled": "False", "comport": "COM16", "run_mode": "2*4"},
}

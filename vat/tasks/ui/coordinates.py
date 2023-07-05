import os

# init path
ROOT = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-3])
TEMP = os.path.join(ROOT, "tmp")
if not os.path.exists(TEMP):
    os.mkdir(TEMP)

# define coordinates
BT_BUTTON = (2400, 220)
WIFI_BUTTON = (2400, 220)
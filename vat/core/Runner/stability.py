import os
import time
from datetime import datetime
from robot import run_cli, rebot_cli
from loguru import logger
import sys
import argparse

# User argument interface
parser = argparse.ArgumentParser()
parser.add_argument("--task", type=str, required=True, help='robot task file')
parser.add_argument("--slot", default=1, type=int, help='slot number')
parser.add_argument("--max_loop", default=1, type=int, help='maximum of loops',)
parser.add_argument("--name", default='Stability Test', type=str, help='name of combined test suite')
parser.add_argument("--listener", default='PyListener.py', type=str, help='listener file')
parser.add_argument("--modifier", type=str, help='modifier file')
args = parser.parse_args()

TASK = args.task  # required
SLOT = args.slot  # default to be 1
MAXLOOP = args.max_loop  # default to be 1
REPORTNAME = args.name  # default to be `Stability Test`
LISTENER = args.listener  # default to be `PyListener.py`
MODIFIER = args.modifier  # default to be None

'''
=============================== DO NOT CHANGE ===============================
'''
ROOT = "\\".join(os.path.abspath(__file__).split("\\")[:-4])
LOGPATH = os.path.join(ROOT, 'log', f"{datetime.now().strftime('%A')}_{time.strftime('%m%d%Y_%H%M')}_SLOT{SLOT}")
TASKPATH = os.path.join(ROOT, 'vat', 'tasks', TASK)
if LISTENER: LISTENERPATH = os.path.join(ROOT, 'vat', 'core', 'utils', LISTENER)
if MODIFIER: MODIFIERPATH = os.path.join(ROOT, 'vat', 'core', 'utils', MODIFIER)
logger.remove()
logger.add(sys.stdout, level="DEBUG")
mylogger = logger.add(
    f"{LOGPATH}\\log_{time.strftime('%m%d%Y_%H%M%S')}.log",
    backtrace=True,
    diagnose=False,
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    rotation="1 week",
    level="TRACE",
)
'''
=============================== DO NOT CHANGE ===============================
'''

# Satbility Runner
if not os.path.exists(TASKPATH):
    logger.error(f"{TASK} not exist!")
    exit(1)

count = 1

for i in range(MAXLOOP):
    logger.remove(mylogger)
    mylogger = logger.add(
        f"{LOGPATH}\\log_{count}.log",
        backtrace=True,
        diagnose=False,
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
        rotation="1 week",
        level="TRACE",
    )
    common = ['--exitonfailure', '--outputdir', f'{LOGPATH}', '--output', f'output_{count}.xml', '--log', f'log_{count}.html', '--report', 'none']
    if LISTENER:
        common += ['--listener', f'{LISTENERPATH}']
    if MODIFIER:
        common += ['--prerunmodifier', f'{MODIFIERPATH}']
    variable = ['--variable', f'SLOT:SLOT_{SLOT}']
    rc = run_cli(common + variable + ['--exclude', 'skip',f'{TASKPATH}'], exit=False)
    if rc != 0: 
        logger.warning(f"Test terminated due to exitcode {rc}!")
    count += 1

try:
    rebot_cli(['--name', f'{REPORTNAME}', '--outputdir', f'{LOGPATH}\\report', f'{LOGPATH}\\*.xml'])
    logger.success("Reports are combined successfully!")
except SystemExit:
    # normal exit by rebot cli
    pass
except:
    logger.exception("Unable to combine outputs!!!")
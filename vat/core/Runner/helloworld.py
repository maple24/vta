import os
import time
from datetime import datetime
from robot import run_cli, rebot_cli
from loguru import logger
import sys

# set your task here
TASK = 'hello.robot'
SLOT = 2
MAXLOOP = 2
REPORTNAME = 'Just an example'

'''
=============================== DO NOT CHANGE ===============================
'''
ROOT = "\\".join(os.path.abspath(__file__).split("\\")[:-3])
LOGPATH = os.path.join(ROOT, 'log', f"{datetime.now().strftime('%A')}_{time.strftime('%m%d%Y_%H%M')}_SLOT{SLOT}")
TASKPATH = os.path.join(ROOT, 'vat', 'tasks', TASK)
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


if __name__ == '__main__':
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
        variable = ['--variable', f'SLOT:SLOT_{SLOT}']
        common = ['--outputdir', f'{LOGPATH}', '--output', f'output_{count}.xml', '--log', f'log_{count}.html', '--report', 'none']
        rc = run_cli(common + variable + ['--exclude', 'notReady',f'{TASKPATH}'], exit=False)
        if rc != 0: 
            logger.warning(f"Test terminated due to exitcode {rc}!")
        count += 1
    
    try:
        rebot_cli(['--name', f'{REPORTNAME}', '--outputdir', f'{LOGPATH}\\report', f'{LOGPATH}\\*.xml'])
    except SystemExit:
        # normal exit by rebot cli
        pass
    except:
        logger.exception("Unable to combine outputs!!!")
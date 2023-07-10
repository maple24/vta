from loguru import logger
import os
from performance import Performance

logger.add(
    os.path.join(os.path.dirname(__file__), "performance.log"),
    backtrace=True,
    diagnose=False,
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    rotation="1 week",
)

if __name__ == "__main__":
    nfs_disk = ["/data/vendor/nfs/mount", "/data/vendor/nfs/nfs_log"]
    aos_cmds = [
        {"cmd": "top -b -n 1", "output": "aos_top_log"},
        {"cmd": "dumpsys cpuinfo", "output": "aos_sys_cpuinfo.log"},
        {"cmd": "ps -A", "output": "aos_ps.log"},
        {"cmd": "cat /proc/cpuinfo", "output": "aos_proc_cpuinfo.log"},
        {"cmd": "dumpsys meminfo", "output": "aos_meminfo.log"},
    ]
    qnx_cmds = [
        {"cmd": "top -b -i 1", "output": "qnx_top.log"},
        {"cmd": "hogs -i 1", "output": "qnx_hogs.log"},
        {"cmd": "showmem -s", "output": "qnx_showmem.log"},
    ]
    mp = Performance(deviceID="", comport="", username="zeekr", password="Aa123123")
    mp.android_nfs_iospeed

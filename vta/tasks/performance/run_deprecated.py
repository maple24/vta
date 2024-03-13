# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

import os

from loguru import logger
from performance_deprecated import Performance

logger.add(
    os.path.join(os.path.dirname(__file__), "performance.log"),
    backtrace=True,
    diagnose=False,
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    rotation="1 week",
)

if __name__ == "__main__":
    loop = 2
    outputname = "perf_io.csv"
    output = os.path.join(os.path.dirname(__file__), "result", outputname)
    nfs_disk = ["/data/vendor/nfs/mount", "/data/vendor/nfs/nfs_log"]
    aos_cmds = [
        {"cmd": "top -b -n 1", "file": "aos_top.log"},
        {"cmd": "dumpsys cpuinfo", "file": "aos_sys_cpuinfo.log"},
        {"cmd": "ps -A", "file": "aos_ps.log"},
        {"cmd": "cat /proc/cpuinfo", "file": "aos_proc_cpuinfo.log"},
        {"cmd": "dumpsys meminfo", "file": "aos_meminfo.log"},
        {"cmd": "df -h", "file": "aos_df.log"},
    ]
    qnx_cmds = [
        {"cmd": "cat /mnt/Buildinfo.txt", "file": "qnx_buildinfo.log"},
        {"cmd": "top -b -i 1", "file": "qnx_top.log"},
        {"cmd": "hogs -i 1", "file": "qnx_hogs.log"},
        {"cmd": "showmem -s", "file": "qnx_showmem.log"},
        {"cmd": "slog2info | grep devb", "file": "qnx_slogdevb.log"},
        {"cmd": "df -h", "file": "qnx_df.log"},
    ]
    mp = Performance(
        deviceID="c35364f", comport="com5", username="zeekr", password="Aa123123"
    )
    results = []
    for i in range(loop):
        res = {}
        # android nfs
        for d in nfs_disk:
            res.update(mp.android_nfs_iospeed(disk=d, type="w"))
            res.update(mp.android_nfs_iospeed(disk=d, type="r"))

        # android ufs
        res.update(mp.android_ufs_iospeed())
        results.append(res)
    Performance.dict2csv(file=output, data=results)

    # qnx ufs: blocked

    # android cpu mem
    for i in aos_cmds:
        mp.android_cpu_mem(cmd=i["cmd"], file=i["file"])

    # qnx cpu mem
    for i in qnx_cmds:
        mp.qnx_cpu_mem(cmd=i["cmd"], file=i["file"])

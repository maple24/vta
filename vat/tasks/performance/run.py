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
    # android nfs
    for i in nfs_disk:
        results.append(mp.android_nfs_iospeed(disk=i, type="w"))
        results.append(mp.android_nfs_iospeed(disk=i, type="r"))

    # android ufs
    results.append(mp.android_ufs_iospeed())
    print(results)
    Performance.dict2csv(file='perf.csv', data=results)

    # qnx ufs: blocked

    # android cpu mem
    for i in aos_cmds:
        mp.android_cpu_mem(cmd=i["cmd"], file=i["file"])

    # qnx cpu mem
    for i in qnx_cmds:
        mp.qnx_cpu_mem(cmd=i["cmd"], file=i["file"])

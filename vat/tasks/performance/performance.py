import os
import sys
from loguru import logger

sys.path.append(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-4]))

from vat.library.GenericHelper import GenericHelper
from vat.library.SystemHelper import SystemHelper

BIN = os.path.join(os.path.dirname(__file__), "bin")


class Performance:
    def __init__(
        self, deviceID: str, comport: str, username: str, password: str
    ) -> None:
        self.deviceID = deviceID
        self.comport = comport
        self.username = username
        self.password = password

    def android_nfs_iospeed(self, disk: str, type: str = "w"):
        """test android nfs i/o speed by `dd` command for `nfs_log` and `mount` disk
        write: dd if=/dev/zero of=/data/vendor/nfs/nfs_log/test.image count=100 bs=1440k
        read: dd if={}/test.image of=/dev/null count=100 bs=1440k
        """
        pattern = "[0-9]+\sbytes\stransferred\sin\s([0-9]+(\.[0-9]{1,3})?)\ssecs\s\(([0-9]+)\sbytes\/sec\)"
        if type == "w":
            logger.info(f"Testing write speed of {disk}")
            data = GenericHelper.prompt_command(
                f"adb -s {self.deviceID} shell dd if=/dev/zero of={disk}/test.image count=100 bs=1440k"
            )
            res, matched = GenericHelper.match_string(pattern=pattern, data=data)
        elif type == "r":
            logger.info(f"Testing read speed of {disk}")
            data = GenericHelper.prompt_command(
                f"adb -s {self.deviceID} shell dd if={disk}/test.image of=/dev/null count=100 bs=1440k"
            )
            res, matched = GenericHelper.match_string(pattern=pattern, data=data)
        else:
            logger.warning(f"Unknown test type: {type}")

    def android_ufs_iospeed(self, disk: str = "/data") -> dict:
        """test android ufs i/o speed by `tiotest_la` tool
        ./data/tiotest_la.out -t 1 -d /data/ -b 2097152 -f 200 -L
        return: {'Write': '354.371', 'Read': '662.324'}
        TBD: return files
        """
        pattern = "\| (Write|Read)\s+.*\s+([0-9\.]+)\sMB/s"
        tiotest = os.path.join(BIN, "tiotest_la")
        androidPath = "/data"
        tiotest_android = f"{androidPath}/tiotest_la"
        SystemHelper.PC2Android(
            localPath=tiotest, androidPath=androidPath, deviceID=self.deviceID
        )
        GenericHelper.prompt_command(
            f"adb -s {self.deviceID} shell chmod +x {tiotest_android}"
        )
        data = GenericHelper.prompt_command(
            f"adb -s {self.deviceID} shell {tiotest_android} -t 1 -d {disk} -b 2097152 -f 200 -L",
            timeout=20.0,
        )
        res, matched = GenericHelper.match_string(pattern=pattern, data=data)
        if res:
            return {matched[0][0]: matched[0][1], matched[1][0]: matched[1][1]}

    def qnx_ufs_iospeed(self):
        """test android ufs i/o speend by `tiotest_qnx` tool
        on -p 63 /var/log/tiotest_qnx -t 1 -d /otaupdate -b 2097152 -f 200 -L
        """
        tiotest = os.path.join(BIN, "tiotest_qnx")
        tiotest_qnx = f"{SystemHelper.disk_mapping.get('qnx')}/tiotest_qnx"
        SystemHelper.PC2QNX(
            comport=self.comport,
            localPath=tiotest,
            deviceID=self.deviceID,
            username=self.username,
            password=self.password,
        )
        SystemHelper.serial_command(f"chmod +x {tiotest_qnx}")
        data = SystemHelper.serial_command(
            f"on -p 63 {tiotest_qnx} -t 1 -d /var -b 2097152 -f 200 -L"
        )
        res, matched = GenericHelper.match_string(
            pattern="\| (Write|Read)\s+.*\s+([0-9\.]+)\sMB/s", data=data
        )
        if res:
            return {matched[0][0]: matched[0][1], matched[1][0]: matched[1][1]}

    def android_cpu_mem():
        """
        cmd:
        1. android: top -b -n 1
        2. android: dumpsys cpuinfo
        3. android: ps -A
        4. android: cat /proc/cpuinfo
        5. android: dumpsys meminfo
        output: files
        """
        cmds = [
            "top -b -n 1 > top.log",
            "dumpsys cpuinfo > sys_cpuinfo.log",
            "ps -A > ps.log",
            "cat /proc/cpuinfo > proc_cpuinfo.log",
            "dumpsys meminfo > meminfo.log",
        ]
        log_folder = SystemHelper.disk_mapping.get("android")
        GenericHelper.prompt_command()

    def qnx_cpu_mem():
        """
        cmd:
        1. qnx: top -b -i 1
        2. qnx: hogs -i 1
        3. qnx: showmem -s
        output: files
        """
        cmds = [
            "top -b -i 1 > top.log",
            "hogs -i 1 > hogs.log",
            "showmem -s > showmem.log",
        ]


if __name__ == "__main__":
    p = Performance(
        deviceID="605712f4", comport="com8", username="zeekr", password="Aa123123"
    )
    res = p.android_ufs_iospeed()
    print(res)

import os
import sys

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

    def nfs_iospeed():
        """test android nfs i/o speend by `dd` command
        dd if=/dev/zero of=/data/test.image count=100 bs=1440k
        """
        ...

    def android_ufs_iospeed(self) -> dict:
        """test android ufs i/o speend by `tiotest_la` tool
        ./data/tiotest_la.out -t 1 -d /data/ -b 2097152 -f 200 -L
        return: {'Write': '354.371', 'Read': '662.324'}
        """
        tiotest = os.path.join(BIN, "tiotest_la")
        SystemHelper.PC2Android(
            localPath=tiotest, androidPath="/data", deviceID=self.deviceID
        )
        GenericHelper.prompt_command(
            f"adb -s {self.deviceID} shell chmod +x /data/tiotest_la"
        )
        data = GenericHelper.prompt_command(
            f"adb -s {self.deviceID} shell /data/tiotest_la -t 1 -d /data/ -b 2097152 -f 200 -L",
            timeout=20.0,
        )
        res, matched = GenericHelper.match_string(
            pattern="\| (Write|Read)\s+.*\s+([0-9\.]+)\sMB/s", data=data
        )
        if res:
            return {
                matched[0][0]: matched[0][1],
                matched[1][0]: matched[1][1]
            }

    def qnx_ufs_iospeed():
        """test android ufs i/o speend by `tiotest_qnx` tool
        on -p 63 /var/log/tiotest_qnx -t 1 -d /otaupdate -b 2097152 -f 200 -L
        """
        tiotest = os.path.join(BIN, "tiotest_qnx")

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

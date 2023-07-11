import os
import sys
from loguru import logger
from typing import Union, List
import csv

sys.path.append(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-4]))

from vat.library.GenericHelper import GenericHelper
from vat.library.SystemHelper import SystemHelper

BIN = os.path.join(os.path.dirname(__file__), "bin")
RESULT = os.path.join(os.path.dirname(__file__), "result")


class Performance:
    def __init__(
        self, deviceID: str, comport: str, username: str, password: str
    ) -> None:
        self.deviceID = deviceID
        self.comport = comport
        self.username = username
        self.password = password
        if not os.path.exists(RESULT):
            os.mkdir(RESULT)
        if not os.path.exists(BIN):
            logger.error("Binary folder does not exist!")
            sys.exit(1)

    def android_nfs_iospeed(self, disk: str, type: str = "w") -> dict:
        """test android nfs i/o speed by `dd` command for `nfs_log` and `mount` disk
        write: dd if=/dev/zero of=/data/vendor/nfs/nfs_log/test.image count=100 bs=1440k
        read: dd if={}/test.image of=/dev/null count=100 bs=1440k
        """
        pattern = "\d+\sbytes\s\(.+\)\scopied,\s.+,\s(.+)"
        if type == "w":
            logger.info(f"Testing write speed of {disk}")
            data = GenericHelper.prompt_command(
                f"adb -s {self.deviceID} shell dd if=/dev/zero of={disk}/test.image count=100 bs=1440k"
            )
            res, matched = GenericHelper.match_string(pattern=pattern, data=data)
            if res:
                return {f"nfs_{disk}_Write": matched[0][0]}
        elif type == "r":
            logger.info(f"Testing read speed of {disk}")
            data = GenericHelper.prompt_command(
                f"adb -s {self.deviceID} shell dd if={disk}/test.image of=/dev/null count=100 bs=1440k"
            )
            res, matched = GenericHelper.match_string(pattern=pattern, data=data)
            if res:
                return {f"nfs_{disk}_Read": matched[0][0]}
        else:
            logger.warning(f"Unknown test type: {type}")

    def android_ufs_iospeed(self, disk: str = "/data") -> dict:
        """test android ufs i/o speed by `tiotest_la` tool
        ./data/tiotest_la.out -t 1 -d /data/ -b 2097152 -f 200 -L
        return: {'Write': '354.371', 'Read': '662.324'}
        """
        pattern = "\| (Write|Read)\s+.*\s+([0-9\.]+\sMB/s)"
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
            return {
                f"aos_ufs_{matched[0][0]}": matched[0][1],
                f"aos_ufs_{matched[1][0]}": matched[1][1],
            }

    def qnx_ufs_iospeed(self, disk: str = "/data") -> dict:
        """test android ufs i/o speend by `tiotest_qnx` tool
        on -p 63 /var/log/tiotest_qnx -t 1 -d /otaupdate -b 2097152 -f 200 -L
        """
        pattern = "\| (Write|Read)\s+.*\s+([0-9\.]+\sMB/s)"
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
            f"on -p 63 {tiotest_qnx} -t 1 -d {disk} -b 2097152 -f 200 -L"
        )
        res, matched = GenericHelper.match_string(pattern=pattern, data=data)
        if res:
            return {
                f"qnx_ufs_{matched[0][0]}": matched[0][1],
                f"qnx_ufs_{matched[1][0]}": matched[1][1],
            }

    def android_cpu_mem(self, cmd: str, file: str) -> None:
        """
        cmd: top -b -n 1
        output: aos_top.log
        """
        tmp = "/sdcard"
        output = f"{tmp}/{file}"
        GenericHelper.prompt_command(f'adb -s {self.deviceID} shell "{cmd} > {output}"')
        SystemHelper.Android2PC(
            androidPath=output, localPath=RESULT, deviceID=self.deviceID
        )

    def qnx_cpu_mem(self, cmd: str, file: str) -> None:
        """
        cmd: top -b -i 1
        output: qnx_top.log
        """
        tmp = "/var"
        output = f"{tmp}/{file}"
        SystemHelper.serial_command(
            cmd=f"{cmd} > {output}",
            comport=self.comport,
            username=self.username,
            password=self.password,
        )
        SystemHelper.QNX2PC(
            comport=self.comport,
            qnxPath=output,
            localPath=RESULT,
            deviceID=self.deviceID,
            username=self.username,
            password=self.password,
        )

    @staticmethod
    def dict2csv(file: str, data: Union[List[dict], dict]) -> None:
        if isinstance(data, list):
            fieldnames = data[0].keys()
        else:
            fieldnames = data.keys()
            data = [data]
        with open(file, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        logger.success("Succeed to write to csv file!")


if __name__ == "__main__":
    # p = Performance(
    #     deviceID="605712f4", comport="com8", username="zeekr", password="Aa123123"
    # )
    # res = p.android_ufs_iospeed()
    # print(res)
    a = [
        {"nfs_/data/vendor/nfs/mount_Write": "59 M/s"},
        {"nfs_/data/vendor/nfs/mount_Read": "52 M/s"},
        {"nfs_/data/vendor/nfs/nfs_log_Write": "444 M/s"},
        {"nfs_/data/vendor/nfs/nfs_log_Read": "7.5 G/s"},
        {"ufs_/data_Write": "358.693 MB/s", "ufs_/data_Read": "678.157 MB/s"},
    ]
    Performance.dict2csv(file="yesy.csv", data=a)

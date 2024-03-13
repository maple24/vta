# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

import os
import re

import matplotlib.pyplot as plt
from loguru import logger


class Performance:
    # RESULT = os.path.join('.', "result") # for pyinstaller
    RESULT = os.path.join(os.path.dirname(__file__), "result")
    if not os.path.exists(RESULT):
        os.mkdir(RESULT)

    def __init__(self, per_type) -> None:
        self.per_type = per_type
        self.type_result = os.path.join(self.RESULT, self.per_type)
        if not os.path.exists(self.type_result):
            os.mkdir(self.type_result)

    @property
    def seperator_pattern(self):
        mappings = {
            "qnxcpu": r"\d+ processes; \d+ threads;",
            "qnxmem": r"\*+\s*E\s*N\s*D\s*\*+",
            "aoscpu": r"Tasks.*?zombie",
            "aosmem": r"RAM.*?slab",
        }
        return mappings.get(self.per_type)

    def match_pattern(self, process):
        mappings = {
            "qnxcpu": r"(\d+\.\d+)%\s" + process,
            "qnxmem": process + r"\s\|.*?\|.*?\|\s+(\d+)\s\|",
            "aoscpu": r"\s[A-Z]+\s+(\d+\.\d+).*?" + process,
            "aosmem": r".*?K.*?K\s+(\d+)K.*?" + process,
        }
        return mappings.get(self.per_type)

    @property
    def units(self):
        mappings = {
            "qnxcpu": "%",
            "qnxmem": "KB",
            "aoscpu": "%",
            "aosmem": "K",
        }
        return mappings.get(self.per_type)

    @staticmethod
    def remove_escape_characters(text):
        return re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", text)

    @staticmethod
    def content_splits(file: str, separator_pattern: str) -> list[str]:
        chunks = []
        with open(file, "r") as file:
            content = file.read()
            cleaned_content = Performance.remove_escape_characters(content)
            chunks = re.split(separator_pattern, cleaned_content)
        return chunks

    @staticmethod
    def data_extraction(chunks: list, pattern: str):
        if len(chunks) <= 1:
            logger.error("Chunks are empty! Terminated!")
            exit(1)
        data = []
        for chunk in chunks:
            matches = re.findall(pattern, chunk)
            if matches:
                data.append(sum(map(float, matches)))
        logger.debug(data)
        return data

    def save_plot(
        self,
        y_data: list,
        x_data: list = None,
        y_label: str = "default",
        title: str = "default",
    ):
        file_name = f"{os.path.join(self.type_result, title)}.png"
        if not y_data:
            logger.warning(f"{title} data is empty!")
            return
        if not x_data:
            x_data = [i for i in range(len(y_data))]
        try:
            plt.figure(figsize=(10, 5))
            plt.plot(x_data, y_data)
            plt.ylabel(f"{y_label} ({self.units})")
            plt.title(title)

            # mark max point and average line
            max_index = y_data.index(max(y_data))
            average = sum(y_data) / len(y_data)
            plt.scatter(
                max_index, max(y_data), color="red", label="Max Point", marker="o"
            )
            plt.text(
                max_index,
                max(y_data),
                f"Max Value: {max(y_data): .2f}",
                color="red",
                ha="right",
                va="bottom",
            )
            plt.axhline(y=average, color="green", linestyle="--", label="Average Line")
            plt.text(
                0.5,
                average,
                f"Average Value: {average: 0.2f}",
                color="green",
                va="bottom",
            )
            # save
            plt.savefig(file_name)
            plt.close()
        except Exception as e:
            logger.exception(e)
            return
        else:
            logger.success(f"save file to {file_name}")


if __name__ == "__main__":
    # qnx_cpu
    file = os.path.join(os.path.dirname(__file__), "qnx_cpu.txt")
    mp = Performance("qnxcpu")
    per_type = "QNX CPU Usage"
    processes = ["qvm", "AudioSystemControllerDeamon"]
    chunks = Performance.content_splits(
        file, separator_pattern=r"\d+ processes; \d+ threads;"
    )
    for process in processes:
        pattern = r"(\d+\.\d+)%\s" + process
        y_data = Performance.data_extraction(chunks, pattern)
        mp.save_plot(y_data, y_label=per_type, title=f"{per_type}_{process}")

    # qnx_mem
    file = os.path.join(os.path.dirname(__file__), "qnx_mem.txt")
    mp = Performance("qnxmem")
    per_type = "QNX Memory Usage"
    processes = ["diag_service", "procnto-smp-instr"]
    chunks = Performance.content_splits(
        file, separator_pattern=r"\*+\s*E\s*N\s*D\s*\*+"
    )
    for process in processes:
        pattern = process + r"\s\|.*?\|.*?\|\s+(\d+)\s\|"
        y_data = Performance.data_extraction(chunks, pattern)
        mp.save_plot(y_data, y_label=per_type, title=f"{per_type}_{process}")

    # aos_cpu
    file = os.path.join(os.path.dirname(__file__), "aos_cpu.txt")
    mp = Performance("aoscpu")
    per_type = "AOS CPU Usage"
    processes = ["system_server", "[system]"]
    chunks = Performance.content_splits(file, separator_pattern=r"Tasks.*?zombie")
    for process in processes:
        pattern = r"\s[A-Z]+\s+(\d+\.\d+).*?" + process
        y_data = Performance.data_extraction(chunks, pattern)
        mp.save_plot(y_data, y_label=per_type, title=f"{per_type}_{process}")

    # aos_mem
    file = os.path.join(os.path.dirname(__file__), "aos_mem.txt")
    mp = Performance("aosmem")
    per_type = "AOS Memory Usage"
    processes = ["system_server", "/system/bin/audioserver"]
    chunks = Performance.content_splits(file, separator_pattern="RAM.*?slab")
    for process in processes:
        pattern = r".*?K.*?K\s+(\d+)K.*?" + process
        y_data = Performance.data_extraction(chunks, pattern)
        mp.save_plot(
            y_data, y_label=per_type, title=f"{per_type}_{process.replace('/', '_')}"
        )

import os
import sys
import re
from loguru import logger
import matplotlib.pyplot as plt


class Performance:
    RESULT = os.path.join(os.path.dirname(__file__), "result")

    @staticmethod
    def content_splits(file: str, separator_pattern: str) -> list[str]:
        # qnxcpu: separator_pattern = r"\d+ processes; \d+ threads;"
        # qnxmem: separator_pattern = r'\*+\s*E\s*N\s*D\s*\*+'
        # aoscpu: separator_pattern = r''
        # aosmem: separator_pattern = r'RAM.*?slab'
        chunks = []
        with open(file, "r") as file:
            content = file.read()
            chunks = re.split(separator_pattern, content)
        return chunks

    @staticmethod
    def data_extraction(chunks: list, pattern: str):
        # qnxcpu: pattern = r"(\d+\.\d+)%\s" + process
        # qnxmem: pattern = process + r"\s\|.*?\|.*?\|\s+(\d+)\s\|"
        # aoscpu:
        # aosmem: pattern = r".*?K.*?K\s+(\d+)K.*?" + process
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

    @staticmethod
    def save_plot(
        y_data: list,
        x_data: list = None,
        y_label: str = "default",
        title: str = "default",
    ):
        file_name = f"{os.path.join(Performance.RESULT, title)}.png"
        if not y_data:
            logger.warning(f"{title} data is empty!")
            return
        if not x_data:
            x_data = [i for i in range(len(y_data))]
        try:
            plt.figure(figsize=(10, 5))
            plt.plot(x_data, y_data)
            plt.ylabel(y_label)
            plt.title(title)

            # mark max point and average line
            max_index = y_data.index(max(y_data))
            average = sum(y_data) / len(y_data)
            plt.scatter(
                max_index, max(y_data), color="red", label="Max Point", marker="o"
            )
            plt.axhline(y=average, color="green", linestyle="--", label="Average Line")

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
    # file = os.path.join(os.path.dirname(__file__), "qnx_cpu.txt")
    # per_type = "QNX CPU Usage"
    # processes = ["qvm", "AudioSystemControllerDeamon"]
    # chunks = Performance.content_splits(
    #     file, separator_pattern=r"\d+ processes; \d+ threads;"
    # )
    # for process in processes:
    #     pattern = r"(\d+\.\d+)%\s" + process
    #     y_data = Performance.data_extraction(
    #         chunks, pattern
    #     )
    #     Performance.save_plot(y_data, y_label=per_type, title=f"{per_type}_{process}")

    # qnx_mem
    # file = os.path.join(os.path.dirname(__file__), "qnx_mem.txt")
    # per_type = "QNX Memory Usage"
    # processes = ["diag_service", "procnto-smp-instr"]
    # chunks = Performance.content_splits(
    #     file, separator_pattern=r"\*+\s*E\s*N\s*D\s*\*+"
    # )
    # for process in processes:
    #     pattern = process + r"\s\|.*?\|.*?\|\s+(\d+)\s\|"
    #     y_data = Performance.data_extraction(chunks, pattern)
    #     Performance.save_plot(y_data, y_label=per_type, title=f"{per_type}_{process}")

    # aos_cpu
    file = os.path.join(os.path.dirname(__file__), "aos_cpu.txt")
    per_type = "AOS CPU Usage"
    processes = []
    chunks = Performance.content_splits(
        file, separator_pattern=r"Tasks.*?total.*?running.*?sleeping.*?stopped.*?zombie"
    )

    # aos_mem
    # file = os.path.join(os.path.dirname(__file__), "aos_mem.txt")
    # per_type = "AOS Memory Usage"
    # processes = ["system_server", "/system/bin/audioserver"]
    # chunks = Performance.content_splits(
    #     file, separator_pattern="RAM.*?slab"
    # )
    # for process in processes:
    #     pattern = r".*?K.*?K\s+(\d+)K.*?" + process
    #     y_data = Performance.data_extraction(chunks, pattern)
    #     Performance.save_plot(y_data, y_label=per_type, title=f"{per_type}_{process.replace('/', '_')}")

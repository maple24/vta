import os
import sys
import re
from loguru import logger
import matplotlib.pyplot as plt


class Performance:
    RESULT = os.path.join(os.path.dirname(__file__), "result")

    @staticmethod
    def content_splits(file: str, separator_pattern: str) -> list[str]:
        # separator_pattern = r"\d+ processes; \d+ threads;"
        chunks = []
        with open(file, "r") as file:
            content = file.read()
            chunks = re.split(separator_pattern, content)
        return chunks

    @staticmethod
    def qnx_cpu_data_extraction(chunks: list, process: str) -> list:
        pattern = r"(\d+\.\d+)%\s" + process
        data = []
        for chunk in chunks:
            matches = re.findall(pattern, chunk)
            if matches:
                data.append(sum(map(float, matches)))
        return data

    @staticmethod
    def save_plot(
        y_data: list,
        x_data: list = None,
        y_label="CPU Usage (%)",
        title: str = "default",
    ):
        file_name = f"{os.path.join(Performance.RESULT, title)}.png"
        if not x_data:
            x_data = [i for i in range(len(y_data))]
        try:
            plt.figure(figsize=(10, 5))
            plt.plot(x_data, y_data, label="CPU Usage")
            plt.ylabel(y_label)
            plt.title(title)

            # mark max point and average line
            max_index = y_data.index(max(y_data))
            average = sum(y_data) / len(y_data)
            plt.scatter(max_index, max(y_data), color='red', label='Max Point', marker='o')
            plt.axhline(y=average, color='green', linestyle='--', label='Average Line')

            # save
            plt.savefig(file_name)
            plt.close()
        except Exception as e:
            logger.exception(e)
        else:
            logger.success(f"save file to {file_name}")


if __name__ == "__main__":
    file = os.path.join(os.path.dirname(__file__), "qnx_cpu.txt")
    
    # qnx_cpu
    processes = ["qvm", "AudioSystemControllerDeamon"]
    chunks = Performance.content_splits(
        file, separator_pattern=r"\d+ processes; \d+ threads;"
    )
    for process in processes:
        y_data = Performance.qnx_cpu_data_extraction(
            chunks, process=process
        )
        Performance.save_plot(y_data, title=process)

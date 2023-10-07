import os
import sys
import re
from loguru import logger
import matplotlib.pyplot as plt


class Performance:
    RESULT = os.path.join(os.path.dirname(__file__), "result")

    @staticmethod
    def split_contents(file: str, separator_pattern: str) -> list[str]:
        # separator_pattern = r"\d+ processes; \d+ threads;"
        chunks = []
        with open(file, "r") as file:
            content = file.read()
            chunks = re.split(separator_pattern, content)
        return chunks

    @staticmethod
    def data_extraction(chunks: list, pattern: str) -> list:
        # pattern = r"(\d+\.\d+)%\sAudioSystemControllerDeamon"
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
            plt.xlabel("Time (s)")
            plt.ylabel(y_label)
            plt.title(title)
            plt.savefig(file_name)
            plt.close()
        except Exception as e:
            logger.exception(e)
        else:
            logger.success(f"save file to {file_name}")


if __name__ == "__main__":
    file = os.path.join(os.path.dirname(__file__), "qnx_cpu.txt")
    chunks = Performance.split_contents(
        file, separator_pattern=r"\d+ processes; \d+ threads;"
    )
    y_data = Performance.data_extraction(
        chunks, pattern=r"(\d+\.\d+)%\sAudioSystemControllerDeamon"
    )
    Performance.save_plot(y_data)

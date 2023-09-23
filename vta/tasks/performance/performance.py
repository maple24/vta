import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
import sys
import os
import time
from loguru import logger
from typing import Callable
import subprocess
import re
from pydantic import BaseModel
from enum import Enum

sys.path.append(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-4]))

from vta.library.GenericHelper import GenericHelper
from vta.library.SystemHelper import SystemHelper


class Performance:
    RESULT = os.path.join(os.path.dirname(__file__), "result")

    def __init__(self, duration=30, callback: str = None):
        self.duration = duration
        self.fig, self.ax = plt.subplots()
        (self.line,) = self.ax.plot([], [], lw=2)
        self.x_data = []
        self.y_data = []
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("CPU Usage (%)")
        self.ax.set_title("CPU Usage of system_server (Real-time)")

        operation_map = {
            "qnx_cpu": Performance.get_qnx_cpu_usage,
            "qnx_memory": Performance.get_qnx_memory_usage,
            "aos_cpu": Performance.get_aos_cpu_usage,
            "aos_memory": Performance.get_aos_memory_usage,
            "test": Performance.test,
        }
        self.callback = operation_map.get(callback, None)
        if not self.callback:
            logger.error("Unknown callback function!")
            exit(1)

        self.ani = FuncAnimation(
            self.fig, self.update_plot, interval=1000, cache_frame_data=False
        )
        self.fig.canvas.mpl_connect("close_event", self.on_close)

    def update_plot(self, i):
        elapsed_time = time.time() - self.start_time
        if elapsed_time >= self.duration:
            self.ani.event_source.stop()
            self.save_plot()
        else:
            data = self.callback()
            if data:
                self.x_data.append(elapsed_time)
                self.y_data.append(data)
                self.line.set_data(self.x_data, self.y_data)
                self.ax.relim()
                self.ax.autoscale_view()

    def save_plot(self):
        plt.savefig(os.path.join(self.RESULT, "cpu_usage_plot.png"))
        plt.close()

    def on_close(self, event):
        self.save_plot()

    def animate(self):
        self.start_time = time.time()
        plt.show()

    @staticmethod
    def get_qnx_cpu_usage():
        command = "top -n 1 -b | grep system_server"
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        match = re.search(r"system_server.*?(\d+\.\d+)%", result.stdout)
        if match:
            return float(match.group(1))
        else:
            return None

    @staticmethod
    def get_qnx_memory_usage():
        ...

    @staticmethod
    def get_aos_cpu_usage():
        ...

    @staticmethod
    def get_aos_memory_usage():
        ...

    @staticmethod
    def test():
        return random.choice([1, 2])


if __name__ == "__main__":
    myplot = Performance(duration=10, callback="test")
    myplot.animate()

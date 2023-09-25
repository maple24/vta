import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
import sys
import os
import time
import threading
import numpy as np
from loguru import logger
from typing import Callable

sys.path.append(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-4]))

from vta.library.GenericHelper import GenericHelper
from vta.library.SystemHelper import SystemHelper
from vta.api.PuttyHelper import PuttyHelper


class Performance:
    RESULT = os.path.join(os.path.dirname(__file__), "result")
    dputty = {
        "putty_enabled": False,
        "putty_comport": "COM5",
        "putty_baudrate": 115200,
        "putty_username": "zeekr",
        "putty_password": "Aa123123",
    }

    def __init__(
        self,
        duration=30,
        callback: str = None,
    ) -> None:
        self.mputty = PuttyHelper()
        self.mputty.connect(self.dputty)
        if not os.path.exists(self.RESULT):
            os.mkdir(self.RESULT)

        self.process = None
        self.duration = duration
        self.fig, self.ax = plt.subplots()
        (self.line,) = self.ax.plot([], [], lw=2)
        self.x_data = []
        self.y_data = []
        self.max_annotation = None
        self.avg_line = None
        self.ax.set_xlabel("Time (s)")

        operation_map = {
            "qnx_cpu": self.get_qnx_cpu_usage,
            "qnx_memory": self.get_qnx_memory_usage,
            "aos_cpu": self.get_aos_cpu_usage,
            "aos_memory": self.get_aos_memory_usage,
            "test": self.test,
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
            logger.success(f"Reached time out! {self.duration}")
            self.ani.event_source.stop()
            self.save_plot()
        else:
            data = self.callback()
            if data:
                self.x_data.append(elapsed_time)
                self.y_data.append(data)
                self.line.set_data(self.x_data, self.y_data)
                self.update_annotations()
                self.ax.relim()
                self.ax.autoscale_view()

    def save_plot(self):
        self.fig.savefig(os.path.join(self.RESULT, f"cpu_usage_{self.process}.png"))
        plt.close()

    def on_close(self, event):
        self.save_plot()
        self.mputty.disconnect()

    def animate(self):
        self.start_time = time.time()
        plt.show()

    def update_annotations(self):
        if self.max_annotation:
            self.max_annotation.remove()
        if self.avg_line:
            self.avg_line.remove()

        max_value = max(self.y_data)
        avg_value = np.mean(self.y_data)
        max_index = self.y_data.index(max_value)

        self.max_annotation = self.ax.scatter(
            self.x_data[max_index],
            max_value,
            c="red",
            marker="o",
            s=100,
            label=f"Max: {max_value:.2f}%",
        )
        self.avg_line = self.ax.axhline(
            y=avg_value, color="red", linestyle="--", label=f"Avg: {avg_value:.2f}%"
        )

    def get_qnx_cpu_usage(self):
        # 3010567     6  10 Sem       1:16:29   5.59% qvm
        value = 0
        self.process = "AudioSystemControllerDeamon"
        command = f"top -i 1 -b | grep {self.process}"
        self.ax.set_ylabel("CPU Usage (%)")
        self.ax.set_title(f"CPU Usage of {self.process} (Real-time)")
        pattern = r"(\d+\.\d+)%"
        data = self.mputty.send_command_and_return_traces(
            cmd=command, wait=2, login=False
        )
        res, matched = GenericHelper.match_string(pattern, data)
        if not res:
            logger.warning("Nothing matched!")
        else:
            for i in matched:
                value += float(i[0])
            return value

    def get_qnx_memory_usage(self):
        ...

    def get_aos_cpu_usage(self):
        ...

    def get_aos_memory_usage(self):
        ...

    def test(self):
        return random.choice([1, 2])


if __name__ == "__main__":
    myplot = Performance(
        duration=10,
        callback="test",
    )
    myplot.animate()

from vehicle import Vehicle
import os
from loguru import logger

logger.add(
    os.path.join(os.path.dirname(__file__), "vehicle.log"),
    backtrace=True,
    diagnose=False,
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    rotation="1 week",
)


if __name__ == "__main__":
    protoname = "com.platform.vehicle.proto"
    templatename = "vehicle_template.csv"
    outputname = "vehicle_outputs.csv"
    proto = os.path.join(os.path.dirname(__file__), protoname)
    template = os.path.join(os.path.dirname(__file__), templatename)
    output = os.path.join(os.path.dirname(__file__), outputname)
    dputty = {
        "putty_enabled": True,
        "putty_comport": "COM11",
        "putty_baudrate": 115200,
        "putty_username": "zeekr",
        "putty_password": "Aa123123",
    }
    mv = Vehicle(dputty=dputty, canoe=True, proto=proto)
    data = Vehicle.csv2dict(template)

    results = []
    for row in data:
        results.append(mv.run(row, bus="CAN"))
    Vehicle.dict2csv(output, results)

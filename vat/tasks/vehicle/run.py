from vehicle import Vehicle
import os


if __name__ == "__main__":
    protoname = "com.platform.vehicle.proto"
    templatename = "vehicle_template.csv"
    outputname = 'vehicle_outputs.csv'
    proto = os.path.join(os.path.dirname(__file__), protoname)
    template = os.path.join(os.path.dirname(__file__), templatename)
    output = os.path.join(os.path.dirname(__file__), outputname)
    dputty = {
        "putty_enabled": True,
        "putty_comport": "COM11",
        "putty_baudrate": 115200,
        "putty_username": "root",
        "putty_password": "6679836772",
    }
    mv = Vehicle(dputty=dputty, canoe=True, proto=proto)
    data = Vehicle.csv2dict(template)

    results = []
    for row in data:
        results.append(mv.run(row, bus='CAN'))
    Vehicle.dict2csv(output, results)

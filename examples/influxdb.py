import sys
from mikrotik_bt5 import MikrotikBT5
import asyncio
import datetime, time
import struct

from influxdb import InfluxDBClient

"""
    Scanner example. Uplaod all scanned packets to influxdb
    This will run scanner forever (or until interupted by Ctrl^C)
"""


server_ip = "192.168.88.10"
server_port = 8086
influx_user = "root"
influx_pwd = ""
influx_db = "Sandbox"

def mkpt(device, key, beacon, timestr):
    t  = beacon.temperature
    ax = beacon.acceleration.x
    ay = beacon.acceleration.y
    az = beacon.acceleration.z
    u  = beacon.uptime
    b = beacon.battery
    ri = beacon.rssi

    point = {
        "measurement": key,
        "tags": {
            "device": device,
        },
        "time": timestr,
        "fields": {
            "accel_x": ax,
            "accel_y": ay,
            "accel_z": az,
            "uptime": u,
            "battery": b,
            "rssi": ri,
        }
    }

    if beacon.hasTemperature():
        point["fields"]["temperature"] = t

    return point

def on_scan(beacon, device):
    print(f"  {device.address}")
    pts = []

    client = InfluxDBClient(server_ip, server_port, influx_user, influx_pwd, influx_db)
    client.create_database(influx_db)

    tim = now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).timestamp()

    strtim = datetime.datetime.utcfromtimestamp(tim).strftime('%Y-%m-%dT%H:%M:%SZ') # ISO 8601 UTC
    pts.append(mkpt(device.address, "bt5-tag", beacon, strtim))

    client.write_points(pts)

async def main(argv):
    scanner = MikrotikBT5(on_scan)
    await scanner.start_scan()
    while (True): # Run forever
        await asyncio.sleep(1)
    await scanner.stop_scan()


if __name__== "__main__":
    try:
        asyncio.run(main(sys.argv[1:]))
    except KeyboardInterrupt:
        print("User interupted.")

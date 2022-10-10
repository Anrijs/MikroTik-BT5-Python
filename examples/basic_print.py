import sys
from mikrotik_bt5 import MikrotikBT5
import asyncio

"""
    Scanner example. Uplaod all scanned packets to influxdb
    This will run scanner forever (or until interupted by Ctrl^C)
"""


def on_scan(beacon, device):
    print("---------------------------")
    print(f"  {device.address}")
    print("---------------------------")

    if beacon.hasTemperature():
        print(f"  temperature:  {beacon.temperature:.2f} \u00b0C")
    print( "  acceleration:")
    print(f"      x:         {beacon.acceleration.x:.2f} m/s^2")
    print(f"      y:         {beacon.acceleration.y:.2f} m/s^2")
    print(f"      z:         {beacon.acceleration.z:.2f} m/s^2")
    print(f"  uptime:        {beacon.uptime}")
    print(f"  battery:       {beacon.battery} %")
    print()

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

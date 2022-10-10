import asyncio
import struct
import math
from enum import IntEnum

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from dataclasses import dataclass, field


class BeaconType(IntEnum):
    MIKROTIK = 1


class BaseBeacon:
    rssi: int = -1

    def __init__(self, type):
        self.type = type;

    def toDict(self):
        return {}

class MikrotikBeacon(BaseBeacon):
    """dataclass to store mikrotik beacon data"""

    @dataclass
    class Acceleration:
        x: float = 0
        y: float = 0
        z: float = 0

        def magnitude(self):
            xx = self.x * self.x
            yy = self.y * self.y
            zz = self.z * self.z

            ms = math.sqrt(xx + yy + zz)
            return ms


    version: int = -1
    udata: int = 0
    salt: int = 0
    acceleration = Acceleration()
    temperature: float = -1
    uptime: int = -1
    flags: int = -1
    battery: int = -1

    def __init__(self):
        super().__init__(BeaconType.MIKROTIK.value)

    def decode(self, value: tuple):
        self.version = value[0]
        self.udata   = value[1]
        self.salt    = value[2]

        self.acceleration.x = value[3] / 256.0
        self.acceleration.y = value[4] / 256.0
        self.acceleration.z = value[5] / 256.0

        self.temperature = value[6] / 256.0
        self.uptime = value[7]
        self.flags = value[8]
        self.battery = value[9]

    def hasTemperature(self):
        return self.temperature != -128.0

    def toDict(self):
        return {
            "version": self.version,
            "acceleration": {
                "x": self.acceleration.x,
                "y": self.acceleration.y,
                "z": self.acceleration.z
            },
            "temperature": self.temperature,
            "uptime": self.uptime,
            "flags": self.flags,
            "battery": self.battery
        }

@dataclass
class BT5Device:
    address: str = None
    beacons = {}

    def __init__(self, addr):
        self.address = addr

    def toDict(self):
        d = {
            "address": self.address,
            "beacons": {}
        }
        for k,v in self.beacons.items():
            d["beacons"][k] = []
            for b in v:
                d["beacons"][k].append(b.toDict())
        return d

class MikrotikBT5:
    """Mikrotik BT5 Scanner class - scan advertisements and process data, if available"""

    MIKROTIK_ID = 0x094F

    history_size = 10

    scanner: BleakScanner = None
    devices = {} # identified by mac address

    def _register_beacon(self, device, beacon) -> BT5Device:
        addr = device.address
        type = beacon.type

        if not addr in self.devices:
           self.devices[addr] = BT5Device(addr)

        dev = self.devices[addr]

        if not type in dev.beacons:
            dev.beacons[type] = []

        dev.beacons[type].append(beacon)
        count = len(dev.beacons[type])

        return dev


    def _process_advertisement(self, device, ad_data):
        """Processes Mikrotik advertisement data"""

        if self.MIKROTIK_ID in ad_data.manufacturer_data:
            raw_bytes = ad_data.manufacturer_data[self.MIKROTIK_ID]

            version = int(raw_bytes[0])
            beacon = None
            value_fmt = None

            if version == 0:
                value_fmt = "<BBHhhhbIBB"
            elif version == 1:
                value_fmt = "<BBHhhhhIBB"

            if value_fmt:
                value = struct.unpack(value_fmt, raw_bytes)
                beacon = MikrotikBeacon()
                beacon.decode(value)
                beacon.rssi = device.rssi
                dev = self._register_beacon(device, beacon)
                self.on_scan(beacon, dev)

    def __init__(self, on_scan):
        self.on_scan = on_scan

    async def start_scan(self):
        if self.scanner:
            self.stop_scan()

        self.scanner = BleakScanner(
            detection_callback=self._process_advertisement,
            # scanning_mode="passive"
        )

        await self.scanner.start()


    async def stop_scan(self):
        await self.scanner.stop()
        self.scanner = None

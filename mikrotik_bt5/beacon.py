import struct
import math

from enum import IntEnum

class BeaconType(IntEnum):
    MIKROTIK = 1

class BaseBeacon:
    rssi: int = -1

    def __init__(self, type):
        self.type = type

    def toDict(self):
        return {}

class MikrotikBeacon(BaseBeacon):
    """Mikrotik beacon data"""

    MIKROTIK_ID = 0x094F

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

    name: str = "MikroTik BT5"
    address: str | None = None
    version: int | None = None
    udata: int | None = None
    salt: int | None = None
    acceleration: Acceleration | None = None
    temperature: float | None = None
    uptime: int | None = None
    flags: int | None = None
    battery: int | None = None
    rssi: int | None = None

    def __init__(self, device = None, ad_data = None):
        super().__init__(BeaconType.MIKROTIK.value)

        if device and ad_data and MikrotikBeacon.MIKROTIK_ID in ad_data.manufacturer_data:
            if device.name:
                self.name = device.name

            self.address = device.address
            self.rssi = getattr(ad_data, 'rssi', None)

            raw_bytes = ad_data.manufacturer_data[MikrotikBeacon.MIKROTIK_ID]

            version = int(raw_bytes[0])
            value_fmt = None

            if version == 0:
                value_fmt = "<BBHhhhbIBB"
            elif version == 1:
                value_fmt = "<BBHhhhhIBB"
            else:
                self.version = version
                return
                # invalid/unknown version

            if value_fmt:
                value = struct.unpack(value_fmt, raw_bytes)
                self.decode(value)

    def decode_v0(self, value: tuple):
        self.udata   = value[1]
        self.salt    = value[2]

        self.acceleration = MikrotikBeacon.Acceleration()
        self.acceleration.x = value[3] / 256.0
        self.acceleration.y = value[4] / 256.0
        self.acceleration.z = value[5] / 256.0

        self.temperature = value[6]

        self.uptime = value[7]
        self.flags = value[8]
        self.battery = value[9]

    def decode_v1(self, value: tuple):
        self.udata   = value[1]
        self.salt    = value[2]

        self.acceleration = MikrotikBeacon.Acceleration()
        self.acceleration.x = value[3] / 256.0
        self.acceleration.y = value[4] / 256.0
        self.acceleration.z = value[5] / 256.0

        if value[6] != -32768:
            self.temperature = value[6] / 256.0

        self.uptime = value[7]
        self.flags = value[8]
        self.battery = value[9]

    def decode(self, value: tuple):
        self.version = value[0]

        if self.version == 0:
            self.decode_v0(value)
        elif self.version == 1:
            self.decode_v1(value)

    def hasTemperature(self):
        return self.temperature and self.temperature != -128.0

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

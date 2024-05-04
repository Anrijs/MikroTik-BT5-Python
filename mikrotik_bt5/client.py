from bleak import BleakScanner
from .beacon import MikrotikBeacon

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
        if MikrotikBeacon.MIKROTIK_ID in ad_data.manufacturer_data:
            beacon = MikrotikBeacon(device, ad_data)
            if beacon.version != -1:
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

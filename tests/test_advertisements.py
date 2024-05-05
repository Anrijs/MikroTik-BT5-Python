import datetime
import io
import unittest
from unittest import mock

from bleak.backends.scanner import AdvertisementData
from bleak import BleakClient

from mikrotik_bt5 import MikrotikBeacon

def fake_ad_data(manufacturer_data, address="00:11:22:33:44:55"):
    """Return a BluetoothServiceInfoBleak for use in testing."""

    ad_data = AdvertisementData(
        local_name="Mikrotik tag",
        manufacturer_data=manufacturer_data,
        service_data={},
        service_uuids=[],
        rssi=-60,
        tx_power=-127,
        platform_data=(),
    )

    device = BleakClient(address)
    device.name = address

    return {
        "ad_data": ad_data,
        "device": device
    }

TEST_OK_DATA_V1 = {
    "data_ok": {2383: b'\x01\x00\xdbA\xE0\xff\xaa\xff\x02\x00\x80\x16\xe3\x1e\xda\x04\x00R'},
    "data_ok_no_temperature": {2383: b'\x01\x00\xdbA\xE0\x00\x00\x01\x00\x00\x00\x80\xe3\x1e\xda\x04\x00\x64'},
}

TEST_BAD_DATA = {
    "data_bad_version": {2383: b'\x99\x00\xdbA\xff\xff\xff\xff\x02\x00\x80\x16\xe3\x1e\xda\x04\x00R'},
    "data_bad_id": {8323: b'\x01\x00\xdbA\xff\xff\xff\xff\x02\x00\x80\x16\xe3\x1e\xda\x04\x00R'},
}
class DataManipulation(unittest.TestCase):
    # ---------------------------------------------
    #  Test data validation helpers
    # ---------------------------------------------

    def test_ok_v1_data(self):
        data = fake_ad_data(TEST_OK_DATA_V1["data_ok"])
        ad = MikrotikBeacon(data["device"], data["ad_data"])

        self.assertEqual(1, ad.version)
        self.assertEqual(22.5, ad.temperature)
        self.assertEqual(-0.125, ad.acceleration.x)
        self.assertEqual(-0.3359375, ad.acceleration.y)
        self.assertEqual(0.0078125, ad.acceleration.z)

        self.assertEqual(81403619, ad.uptime)
        self.assertEqual(82, ad.battery)

    def test_ok_v1_data_without_temperature(self):
        data = fake_ad_data(TEST_OK_DATA_V1["data_ok_no_temperature"])
        ad = MikrotikBeacon(data["device"], data["ad_data"])

        self.assertEqual(1, ad.version)
        self.assertEqual(None, ad.temperature)
        self.assertEqual(0.875, ad.acceleration.x)
        self.assertEqual(1.0, ad.acceleration.y)
        self.assertEqual(0.0, ad.acceleration.z)

        self.assertEqual(81403619, ad.uptime)
        self.assertEqual(100, ad.battery)

    def test_bad_version(self):
        data = fake_ad_data(TEST_BAD_DATA["data_bad_version"])
        ad = MikrotikBeacon(data["device"], data["ad_data"])
        self.assertEqual(None, ad.version)

    def test_bad_id(self):
        data = fake_ad_data(TEST_BAD_DATA["data_bad_id"])
        ad = MikrotikBeacon(data["device"], data["ad_data"])
        self.assertEqual(None, ad.version)

if __name__ == "__main__":
    unittest.main()

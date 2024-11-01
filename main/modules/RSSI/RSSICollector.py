import numpy as np
from pywifi import PyWiFi, const
from RSSI.utils import get_mac_address
from typing import Optional


class RSSICollector:
    '''
    Class to collect RSSI values from the WiFi interface.
    '''
    def __init__(self):
        self.device_id = get_mac_address()
        print(f"Device ID (MAC Address): {self.device_id}")
        self.rssi_values = []

        self.wifi = PyWiFi()
        self.iface = self.wifi.interfaces()[0]

        if self.iface.status() == const.IFACE_CONNECTED:
            print("Wi-Fi interface is connected.")
            self.connected_ssid = self._get_connected_ssid()
            if self.connected_ssid:
                print(f"Connected SSID: {self.connected_ssid}")
            else:
                print("Could not retrieve the connected SSID.")
        else:
            print("Wi-Fi interface is not connected or ready.")
            self.connected_ssid = None

    def _get_connected_ssid(self) -> Optional[str]:
        '''
        Gets the SSID of the currently connected Wi-Fi network.
        :return: SSID if connected, else None.
        '''
        try:
            self.iface.scan()
            scan_results = self.iface.scan_results()
            for network in scan_results:
                if self.iface.status() == const.IFACE_CONNECTED and network.ssid:
                    return network.ssid
        except Exception as e:
            print(f"Error retrieving connected SSID: {e}")
        return None

    def collect_rssi(self) -> Optional[int]:
        '''
        Collects the RSSI value from the WiFi interface for the connected SSID.
        :return: The RSSI value if successful, otherwise None.
        '''
        if not self.connected_ssid:
            print("Not connected to any Wi-Fi network.")
            return None

        try:
            self.iface.scan()
            scan_results = self.iface.scan_results()
            for network in scan_results:
                if network.ssid == self.connected_ssid:
                    rssi = network.signal
                    self.rssi_values.append(rssi)
                    return rssi
        except Exception as e:
            print(f"Error collecting RSSI: {e}")
        return None

    def get_rssi_values(self) -> np.ndarray:
        '''
        :return: The collected RSSI values as a NumPy array.
        '''
        return np.array(self.rssi_values)

    def clear_rssi_values(self):
        '''
        Clears the collected RSSI values.
        '''
        self.rssi_values = []

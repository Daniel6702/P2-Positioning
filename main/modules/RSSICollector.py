from pywifi import PyWiFi, const
from typing import Optional
import time
import socket
import psutil
from config import COLLECTOR_INTERVAL
from utils.event_system import event_system, Event

def find_internet_connected_interface():
    """Finds the network interface used for the internet connection."""
    try:
        # Use a temporary socket to detect the IP used for internet connection
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_socket.settimeout(2)
        test_socket.connect(("8.8.8.8", 80))
        ip = test_socket.getsockname()[0]
        test_socket.close()

        # Match the IP address to a network interface
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.address == ip:
                    return interface  # Return the interface name
    except Exception as e:
        print(f"Error detecting interface: {e}")
        return None

def get_mac_address():
    """Retrieves the MAC address of the current internet-connected interface."""
    interface_name = find_internet_connected_interface()
    if not interface_name:
        print("No active internet connection or interface could be detected.")
        return None

    # Retrieve MAC address of the detected interface
    for addr in psutil.net_if_addrs().get(interface_name, []):
        if addr.family == psutil.AF_LINK:  # Checks for MAC address type
            return addr.address

    print("MAC address not found for the internet-connected interface.")
    return None

class RSSICollector():
    '''
    Class to collect RSSI values from the WiFi interface.
    Publishes the collected RSSI values to the event system.
    TOPIC: "rssi"
    '''
    def __init__(self, output_topic: str = "rssi"):
        self.device_id = get_mac_address()
        print(f"Device ID (MAC Address): {self.device_id}")

        self.wifi = PyWiFi()
        self.iface = self.wifi.interfaces()[0]
        self.output_topic = output_topic        

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
    
    def run(self):
        '''
        The method that runs in the background thread to collect RSSI periodically.
        '''
        rssi = self.collect_rssi()
        event = Event(self.output_topic, rssi)
        event_system.publish(self.output_topic, event)

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
                    return rssi
        except Exception as e:
            print(f"Error collecting RSSI: {e}")
        return None
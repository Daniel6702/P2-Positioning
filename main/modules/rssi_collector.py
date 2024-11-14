import numpy as np
from pywifi import PyWiFi, const
from typing import Optional
import threading
import time
import queue
import socket
import psutil
from modules.module import Module
from config import COLLECTOR_INTERVAL

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

class RSSICollector(Module):
    '''
    Class to collect RSSI values from the WiFi interface.
    '''
    def __init__(self, interval: float = COLLECTOR_INTERVAL):
        self.device_id = get_mac_address()
        print(f"Device ID (MAC Address): {self.device_id}")

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

        self._stop_event = threading.Event()
        self._thread = None
        self.interval = interval

    def start(self):
        '''Starts the background collection thread.'''
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
            print("RSSI background collection started.")

    def stop(self):
        '''Stops the background collection thread.'''
        if self._thread is not None:
            self._stop_event.set()
            self._thread.join()
            print("RSSI background collection stopped.")
    
    def _run(self):
        '''
        The method that runs in the background thread to collect RSSI periodically.
        '''
        while not self._stop_event.is_set():
            rssi = self.collect_rssi()
            self.output.put(rssi)
            time.sleep(self.interval)


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
import socket
import psutil

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

# Example Usage
mac_address = get_mac_address()
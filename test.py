import subprocess
import csv
import time

result = str(subprocess.check_output(["netsh", "wlan", "show", "network", "mode=Bssid"]))

print(result)


with open('rssi_output.csv', mode='w', newline='') as file:

    writer = csv.writer(file)
    # Write header if needed
    writer.writerow(["Timestamp", "Estimated_Distance"])  # adjust headers as necessary for your data

    while True:
        result = str(subprocess.check_output(["netsh", "wlan", "show", "network", "mode=Bssid"]))
        index = result.find("%")
        quality = result[index-3:index]
        quality = float(quality)
        rssi = (quality / 2) - 100
        writer.writerow([time.time(), abs(rssi)])
        print(rssi)
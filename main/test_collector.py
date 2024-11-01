from modules.RSSI.RSSICollector import RSSICollector
from modules.RSSI.RSSIBackgroundCollector import RSSIBackgroundCollector
import time

rssi_collector = RSSICollector()

for _ in range(5): # Collect and print 5 RSSI values.
    rssi_value = rssi_collector.collect_rssi()
    print(f"RSSI: {rssi_value}")

background_collector = RSSIBackgroundCollector(rssi_collector, interval=.5)
background_collector.start()

print("running background collector for 10 seconds")
time.sleep(10) # Run the background collector for 10 seconds.

background_collector.stop()

rssi_values = rssi_collector.get_rssi_values()
print(f"Collected RSSI values: {rssi_values}")
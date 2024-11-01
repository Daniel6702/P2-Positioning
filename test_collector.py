from RSSI_Collector.RSSICollector import RSSICollector

rssi_collector = RSSICollector()

for _ in range(5): # Collect and print 5 RSSI values.
    rssi_value = rssi_collector.collect_rssi()
    print(f"RSSI: {rssi_value}")
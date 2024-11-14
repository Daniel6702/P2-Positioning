import csv
from modules.rssi_collector import RSSICollector
from modules.pipeline import Pipeline
from modules.test_filter import TESTFilter
from modules.log_distance_path_loss import LogdistancePathLossModel
import time

pipeline = Pipeline()

rssi_collector = RSSICollector(interval=0)
rssi_collector.start()

test_filter = TESTFilter()
distance_estimator = LogdistancePathLossModel(initial_distance=1, P_tx=20)

pipeline.add_module(rssi_collector)
pipeline.add_module(test_filter)
pipeline.add_module(distance_estimator)

output = pipeline.get_output()

with open('rssi_output.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Estimated_Distance"]) 

    while True:
        data = output.get()
        if data is not None:
            print(data)
            writer.writerow([time.time(), data])

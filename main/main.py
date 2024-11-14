import csv
import time
from modules.rssi_collector import RSSICollector
from modules.pipeline import Pipeline
from modules.test_filter import TESTFilter
from modules.log_distance_path_loss import LogdistancePathLossModel
from modules.mean_filter import MeanFilter
from modules.median_filter import MedianFilter
from modules.KalmanFilter import KalmanFilter
# Initialize the pipeline and modules
pipeline = Pipeline()

rssi_collector = RSSICollector(interval=0.01)
mean_filter = MeanFilter(window_size=25)
kalman_filter = KalmanFilter(dt=0.01, process_var=0.001)
distance_estimator = LogdistancePathLossModel(n=2)

# Add modules to the pipeline
pipeline.add_module(rssi_collector)
pipeline.add_module(mean_filter)
pipeline.add_module(kalman_filter)
pipeline.add_module(distance_estimator)

# Set up the pipeline connections and logging queues
pipeline.setup()

rssi_collector.start()

outputs = pipeline.get_outputs()

# Open CSV to write results
with open('rssi_output.csv', mode='w', newline='') as file:
    writer = csv.writer(file)

    while True:
        data_row = [time.time()]  # First column is the timestamp
        try:
            # Collect data from each module's logging queue
            for output in outputs:
                if not output.empty():
                    data_row.append(output.get())
                else:
                    data_row.append(None)  # Append None if queue is empty
            writer.writerow(data_row)
            print(data_row)  # For debugging purposes
        except KeyboardInterrupt:
            print("Terminated by user.")
            break
        time.sleep(0.1)

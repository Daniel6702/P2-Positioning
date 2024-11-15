import time
from modules import LogdistancePathLossModel, Pipeline, RSSICollector, MeanFilter, CSVLogger

INTERVAL = 0.1  # If too low, the queue will fill up faster than the data can be processed

pipeline = Pipeline()

rssi_collector = RSSICollector(interval=INTERVAL)
mean_filter = MeanFilter(window_size=20)
distance_estimator = LogdistancePathLossModel(n=2)

pipeline.add_module(rssi_collector)
pipeline.add_module(mean_filter)
pipeline.add_module(distance_estimator)

rssi_collector.start()

outputs = pipeline.get_outputs()

logger = CSVLogger(filename='rssi_output.csv', outputs=outputs, interval=INTERVAL)
logger.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Terminating program...")
    logger.stop()
    logger.join()
    print("Program terminated.")



import time
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from modules import *
import queue

# Configuration
INTERVAL = 0.2  # If too low, the queue will fill up faster than the data can be processed
DISTANCES = [1, 2, 3, 4, 5, 10, 15, 20]  # Distances in meters
NUM_SAMPLES = 40  # Number of RSSI samples per distance
CONFIDENCE = 0.95  # Confidence level for intervals

pipeline = Pipeline()
rssi_collector = RSSICollector(interval=INTERVAL)
distance_estimator = LogdistancePathLossModel(n=2)
pipeline.add_module(rssi_collector)
pipeline.add_module(distance_estimator)
outputs = pipeline.get_outputs()

pipeline1 = Pipeline()
rssi_collector1 = RSSICollector(interval=INTERVAL)
filter = MeanFilter(window_size=30)
distance_estimator1 = LogdistancePathLossModel(n=2)
pipeline1.add_module(rssi_collector1)
pipeline1.add_module(filter)
pipeline1.add_module(distance_estimator1)
outputs1 = pipeline1.get_outputs()

pipeline2 = Pipeline()
rssi_collector2 = RSSICollector(interval=INTERVAL)
filter = SavitzkyGolayFilter(window_size=20, polyorder=0)
distance_estimator2 = LogdistancePathLossModel(n=2)
pipeline2.add_module(rssi_collector2)
pipeline2.add_module(filter)
pipeline2.add_module(distance_estimator2)
outputs2 = pipeline2.get_outputs()

pipeline3 = Pipeline()
rssi_collector3 = RSSICollector(interval=INTERVAL)
filter = KalmanFilter(dt=INTERVAL, process_var=0.005)
distance_estimator3 = LogdistancePathLossModel(n=2)
pipeline3.add_module(rssi_collector3)
pipeline3.add_module(filter)
pipeline3.add_module(distance_estimator3)
outputs3 = pipeline3.get_outputs()

logger1 = CSVLogger(filename='raw_rssi.csv', outputs=outputs, interval=INTERVAL)
logger1.start()

logger2 = CSVLogger(filename='Mean.csv', outputs=outputs1, interval=INTERVAL)
logger2.start()

logger3 = CSVLogger(filename='Savitzky.csv', outputs=outputs2, interval=INTERVAL)
logger3.start()

logger4 = CSVLogger(filename='Kalman.csv', outputs=outputs3, interval=INTERVAL)
logger4.start()


# Data storage
data = []
means = []
conf_intervals = []

class Analyzer:
    def __init__(self, pipeline):
        self.collector = pipeline[0]
        self.output = pipeline[-1]

    def run(self):
        

try:
    for distance in DISTANCES:
        for collector in [rssi_collector, rssi_collector1, rssi_collector2, rssi_collector3]:
            collector.start()

        time.sleep(5)

        for collector in [rssi_collector, rssi_collector1, rssi_collector2, rssi_collector3]:
            collector.stop()

        print("move")

        time.sleep(5)

        

        
        print(f"\n*** Capturing data at {distance} meter(s) ***")

        input(f"\nPlace the device at {distance} meter and press Enter to start collecting data...")
        temp = []
        rssi_collector.start()
        #for i in range(NUM_SAMPLES):
        #    _ = distance_estimator.output.get()
        #    print(f"{i+1}/50 \t|  Calibrating...", end='\r')
        #print("\n")
        #for i in range(NUM_SAMPLES):
        #    time.sleep(INTERVAL)
        #    out = distance_estimator.output.get()
        #    print(f"{i+1}/50 - Distance {distance}m - RSSI: {out}", end='\r')
        #    temp.append(out)
        while len(temp) <= NUM_SAMPLES:
            out = distance_estimator.output.get()
            if out is None or out == 0:
                continue
            print(f"{len(temp)}/50 \t|  Distance {distance}m  |  RSSI: {out}", end='\r')
            temp.append(out)
        print("\n")
        #filter.window = []
        rssi_collector.stop()

        # Calculate statistics
        mean = np.mean(temp)
        sem = stats.sem(temp)  # Standard error of the mean
        h = sem * stats.t.ppf((1 + CONFIDENCE) / 2., NUM_SAMPLES-1)  # Margin

        data.append(temp)
        means.append(mean)
        conf_intervals.append(h)

    # Display the means
    for i, distance in enumerate(DISTANCES):
        print(f'{distance} Meter: Mean RSSI = {means[i]:.2f}, Confidence Interval = ±{conf_intervals[i]:.2f}')

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.errorbar(DISTANCES, means, yerr=conf_intervals, fmt='o', ecolor='r', capthick=2, capsize=5, label='Mean RSSI with 95% CI')
    plt.title('Mean RSSI with 95% Confidence Intervals at Various Distances')
    plt.xlabel('Distance (meters)')
    plt.ylabel('RSSI')
    plt.grid(True)
    plt.legend()
    plt.show()

except KeyboardInterrupt:
    print("Terminating program...")
    # If you have a logger, ensure it's properly stopped
    # logger.stop()
    # logger.join()
    print("Program terminated.")

import time
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from modules import *
import queue

# Configuration
INTERVAL = 0.1  # If too low, the queue will fill up faster than the data can be processed
DISTANCES = [1, 2, 3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]  # Distances in meters
NUM_SAMPLES = 50  # Number of RSSI samples per distance
CONFIDENCE = 0.95  # Confidence level for intervals

# Initialize Pipeline
pipeline = Pipeline()

rssi_collector = RSSICollector(interval=INTERVAL)
# You can uncomment and choose a filter if needed
# filter = MeanFilter(window_size=80)
# filter = KalmanFilter(dt=INTERVAL, process_var=0.005)
# filter = SavitzkyGolayFilter(window_size=20, polyorder=0)
# filter = MedianFilter(window_size=20)
distance_estimator = LogdistancePathLossModel(n=2)

pipeline.add_module(rssi_collector)
# pipeline.add_module(filter)
pipeline.add_module(distance_estimator)

outputs = pipeline.get_outputs()

# Data storage
data = []
means = []
conf_intervals = []

try:
    for distance in DISTANCES:
        input(f"\nPlace the device at {distance} meter and press Enter to start collecting data...")
        temp = []
        rssi_collector.start()
        for _ in range(NUM_SAMPLES):
            time.sleep(INTERVAL)
            _ = outputs[-1].get()
            print(f"{i+1}/50 - Calibrating", end='\r')
            print("\n")
        for i in range(NUM_SAMPLES):
            time.sleep(INTERVAL)
            out = outputs[-1].get()
            print(f"{i+1}/50 - Distance {distance}m - RSSI: {out}", end='\r')
            print("\n")
            temp.append(out)
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

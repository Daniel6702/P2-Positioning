import time
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from modules import *
import queue

# Configuration
INTERVAL = 0.1  # If too low, the queue will fill up faster than the data can be processed
DISTANCES = [1, 2, 3, 4, 5, 10, 15, 20]  # Distances in meters
NUM_SAMPLES = 40  # Number of RSSI samples per distance
CONFIDENCE = 0.95  # Confidence level for intervals

# Initialize Pipeline
pipeline = Pipeline()

rssi_collector = RSSICollector(interval=INTERVAL)
# You can uncomment and choose a filter if needed
#filter = MeanFilter(window_size=30)
#filter = KalmanFilter(dt=INTERVAL, process_var=0.005)
#filter = SavitzkyGolayFilter(window_size=20, polyorder=0)
#filter = MedianFilter(window_size=20)
distance_estimator = LogdistancePathLossModel(initial_distance=1, P_tx = 20, d_0 = 1, n=2)

pipeline.add_module(rssi_collector)
#pipeline.add_module(filter)
pipeline.add_module(distance_estimator)

rssi_collector.start()

outputs = pipeline.get_outputs()

logger1 = CSVLogger(filename='mean_30.csv', outputs=outputs, interval=INTERVAL)
logger1.start()

#outputs = pipeline.get_outputs()

# Data storage
data = []
means = []
conf_intervals = []

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("Terminating program...")
    logger1.stop()
    logger1.join()
'''
try:
    for distance in DISTANCES:

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
        filter.window = []
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

    logger1.stop()
    logger1.join()

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.errorbar(DISTANCES, means, yerr=conf_intervals, fmt='o', ecolor='r', capthick=2, capsize=5, label='Mean Distance with 95% CI')
    plt.title('95% Confidence Intervals at Various Distances')
    plt.xlabel('Real Distance')
    plt.ylabel('Measured Distance')
    plt.grid(True)
    plt.legend()
    plt.show()

except KeyboardInterrupt:
    print("Terminating program...")
    print("Program terminated.")
'''
from utils.event_system import event_system
from modules import *
import time
from utils.pauser import pauser
from utils.logger import Logger
from dynamic_analyzer import DynamicAnalyzer

INTERVAL = 0.1

# Set up your filters and distance estimators
mean_filter = MeanFilter(window_size=20, output_topic="mean")
distance_estimator_mean = LogdistancePathLossModel(n=2, input_topic="mean", output_topic="distance_mean")

# Initialize the DynamicAnalyzer
dynamic_analyzer = DynamicAnalyzer(
    results_file="dynamic_results_mean.csv",
    input_topic="distance_mean"
)

# Initialize RSSICollector and Logger
rssi_collector = RSSICollector(output_topic="rssi")
logger = Logger(topics=["rssi", "mean", "distance_mean"], prefix="test1", log_directory="logs")

# Wait for user to start the test
input("Press Enter to start the dynamic test...")
event_system.publish("calibration_finished")  # Start the dynamic test

try:
    while True:
        if pauser.pause:
            _ = input("\nPress Enter to continue... \n")
            pauser.pause = False
            event_system.publish("resume")

        rssi_collector.run()

        if dynamic_analyzer.test_completed:
            print("\nDynamic test completed.")
            break

        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("Terminating program...")
    dynamic_analyzer.write_results()

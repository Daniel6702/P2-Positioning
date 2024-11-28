from utils.event_system import event_system
from modules import *
import time
from utils.pauser import pauser
from utils.logger import Logger
from dynamic_analyzer import DynamicAnalyzer

INTERVAL = 0.1

TEST = 'test14'
N = 1.8
WINDOW = 50

def setup_mean_dynamic_test():
    mean_filter = MeanFilter(window_size=WINDOW, output_topic="mean")
    distance_estimator_mean = LogdistancePathLossModel(n=N, input_topic="mean", output_topic="distance_mean", calibration_samples=50)
    dynamic_analyzer = DynamicAnalyzer(
        results_file=f"data/dynamic/{TEST}/mean/dynamic_results_mean.csv",
        input_topic="distance_mean",
        beep_enabled=True
    )
    logger = Logger(topics=["rssi", "mean", "distance_mean"], prefix=TEST, log_directory=f"data/dynamic/{TEST}/mean")
    return (mean_filter, distance_estimator_mean, dynamic_analyzer, logger)

def setup_raw_dynamic_test():
    distance_estimator_raw = LogdistancePathLossModel(n=N, input_topic="rssi", output_topic="distance_raw", calibration_samples=50)
    dynamic_analyzer = DynamicAnalyzer(
        results_file=f"data/dynamic/{TEST}/raw/dynamic_results_raw.csv",
        input_topic="distance_raw",
    )
    logger = Logger(topics=["rssi", "distance_raw"], prefix=TEST, log_directory=f"data/dynamic/{TEST}/raw")
    return (distance_estimator_raw, dynamic_analyzer, logger)

def setup_savitzky_dynamic_test():
    savitzky_filter = SavitzkyGolayFilter(window_size=WINDOW-1, polyorder=0, input_topic="rssi", output_topic="savgol")
    distance_estimator_savitzky = LogdistancePathLossModel(n=N, input_topic="savgol", output_topic="distance_savitzky", calibration_samples=50)
    dynamic_analyzer = DynamicAnalyzer(
        results_file=f"data/dynamic/{TEST}/savitzky/dynamic_results_savitzky.csv",
        input_topic="distance_savitzky",
    )
    logger = Logger(topics=["rssi", "savgol", "distance_savitzky"], prefix=TEST, log_directory=f"data/dynamic/{TEST}/savitzky")
    return (savitzky_filter, distance_estimator_savitzky, dynamic_analyzer, logger)

def setup_median_dynamic_test():
    median_filter = MedianFilter(window_size=WINDOW-1, input_topic="rssi", output_topic="median")
    distance_estimator_median = LogdistancePathLossModel(n=N, input_topic="median", output_topic="distance_median", calibration_samples=50)
    dynamic_analyzer = DynamicAnalyzer(
        results_file=f"data/dynamic/{TEST}/median/dynamic_results_median.csv",
        input_topic="distance_median",
    )
    logger = Logger(topics=["rssi", "median", "distance_median"], prefix=TEST, log_directory=f"data/dynamic/{TEST}/median")
    return (median_filter, distance_estimator_median, dynamic_analyzer, logger)

def setup_kalman_dynamic_test():
    kalman_filter = KalmanFilter(dt=INTERVAL, process_var=0.005, input_topic="rssi", output_topic="kalman")
    distance_estimator_kalman = LogdistancePathLossModel(n=N, input_topic="kalman", output_topic="distance_kalman", calibration_samples=50)
    dynamic_analyzer = DynamicAnalyzer(
        results_file=f"data/dynamic/{TEST}/kalman/dynamic_results_kalman.csv",
        input_topic="distance_kalman",
    )
    logger = Logger(topics=["rssi", "kalman", "distance_kalman"], prefix=TEST, log_directory=f"data/dynamic/{TEST}/kalman")
    return (kalman_filter, distance_estimator_kalman, dynamic_analyzer, logger)

rssi_collector = RSSICollector(output_topic="rssi")

_ = setup_mean_dynamic_test()
_ = setup_raw_dynamic_test()
_ = setup_savitzky_dynamic_test()
_ = setup_median_dynamic_test()
_ = setup_kalman_dynamic_test()

# Wait for user to start the test
input("Press Enter to start the dynamic test...")

try:
    while True:
        if pauser.pause:
            _ = input("\nPress Enter to continue... \n")
            pauser.pause = False
            event_system.publish("resume")

        rssi_collector.run()

        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("Terminating program...")

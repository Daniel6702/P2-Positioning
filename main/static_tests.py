from modules import *
from static_analyzer import StaticAnalyzer
from utils.logger import Logger

INTERVAL = 2
N = 1.8
#DISTANCES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
#DISTANCES = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23]
DISTANCES = [1, 4, 8, 12, 16, 20, 24]

#DISTANCES = [1, 2]
NUM_SAMPLES = 20
#NUM_SAMPLES = 10
WINDOW = 10
TEST = 'test15'


# ----------------- NO filter Pipeline -----------------
def setup_raw_static_test():
    distance_estimator_raw = LogdistancePathLossModel(n=N, input_topic = "rssi", output_topic="distance_raw")
    analyzer_raw = StaticAnalyzer(distances = DISTANCES, 
                        num_samples = NUM_SAMPLES,
                        results_file = f"data/{TEST}/raw/results_raw.csv", 
                        input_topic = "distance_raw")
    logger = Logger(topics=["rssi", "distance_raw"], prefix="raw", log_directory=f"data/{TEST}/raw")
    return (distance_estimator_raw, analyzer_raw, logger)


# ----------------- MEAN Pipeline -----------------
def setup_mean_static_test():
    mean_filter = MeanFilter(window_size=WINDOW, output_topic="mean")
    distance_estimator_mean = LogdistancePathLossModel(n=N, input_topic = "mean", output_topic="distance_mean")
    analyzer_mean = StaticAnalyzer(distances = DISTANCES, 
                        num_samples = NUM_SAMPLES,
                        results_file = f"data/{TEST}/mean/results_mean.csv", 
                        input_topic = "distance_mean")
    logger = Logger(topics=["rssi", "mean", "distance_mean"], prefix="mean", log_directory=f"data/{TEST}/mean")
    return (mean_filter, distance_estimator_mean, analyzer_mean, logger)


# ----------------- Savitzky Pipeline -------------
def setup_savitzky_static_test():
    savitzky_filter = SavitzkyGolayFilter(window_size=WINDOW-1, polyorder=0, input_topic="rssi", output_topic="savgol")
    distance_estimator_savitzky = LogdistancePathLossModel(n=N, input_topic = "savgol", output_topic="distance_savitzky")
    analyzer_savitzky = StaticAnalyzer(distances = DISTANCES, 
                        num_samples = NUM_SAMPLES,
                        results_file = f"data/{TEST}/savitzky/results_savitzky.csv", 
                        input_topic = "distance_savitzky")
    logger = Logger(topics=["rssi", "savgol", "distance_savitzky"], prefix="savitzky", log_directory=f"data/{TEST}/savitzky")
    return (savitzky_filter, distance_estimator_savitzky, analyzer_savitzky, logger)

# ----------------- Median Pipeline -------------
def setup_median_static_test():
    median_filter = MedianFilter(window_size=WINDOW-1, input_topic="rssi", output_topic="median")
    distance_estimator_median = LogdistancePathLossModel(n=N, input_topic = "median", output_topic="distance_median")
    analyzer_median = StaticAnalyzer(distances = DISTANCES, 
                        num_samples = NUM_SAMPLES,
                        results_file = f"data/{TEST}/median/results_median.csv", 
                        input_topic = "distance_median")
    logger = Logger(topics=["rssi", "median", "distance_median"], prefix="median", log_directory=f"data/{TEST}/median")
    return (median_filter, distance_estimator_median, analyzer_median, logger)

# ----------------- Kalman Pipeline -------------
def setup_kalman_static_test():
    kalman_filter = KalmanFilter(dt=INTERVAL, process_var=0.005, input_topic="rssi", output_topic="kalman")
    distance_estimator_kalman = LogdistancePathLossModel(n=N, input_topic = "kalman", output_topic="distance_kalman")
    analyzer_kalman = StaticAnalyzer(distances = DISTANCES, 
                        num_samples = NUM_SAMPLES,
                        results_file = f"data/{TEST}/kalman/results_kalman.csv", 
                        input_topic = "distance_kalman")
    logger = Logger(topics=["rssi", "kalman", "distance_kalman"], prefix="kalman", log_directory=f"data/{TEST}/kalman")
    return (kalman_filter, distance_estimator_kalman, analyzer_kalman, logger)

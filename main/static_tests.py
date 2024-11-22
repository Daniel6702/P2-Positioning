from modules import *
from main.static_analyzer import StaticAnalyzer

# ----------------- NO filter Pipeline -----------------
def setup_raw_static_test():
    distance_estimator_raw = LogdistancePathLossModel(n=2, input_topic = "rssi", output_topic="distance_raw")
    analyzer_raw = StaticAnalyzer(distances = [1, 4], 
                        num_samples = 40,
                        results_file = "results_raw.csv", 
                        input_topic = "distance_raw")
    return (distance_estimator_raw, analyzer_raw)


# ----------------- MEAN Pipeline -----------------
def setup_mean_static_test():
    mean_filter = MeanFilter(window_size=20, output_topic="mean")
    distance_estimator_mean = LogdistancePathLossModel(n=2, input_topic = "mean", output_topic="distance_mean")
    analyzer_mean = StaticAnalyzer(distances = [1, 4], 
                        num_samples = 40,
                        results_file = "results_mean.csv", 
                        input_topic = "distance_mean")
    return (mean_filter, distance_estimator_mean, analyzer_mean)


# ----------------- Savitzky Pipeline -------------
def setup_savitzky_static_test():
    savitzky_filter = SavitzkyGolayFilter(window_size=20, polyorder=0, input_topic="rssi", output_topic="savgol")
    distance_estimator_savitzky = LogdistancePathLossModel(n=2, input_topic = "savgol", output_topic="distance_savitzky")
    analyzer_savitzky = StaticAnalyzer(distances = [1, 4], 
                        num_samples = 40,
                        results_file = "results_savitzky.csv", 
                        input_topic = "distance_savitzky")
    return (savitzky_filter, distance_estimator_savitzky, analyzer_savitzky)

from utils.event_system import event_system
from modules import *
import time
from utils.pauser import pauser
from utils.logger import Logger

INTERVAL = 5

rssi_collector = RSSICollector(output_topic="rssi")
mean_filter = MeanFilter(window_size=30, output_topic="mean")
distance_estimator_mean = LogdistancePathLossModel(n=2, input_topic = "mean", output_topic="distance_mean")
logger = Logger(topics=["rssi", "mean", "distance_mean"], prefix="quicktest", log_directory="test_log/test1")

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


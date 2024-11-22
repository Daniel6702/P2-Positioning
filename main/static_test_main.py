from utils.event_system import event_system
from modules import *
import time
from utils.pauser import pauser
from utils.logger import Logger
from main.static_analyzer import StaticAnalyzer
from static_tests import setup_mean_static_test

INTERVAL = 0.1

rssi_collector = RSSICollector(output_topic="rssi")

_ = setup_mean_static_test()

logger = Logger(topics=["rssi", "mean", "distance_mean"], prefix="test1", log_directory="logs")

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


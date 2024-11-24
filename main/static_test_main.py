from utils.event_system import event_system
from modules import *
import time
from utils.pauser import pauser
from utils.logger import Logger
from static_analyzer import StaticAnalyzer
from static_tests import setup_mean_static_test, setup_raw_static_test, setup_savitzky_static_test, setup_median_static_test, setup_kalman_static_test

INTERVAL = 5

rssi_collector = RSSICollector(output_topic="rssi")

_ = setup_raw_static_test()
_ = setup_mean_static_test()
_ = setup_median_static_test()
_ = setup_savitzky_static_test()
_ = setup_kalman_static_test()

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


import threading
import time
from RSSI.RSSICollector import RSSICollector

class RSSIBackgroundCollector:
    '''
    Background RSSI collector using threading.
    '''
    def __init__(self, rssi_collector: RSSICollector, interval: float = 2.0):
        '''
        Initializes the background collector.
        :param rssi_collector: An instance of the RSSICollector class.
        :param interval: Time interval (in seconds) between RSSI collection.
        '''
        self.rssi_collector = rssi_collector
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread = None

    def start(self):
        '''Starts the background collection thread.'''
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run)
            self._thread.start()
            print("RSSI background collection started.")

    def stop(self):
        '''Stops the background collection thread.'''
        if self._thread is not None:
            self._stop_event.set()
            self._thread.join()
            print("RSSI background collection stopped.")

    def _run(self):
        '''The main loop that runs in the background thread.'''
        while not self._stop_event.is_set():
            rssi = self.rssi_collector.collect_rssi()
            time.sleep(self.interval)

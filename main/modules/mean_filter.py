from modules.module import Module
import threading
from statistics import mean

class MeanFilter(Module):
    '''
    Mean Filter with configurable window size
    '''
    def __init__(self, window_size=100):
        super().__init__()
        self.window_size = window_size  # Set the window size
        self.start()

    def start(self):
        self.process_thread = threading.Thread(target=self.process, daemon=True)
        self.process_thread.start()

    def stop(self):
        self.input.put(None)
        self.process_thread.join()

    def process(self):
        window = []
        while True:
            data = self.input.get()
            if data is None:
                break
            window.append(data)
            if len(window) > self.window_size:
                window.pop(0)  # Keep the window at the correct size
            if len(window) == self.window_size:
                mean_value = mean(window)
                self.output.put(mean_value)

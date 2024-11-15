from modules.module import Module
import threading
from scipy.signal import savgol_filter

class SavitzkyGolayFilter(Module):
    '''
    Savitzky-Golay Filter with configurable window size and polynomial order
    '''
    def __init__(self, window_size=99, polyorder=3):
        super().__init__()
        self.window_size = window_size  # Set the window size
        self.polyorder = polyorder      # Set the polynomial order
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
                window.pop(0)
            
            # Only apply the filter when the window is full
            if len(window) == self.window_size:
                # Apply the Savitzky-Golay filter
                smoothed_value = savgol_filter(window, window_length=self.window_size, polyorder=self.polyorder)[-1]
                self.output.put(smoothed_value)

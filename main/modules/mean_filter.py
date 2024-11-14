from modules.module import Module
import threading
from statistics import mean

class MeanFilter(Module):
    '''
    Mean Fitler
    '''
    def __init__(self,):
        super().__init__()
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
            if len(window) > 3:
                window.pop(0)
            if len(window) == 3:
                mean_value = mean(window)
                self.output.put(mean_value)

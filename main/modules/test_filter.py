from .Module import Module
import queue
import threading

class TESTFilter(Module):
    '''
    Test filter
    '''
    def __init__(self, ):
        super().__init__()
        self.start()

    def start(self):
        self.process_thread = threading.Thread(target=self.process, daemon=True)
        self.process_thread.start()

    def stop(self):
        self.input.put(None)
        self.process_thread.join()

    def process(self):
        while True:
            data = self.input.get()

            if data is None:
                break

            # Process the data here
            data = data

            self.output.put(data)

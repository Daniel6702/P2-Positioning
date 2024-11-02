from modules.module import Module
import queue
import threading

class TESTFilter(Module):
    '''
    Test filter that takes an input and returns the absolute value of the input.
    '''
    def __init__(self, ):
        super().__init__()
        self.start()

    def start(self):
        self.process_thread = threading.Thread(target=self.process)
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
            abs_data = abs(data)

            self.output.put(abs_data)

import queue

class Module:
    def __init__(self):
        self.input = queue.Queue()
        self.output = queue.Queue()
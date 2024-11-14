from modules.module import Module
import queue

import queue

class TeeQueue:
    def __init__(self, *queues):
        self.queues = queues

    def put(self, item, block=True, timeout=None):
        for q in self.queues:
            q.put(item, block, timeout)

    def get(self, block=True, timeout=None):
        # Not used in this context, but implemented for completeness
        raise NotImplementedError("TeeQueue does not support get()")

class Pipeline:
    '''
    Pipeline class that contains a list of modules and connects them together in series.
    '''
    def __init__(self):
        self.modules = []
        self.logging_queues = []

    def add_module(self, module: Module):
        '''
        Add a module to the pipeline.
        '''
        self.modules.append(module)

    def get_outputs(self):
        '''
        Get the list of logging queues.
        '''
        return self.logging_queues

    def setup(self):
        '''
        Set up the pipeline connections and logging queues.
        '''
        num_modules = len(self.modules)
        for i in range(num_modules):
            module = self.modules[i]
            logging_queue = queue.Queue()
            self.logging_queues.append(logging_queue)
            if i < num_modules - 1:
                next_module = self.modules[i + 1]
                # Replace module's output with a TeeQueue
                module.output = TeeQueue(next_module.input, logging_queue)
            else:
                # Last module
                # Replace module's output with a TeeQueue that includes the original output
                original_output = module.output
                module.output = TeeQueue(original_output, logging_queue)

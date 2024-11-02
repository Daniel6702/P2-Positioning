from modules.module import Module
import queue

class Pipeline:
    '''
    Pipeline class that contains a list of modules and connects them together in series.
    '''
    def __init__(self):
        self.modules = []

    def add_module(self, module: Module):
        '''
        Add a module to the pipeline.
        '''
        if self.modules:
            previous_module = self.modules[-1]
            previous_module.output = module.input
        self.modules.append(module)

    def get_output(self) -> queue.Queue:
        '''
        Get the output queue of the last module in the pipeline.
        '''
        if not self.modules:
            raise ValueError("Pipeline has no modules.")
        
        return self.modules[-1].output

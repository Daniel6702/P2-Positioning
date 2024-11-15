from .Module import Module
import queue

class CapturingQueue:
    def __init__(self, target_queue):
        """
        Initialize the CapturingQueue with a target queue where items will be forwarded.
        
        :param target_queue: The queue to which items are forwarded (e.g., the next module's input queue).
        """
        self.target_queue = target_queue
        self.capture_queue = queue.Queue()

    def put(self, item, *args, **kwargs):
        """
        Put an item into both the target queue and the capture queue.
        
        :param item: The item to be put into the queues.
        """
        self.capture_queue.put(item)
        self.target_queue.put(item, *args, **kwargs)

    def get_capture_queue(self):
        """
        Retrieve the capture queue for reading captured items.
        
        :return: The capture queue.
        """
        return self.capture_queue

    def __getattr__(self, attr):
        """
        Delegate attribute access to the target queue.
        This allows the CapturingQueue to behave like a regular queue for other operations.
        
        :param attr: The attribute name.
        :return: The attribute from the target queue.
        """
        return getattr(self.target_queue, attr)

class Pipeline:
    """
    Pipeline class that contains a list of modules and connects them together in series.
    Additionally, captures the output between each module.
    """
    def __init__(self):
        self.modules = []
        self.capturing_queues = []  # List to store capture queues

    def add_module(self, module: Module):
        """
        Add a module to the pipeline and set up capturing of its output.
        
        :param module: The module to add to the pipeline.
        """
        if self.modules:
            previous_module = self.modules[-1]
            # Replace the previous module's output with a CapturingQueue
            capturing_queue = CapturingQueue(target_queue=module.input)
            previous_module.output = capturing_queue
            # Store the capture queue for later retrieval
            self.capturing_queues.append(capturing_queue.get_capture_queue())
        self.modules.append(module)

    def get_outputs(self) -> list:
        """
        Get the list of capture queues between modules.
        
        :return: A list of queues capturing the outputs between modules.
        """
        if not self.modules:
            raise ValueError("Pipeline has no modules.")
        
        return self.capturing_queues + [self.modules[-1].output]
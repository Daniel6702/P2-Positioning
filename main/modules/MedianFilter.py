from statistics import median
from utils.event_system import event_system, Event

class MedianFilter:
    '''
    Median Filter with configurable window size using an event-driven system.
    '''
    def __init__(self, window_size=99, input_topic="input", output_topic="median"):
        '''
        Initializes the MedianFilter.

        Parameters:
        - window_size: The size of the moving window for calculating the median.
        - input_topic: Event topic to subscribe to for input data.
        - output_topic: Event topic to publish the calculated median values.
        '''
        self.window_size = window_size
        self.output_topic = output_topic
        self.window = []
        
        # Subscribe to the input topic
        event_system.subscribe(input_topic, self.handle_event)
        event_system.subscribe("clear", self.clear)

    def clear(self):
        '''
        Clears the window.
        '''
        self.window.clear()
    
    def handle_event(self, event: Event):
        '''
        Handles incoming data events for the median filter.

        Parameters:
        - event: The new data point to process.
        '''
        self.window.append(event.data)
        
        # Maintain the window size
        if len(self.window) > self.window_size:
            self.window.pop(0)
        
        # Calculate and publish the median when the window is full
        median_value = median(self.window)
        
        # Create and publish the output event
        output_event = Event(self.output_topic, median_value)
        event_system.publish(self.output_topic, output_event)

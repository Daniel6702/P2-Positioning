from statistics import mean
from utils.event_system import event_system, Event

class MeanFilter():
    '''
    Mean Filter with configurable window size using an event-driven system.
    '''
    def __init__(self, window_size=100, input_topic = "rssi", output_topic = "mean"):
        '''
        Initializes the MeanFilter.

        Parameters:
        - window_size: The size of the moving window for calculating the mean.
        - output_topic: Event topic to publish the calculated mean values.
        '''
        super().__init__()
        self.window_size = window_size  # Set the window size
        self.output_topic = output_topic
        self.window = []  # Store the data in the moving window
        event_system.subscribe(input_topic, self.input)
        event_system.subscribe("clear", self.clear)

    def clear(self):
        '''
        Clears the window.
        '''
        self.window.clear()

    def input(self, event: Event):
        '''
        Handles incoming data for the mean filter.

        Parameters:
        - data: The new data point to process.
        '''
        self.window.append(event.data)

        # Keep the window at the correct size
        if len(self.window) > self.window_size:
            self.window.pop(0)

        # If the window is filled, calculate and publish the mean
        if len(self.window) == self.window_size:
            mean_value = mean(self.window)

            # Publish the mean value
            output_event = Event(self.output_topic, mean_value)
            event_system.publish(self.output_topic, output_event)
        else:
            # Publish the raw data if the window is not filled
            output_event = Event(self.output_topic, event.data)
            event_system.publish(self.output_topic, output_event)
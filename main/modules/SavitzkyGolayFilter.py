from scipy.signal import savgol_filter
from utils.event_system import event_system, Event

class SavitzkyGolayFilter:
    '''
    Savitzky-Golay Filter with configurable window size and polynomial order using an event-driven system.
    '''
    def __init__(self, window_size=99, polyorder=3, input_topic="input", output_topic="savgol"):
        '''
        Initializes the SavitzkyGolayFilter.

        Parameters:
        - window_size: The size of the moving window for applying the filter. Must be a positive odd integer.
        - polyorder: The order of the polynomial used to fit the samples. polyorder must be less than window_size.
        - input_topic: Event topic to subscribe to for input data.
        - output_topic: Event topic to publish the filtered values.
        '''
        if window_size % 2 == 0:
            raise ValueError("window_size must be a positive odd integer.")
        if polyorder >= window_size:
            raise ValueError("polyorder must be less than window_size.")
        
        self.window_size = window_size
        self.polyorder = polyorder
        self.input_topic = input_topic
        self.output_topic = output_topic
        self.window = []
        
        # Subscribe to the input topic
        event_system.subscribe(self.input_topic, self.handle_event)
        event_system.subscribe("clear", self.clear)

    def clear(self):
        '''
        Clears the window.
        '''
        self.window.clear()

    def handle_event(self, event: Event):
        '''
        Handles incoming data events for the Savitzky-Golay filter.

        Parameters:
        - event: The new data point to process.
        '''
        self.window.append(event.data)
        
        # Maintain the window size
        if len(self.window) > self.window_size:
            self.window.pop(0)
        
        # Only apply the filter when the window is full
        smoothed_values = savgol_filter(self.window, window_length=len(self.window), polyorder=self.polyorder)
        smoothed_value = smoothed_values[-1]  # Take the latest smoothed value
        
        # Create and publish the output event
        output_event = Event(self.output_topic, smoothed_value)
        event_system.publish(self.output_topic, output_event)


from dataclasses import dataclass

@dataclass
class Event:
    '''
    Data class for an event.
    '''
    event_type: str
    data: any = None

class EventSystem:
    '''
    Singleton EventSystem class.
    Maintains a subscription model where various functions (subscribers) can subscribe to specific event types.
    When an event of a subscribed type occurs, the EventSystem runs all subscribed functions with the published data.
    '''
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventSystem, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.subscribers = dict()
        self.__initialized = True

    def subscribe(self, event_type, fn):
        '''Allows a function 'fn' to subscribe to a specific event type 'event_type'.'''
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(fn)

    def publish(self, event_type, data = None):
        '''Publishes event data to all functions subscribed to the 'event_type'.'''
        if event_type in self.subscribers:
            for fn in self.subscribers[event_type]:
                if data is None:
                    fn()
                else:
                    fn(data)

    def unsubscribe(self, event_type, fn):
        '''Removes a function 'fn' from the subscribers of a specific event type 'event_type'.'''
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(fn)
                # Clean up if no subscribers left for the event_type
                if not self.subscribers[event_type]:
                    del self.subscribers[event_type]
            except ValueError:
                # The function was not found in the subscribers list
                pass

event_system = EventSystem()
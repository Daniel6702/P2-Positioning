from utils.event_system import Event, event_system
from datetime import datetime
import csv
import os
import threading

class Logger:
    '''
    Logger class that subscribes to specified event topics and logs them to separate CSV files.
    Each file is named with a common prefix followed by the topic name.
    '''

    def __init__(self, topics: list, prefix: str, log_directory: str = "logs"):
        '''
        Initializes the Logger.

        :param topics: List of event types to subscribe to.
        :param prefix: Common prefix for all log files.
        :param log_directory: Directory where log files will be stored.
        '''
        self.topics = topics
        self.prefix = prefix
        self.log_directory = log_directory
        self.file_paths = {}  # Mapping from topic to its CSV file path
        self.lock = threading.Lock()  # Ensures thread-safe file writes

        # Ensure the log directory exists
        os.makedirs(self.log_directory, exist_ok=True)

        # Initialize CSV files for each topic
        for topic in self.topics:
            file_name = f"{self.prefix}_{topic}.csv"
            file_path = os.path.join(self.log_directory, file_name)
            self.file_paths[topic] = file_path
            self._initialize_csv(file_path)
            event_system.subscribe(topic, self.handle_event)

    def _initialize_csv(self, file_path: str):
        '''
        Initializes the CSV file with headers if it doesn't already exist.

        :param file_path: Path to the CSV file.
        '''
        if not os.path.isfile(file_path):
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Timestamp', 'Data'])  # Headers

    def handle_event(self, event: Event):
        '''
        Handles incoming events and logs them to the appropriate CSV file.

        :param event: The event object containing event_type and data.
        '''
        event_type = event.event_type
        data = event.data
        timestamp = datetime.now().isoformat()

        if event_type not in self.file_paths:
            # If the event type is not being logged, ignore it
            return

        log_entry = [timestamp, str(data)]
        file_path = self.file_paths[event_type]

        # Write the log entry to the CSV file in a thread-safe manner
        with self.lock:
            try:
                with open(file_path, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(log_entry)
            except Exception as e:
                print(f"Error logging event '{event_type}': {e}")

    def unsubscribe_all(self):
        '''
        Unsubscribes the logger from all subscribed topics.
        '''
        for topic in self.topics:
            event_system.unsubscribe(topic, self.handle_event)

    def __del__(self):
        '''
        Ensures that the logger unsubscribes from all topics upon deletion.
        '''
        self.unsubscribe_all()

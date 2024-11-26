from utils.event_system import event_system, Event
import time
import platform

class DynamicAnalyzer:
    def __init__(self, results_file="dynamic_results.csv", input_topic="distance", beep_enabled=False):
        """
        Initializes the DynamicAnalyzer.

        Args:
            results_file (str): Path to the CSV file where results will be saved.
            input_topic (str): The topic name to subscribe for distance events.
            beep_enabled (bool): Flag to enable or disable beep sounds.
        """
        self.results_file = results_file
        self.input_topic = input_topic
        self.CALLIBRATED = False
        self.beep_enabled = beep_enabled  # Parameter to control beep sounds

        self.start_time = None  # Will be set when calibration finishes
        self.data = []  # List to store collected data
        self.test_completed = False

        # Initialize variables for beeping logic
        self.previous_action = None
        self.last_beeped_meter = None

        # Define the route as a list of segments with updated speed and timings
        self.route = [
            {'start_time': 0, 'end_time': 5, 'action': 'stand', 'position': 1.0},
            {'start_time': 5, 'end_time': 51, 'action': 'walk', 'start_position': 1.0, 'end_position': 24.0, 'speed': 0.5},
            {'start_time': 51, 'end_time': 56, 'action': 'stand', 'position': 24.0},
            {'start_time': 56, 'end_time': 102, 'action': 'walk', 'start_position': 24.0, 'end_position': 1.0, 'speed': 0.5},
            {'start_time': 102, 'end_time': 107, 'action': 'stand', 'position': 1.0}
        ]
        self.total_duration = 107  # Updated total duration of the route in seconds

        # Subscribe to relevant topics
        event_system.subscribe(self.input_topic, self.input)
        event_system.subscribe("calibration_finished", self.calibration_finished)

    def calibration_finished(self):
        """Handles the calibration finished event."""
        self.CALLIBRATED = True
        self.start_time = time.time()
        print("Calibration finished. Starting dynamic data collection.")

    def play_beep(self):
        """Plays a single beep sound if beeping is enabled."""
        if not self.beep_enabled:
            return  # Do nothing if beeping is disabled

        if platform.system() == "Windows":
            import winsound
            frequency = 1000  # Hz
            duration = 200    # milliseconds
            winsound.Beep(frequency, duration)
        elif platform.system() == "Darwin":
            import os
            os.system('printf "\\a"')  # More reliable beep on macOS
        else:
            # For Linux or other systems, attempt to use the bell character
            print('\a', end='', flush=True)

    def play_double_beep(self):
        """Plays a double beep sound if beeping is enabled."""
        if not self.beep_enabled:
            return  # Do nothing if beeping is disabled

        self.play_beep()
        time.sleep(0.1)  # Short pause between beeps
        self.play_beep()

    def get_actual_distance(self, elapsed_time):
        """
        Calculates the actual distance based on the elapsed time and predefined route.

        Args:
            elapsed_time (float): Time elapsed since the start of data collection.

        Returns:
            tuple: (actual_distance (float or None), current_segment (dict or None))
        """
        for segment in self.route:
            if segment['start_time'] <= elapsed_time < segment['end_time']:
                if segment['action'] == 'stand':
                    return segment['position'], segment
                elif segment['action'] == 'walk':
                    time_in_segment = elapsed_time - segment['start_time']
                    direction = 1 if segment['end_position'] > segment['start_position'] else -1
                    distance = segment['start_position'] + direction * segment['speed'] * time_in_segment
                    return distance, segment
        # If elapsed_time exceeds total duration, return None to indicate end of test
        if elapsed_time >= self.total_duration:
            return None, None
        return None, None  # If elapsed_time is before the route starts

    def input(self, event: Event):
        """
        Handles incoming distance events.

        Args:
            event (Event): The event containing estimated distance data.
        """
        if not self.CALLIBRATED:
            return

        current_time = time.time()
        elapsed_time = current_time - self.start_time

        actual_distance, segment = self.get_actual_distance(elapsed_time)

        if actual_distance is None:
            # Test is over
            if not self.test_completed:
                self.test_completed = True
                self.write_results()
                print("\nDynamic test completed.")
            return

        current_action = segment['action']

        # Check for action change to play double beep
        if self.previous_action != current_action:
            self.play_double_beep()
            self.previous_action = current_action

        # Play beep at each meter during walking
        if current_action == 'walk':
            # Determine the integer meter based on direction
            if segment['end_position'] > segment['start_position']:
                current_meter = int(actual_distance)
            else:
                # When walking backwards, adjust meter calculation
                current_meter = int(round(actual_distance))
            if self.last_beeped_meter is None or current_meter != self.last_beeped_meter:
                self.play_beep()
                self.last_beeped_meter = current_meter
        else:
            # Reset last_beeped_meter when not walking
            self.last_beeped_meter = None

        estimated_distance = event.data  # Estimated distance from the implementation

        # Store the data
        self.data.append({
            'time': elapsed_time,
            'actual_distance': actual_distance,
            'estimated_distance': estimated_distance
        })

        print(f"Time: {elapsed_time:.2f}s, Actual: {actual_distance:.2f}m, Estimated: {estimated_distance:.2f}m", end='\r')

    def write_results(self):
        """Writes the collected data and error metrics to a CSV file."""
        import csv
        with open(self.results_file, 'w', newline='') as csvfile:
            fieldnames = ['time', 'actual_distance', 'estimated_distance', 'error']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for entry in self.data:
                error = entry['estimated_distance'] - entry['actual_distance']
                writer.writerow({
                    'time': entry['time'],
                    'actual_distance': entry['actual_distance'],
                    'estimated_distance': entry['estimated_distance'],
                    'error': error
                })

        # Compute error metrics
        if self.data:
            import numpy as np
            errors = [entry['estimated_distance'] - entry['actual_distance'] for entry in self.data]
            mean_error = np.mean(errors)
            mean_abs_error = np.mean(np.abs(errors))
            rmse = np.sqrt(np.mean(np.square(errors)))

            print(f"\nDynamic test completed. Results written to {self.results_file}.")
            print(f"Mean Error: {mean_error:.2f} m")
            print(f"Mean Absolute Error: {mean_abs_error:.2f} m")
            print(f"RMSE: {rmse:.2f} m")
        else:
            print("\nNo data collected to write.")

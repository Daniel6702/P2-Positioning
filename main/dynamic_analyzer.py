from utils.event_system import event_system, Event
import time

class DynamicAnalyzer:
    def __init__(self, results_file="dynamic_results.csv", input_topic="distance"):
        self.results_file = results_file
        self.input_topic = input_topic
        self.CALLIBRATED = False

        self.start_time = None  # Will be set when calibration finishes
        self.data = []  # List to store collected data
        self.test_completed = False

        # Define the route as a list of segments
        # Each segment is a dictionary with 'start_time', 'end_time', 'action', and position information
        self.route = [
            {'start_time': 0, 'end_time': 5, 'action': 'stand', 'position': 1.0},
            {'start_time': 5, 'end_time': 14, 'action': 'walk', 'start_position': 1.0, 'end_position': 10.0, 'speed': 1.0},
            {'start_time': 14, 'end_time': 19, 'action': 'stand', 'position': 10.0},
            {'start_time': 19, 'end_time': 28, 'action': 'walk', 'start_position': 10.0, 'end_position': 1.0, 'speed': 1.0},
            {'start_time': 28, 'end_time': 33, 'action': 'stand', 'position': 1.0}
        ]
        self.total_duration = 33  # Total duration of the route in seconds

        event_system.subscribe(self.input_topic, self.input)
        event_system.subscribe("calibration_finished", self.calibration_finished)

    def calibration_finished(self):
        self.CALLIBRATED = True
        self.start_time = time.time()
        print("Calibration finished. Starting dynamic data collection.")

    def get_actual_distance(self, elapsed_time):
        for segment in self.route:
            if segment['start_time'] <= elapsed_time < segment['end_time']:
                if segment['action'] == 'stand':
                    return segment['position']
                elif segment['action'] == 'walk':
                    time_in_segment = elapsed_time - segment['start_time']
                    direction = 1 if segment['end_position'] > segment['start_position'] else -1
                    distance = segment['start_position'] + direction * segment['speed'] * time_in_segment
                    return distance
        # If elapsed_time exceeds total duration, return None to indicate end of test
        if elapsed_time >= self.total_duration:
            return None
        return None  # If elapsed_time is before the route starts

    def input(self, event: Event):
        if not self.CALLIBRATED:
            return

        current_time = time.time()
        elapsed_time = current_time - self.start_time

        actual_distance = self.get_actual_distance(elapsed_time)

        if actual_distance is None:
            # Test is over
            if not self.test_completed:
                self.test_completed = True
                self.write_results()
                print("\nDynamic test completed.")
            return

        estimated_distance = event.data  # Estimated distance from the implementation

        # Store the data
        self.data.append({
            'time': elapsed_time,
            'actual_distance': actual_distance,
            'estimated_distance': estimated_distance
        })

        print(f"Time: {elapsed_time:.2f}s, Actual: {actual_distance:.2f}m, Estimated: {estimated_distance:.2f}m", end='\r')

    def write_results(self):
        # Write the collected data to a CSV file
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
        errors = [entry['estimated_distance'] - entry['actual_distance'] for entry in self.data]
        import numpy as np
        mean_error = np.mean(errors)
        mean_abs_error = np.mean(np.abs(errors))
        rmse = np.sqrt(np.mean(np.square(errors)))

        print(f"\nDynamic test completed. Results written to {self.results_file}.")
        print(f"Mean Error: {mean_error:.2f} m")
        print(f"Mean Absolute Error: {mean_abs_error:.2f} m")
        print(f"RMSE: {rmse:.2f} m")

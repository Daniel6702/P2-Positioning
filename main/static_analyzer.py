from utils.event_system import event_system, Event
import platform

class StaticAnalyzer:
    def __init__(self, distances=[1, 4, 8, 12, 16, 20], num_samples=40, results_file="results.csv", input_topic="distance"):
        self.DISTANCES = distances
        self.NUM_SAMPLES = num_samples
        self.CONFIDENCE_LEVELS = [0.90, 0.95]  # Added 90% and 95% confidence levels
        self.CALLIBRATED = False
        self.input_topic = input_topic
        self.results_file = results_file

        event_system.subscribe(self.input_topic, self.input)
        event_system.subscribe("calibration_finished", self.calibration_finished)

        self.results = []  # Stores results as dicts with all calculated parameters
        self.temp_samples = []
        self.current_distance_index = 0
        self.collecting = False

    def calibration_finished(self):
        self.CALLIBRATED = True
        # Start collecting data for the first distance
        self.collecting = True
        print(f"Starting data collection for distance {self.DISTANCES[self.current_distance_index]} meters.")

    def input(self, event: Event):
        if not self.CALLIBRATED or not self.collecting:
            return

        distance_estimate = event.data
        self.temp_samples.append(distance_estimate)

        print(f"Collected sample {len(self.temp_samples)}/{self.NUM_SAMPLES}        Estimated distance: {distance_estimate} meters", end="\r")

        if len(self.temp_samples) >= self.NUM_SAMPLES:
            event_system.publish("clear")
            # Calculate statistics
            import math
            import scipy.stats as st

            n = len(self.temp_samples)
            true_distance = self.DISTANCES[self.current_distance_index]
            mean_value = sum(self.temp_samples) / n
            # Compute standard deviation
            variance = sum((x - mean_value) ** 2 for x in self.temp_samples) / (n - 1)
            std_dev = math.sqrt(variance)
            # Initialize dictionary to store confidence intervals
            confidence_intervals = {}
            for confidence in self.CONFIDENCE_LEVELS:
                # Compute confidence interval
                t_critical = st.t.ppf((1 + confidence) / 2, df=n - 1)
                margin_of_error = t_critical * (std_dev / math.sqrt(n))
                confidence_intervals[f'CI_{int(confidence*100)}%'] = margin_of_error

            # Compute Bias
            bias = mean_value - true_distance
            # Compute Standard Error
            standard_error = std_dev / math.sqrt(n)
            # Compute Mean Absolute Error
            mae = sum(abs(x - true_distance) for x in self.temp_samples) / n
            # Compute Root Mean Square Error
            rmse = math.sqrt(sum((x - true_distance) ** 2 for x in self.temp_samples) / n)
            # Compute Relative Error (as percentage)
            relative_error = (abs(bias) / true_distance) * 100 if true_distance != 0 else 0

            # Store the results
            result = {
                'distance': true_distance,
                'mean': mean_value,
                'std_dev': std_dev,
                'bias': bias,
                'standard_error': standard_error,
                'MAE': mae,
                'RMSE': rmse,
                'relative_error(%)': relative_error
            }
            result.update(confidence_intervals)  # Add confidence intervals to the result
            self.results.append(result)
            self.temp_samples = []
            self.collecting = False

            next_location = self.DISTANCES[self.current_distance_index + 1] if self.current_distance_index + 1 < len(self.DISTANCES) else None
            if next_location:
                print(f"\nData collection for distance {true_distance} meters complete.")
                print(f"Please move to the next location: {next_location} meters.")
                self.play_beep()
                input("Press Enter when ready to continue...")
                self.resume()
            else:
                print(f"\nData collection for distance {true_distance} meters complete. All distances processed.")
                self.write_to_csv()
                print(f"Results have been written to {self.results_file}.")

    def resume(self):
        # Move to the next distance or finish if all distances are covered
        self.current_distance_index += 1
        if self.current_distance_index < len(self.DISTANCES):
            self.collecting = True
            print(f"Resuming data collection for distance {self.DISTANCES[self.current_distance_index]} meters.")
        else:
            # All distances have been processed
            print(f"All distances processed. Results have been written to {self.results_file}.")
            self.write_to_csv()
    
    def play_beep(self):
        if platform.system() == "Windows":
            import winsound
            winsound.Beep(1000, 500)
        elif platform.system() == "Darwin":
            import os
            os.system('echo -n "\a"')

    def write_to_csv(self):
        # Write the results to a CSV file
        import csv
        # Determine fieldnames dynamically based on the first result
        fieldnames = list(self.results[0].keys())
        with open(self.results_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in self.results:
                writer.writerow(result)

from utils.event_system import event_system, Event

class StaticAnalyzer:
    def __init__(self, distances=[1, 4, 8, 12, 16, 20], num_samples=40, results_file="results.csv", input_topic="distance"):
        self.DISTANCES = distances
        self.NUM_SAMPLES = num_samples
        self.CONFIDENCE = 0.95
        self.CALLIBRATED = False
        self.input_topic = input_topic
        self.results_file = results_file

        event_system.subscribe(self.input_topic, self.input)
        event_system.subscribe("calibration_finished", self.calibration_finished)

        self.results = []  # Stores results as dicts with 'distance', 'mean', 'CI'
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
            # Calculate mean and confidence interval
            mean_value = sum(self.temp_samples) / len(self.temp_samples)
            # Compute standard deviation
            import math
            n = len(self.temp_samples)
            variance = sum((x - mean_value) ** 2 for x in self.temp_samples) / (n - 1)
            std_dev = math.sqrt(variance)
            # Compute confidence interval
            import scipy.stats as st
            t_critical = st.t.ppf((1 + self.CONFIDENCE) / 2, df=n - 1)
            margin_of_error = t_critical * (std_dev / math.sqrt(n))

            # Store the results
            self.results.append({
                'distance': self.DISTANCES[self.current_distance_index],
                'mean': mean_value,
                'CI': margin_of_error
            })
            self.temp_samples = []
            self.collecting = False

            next_location = self.DISTANCES[self.current_distance_index + 1] if self.current_distance_index + 1 < len(self.DISTANCES) else None
            if next_location:
                print(f"\nData collection for distance {self.DISTANCES[self.current_distance_index]} meters complete.")
                print(f"Please move to the next location: {next_location} meters.")
                input("Press Enter when ready to continue...")
                self.resume()
            else:
                print(f"\nData collection for distance {self.DISTANCES[self.current_distance_index]} meters complete. All distances processed.")
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

    def write_to_csv(self):
        # Write the results to a CSV file
        import csv
        with open(self.results_file, 'w', newline='') as csvfile:
            fieldnames = ['distance', 'mean', 'CI']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in self.results:
                writer.writerow(result)

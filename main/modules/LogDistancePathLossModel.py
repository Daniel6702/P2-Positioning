import math
from utils.event_system import event_system, Event

class LogdistancePathLossModel():
    '''
    Log-distance path loss model that calibrates itself using initial RSSI measurements at a known distance.
    '''
    def __init__(
        self, 
        initial_distance=1, 
        P_tx=20, 
        d_0=1, 
        calibration_samples=10, 
        n=3, 
        input_topic="rssi",
        output_topic="distance", 
        calibration_topic="calibration_finished"
    ):
        '''
        Initializes the LogdistancePathLossModel.

        Parameters:
        - initial_distance: The known distance at which initial RSSI measurements are taken.
        - P_tx: Transmitted power in dBm.
        - d_0: Reference distance (typically 1 meter).
        - calibration_samples: Number of samples to collect during calibration.
        - n: Path loss exponent.
        - output_topic: Event topic to publish the estimated distance.
        '''
        super().__init__()
        self.initial_distance = initial_distance
        self.P_tx = P_tx
        self.d_0 = d_0
        self.calibration_samples = calibration_samples
        self.calibration_rssi_values = []
        self.calibrated = False
        self.PL_0 = None
        self.n = n
        self.input_topic = input_topic
        self.output_topic = output_topic
        self.calibration_topic = calibration_topic

        event_system.subscribe(self.input_topic, self.input)

    def input(self, event: Event):
        '''
        Handles incoming RSSI data.

        Parameters:
        - data: The RSSI measurement in dBm.
        '''
        rssi = event.data

        if not self.calibrated:
            # Collect calibration samples
            self.calibration_rssi_values.append(rssi)
            print(f"Collected calibration sample {len(self.calibration_rssi_values)}/{self.calibration_samples}", end="\r")
            if len(self.calibration_rssi_values) >= self.calibration_samples:
                self.calibrate()
            return

        # Ensure calibration has been done before processing
        if self.PL_0 is None or self.n is None:
            raise ValueError("Model is not calibrated.")

        # Log-distance path loss formula to estimate distance
        exponent = (self.P_tx - rssi - self.PL_0) / (10 * self.n)
        distance = self.d_0 * (10 ** exponent)
        distance = round(distance, 4)  # Optional: round for readability

        # Publish the estimated distance
        output_event = Event(self.output_topic, distance)
        event_system.publish(self.output_topic, output_event)

    def calibrate(self):
        '''
        Calibrates the model using the collected RSSI values.
        '''
        # Calculate average RSSI during calibration
        avg_rssi = sum(self.calibration_rssi_values) / len(self.calibration_rssi_values)
        print(f"Average RSSI during calibration: {avg_rssi:.2f} dBm")

        # Estimate PL_0
        self.PL_0 = self.P_tx - avg_rssi
        print(f"Estimated PL_0: {self.PL_0:.2f} dB")

        # Estimate n using the known initial distance
        if self.n is None:
            if self.initial_distance != self.d_0:
                self.n = (self.P_tx - avg_rssi - self.PL_0) / (10 * math.log10(self.initial_distance / self.d_0))
            else:
                # If initial_distance equals d_0, path loss exponent n is undefined
                # Assume n = 2 (free space) or any typical value
                self.n = 2
            print(f"Estimated path loss exponent n: {self.n:.2f}")
        else:
            print(f"Using provided path loss exponent n: {self.n:.2f}")

        self.calibrated = True
        print(f"Calibration completed: PL_0 = {self.PL_0:.2f}, n = {self.n:.2f}")
        event_system.publish(self.calibration_topic)

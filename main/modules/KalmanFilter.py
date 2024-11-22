import numpy as np
from utils.event_system import event_system, Event

class KalmanFilter:
    """
    Kalman Filter for filtering RSSI data using an event-driven system.
    """
    def __init__(self,
                 dt: float = 1.0,
                 process_var: float = 1e-4,
                 measurement_var: float = 1.0,
                 initial_state: list = [0.0],
                 initial_uncertainty: np.ndarray = np.array([[1.0]]),
                 input_topic: str = "rssi_input",
                 output_topic: str = "rssi_filtered"):
        """
        Initializes the Kalman Filter.

        Parameters:
        - dt: Time step between updates.
        - process_var: Process variance (uncertainty in the model).
        - measurement_var: Measurement variance (uncertainty in RSSI).
        - initial_state: Initial state vector [RSSI].
        - initial_uncertainty: Initial uncertainty (covariance matrix).
        - input_topic: Event topic to subscribe to for incoming RSSI data.
        - output_topic: Event topic to publish the filtered RSSI values.
        """
        # Time step
        self.dt = dt

        # State vector and covariance matrix
        self.x = np.array(initial_state, dtype=float)  # [RSSI]
        self.P = np.array(initial_uncertainty, dtype=float)  # [[P]]

        # State transition matrix
        self.A = np.array([[1.0]])  # Assuming RSSI is constant without control input

        # Control matrix (unused)
        self.B = np.array([0.0])

        # Measurement matrix
        self.H = np.array([[1.0]])

        # Process and measurement noise covariance matrices
        self.Q = np.array([[process_var]])  # Process noise
        self.R = np.array([[measurement_var]])  # Measurement noise

        self.input_topic = input_topic
        self.output_topic = output_topic

        # Subscribe to the input topic
        event_system.subscribe(self.input_topic, self.handle_event)
        event_system.subscribe("clear", self.clear)

    def clear(self):
        """
        Clears the state vector and covariance matrix.
        """
        self.x.fill(0.0)
        self.P.fill(0.0)
    
    def handle_event(self, event: Event):
        """
        Handles incoming RSSI data events and processes them through the Kalman Filter.

        Parameters:
        - event: The incoming RSSI measurement.
        """
        data = event.data

        # Check if the data is a list (multiple RSSI measurements)
        if isinstance(data, list):
            for rssi in data:
                self.process_rssi(rssi)
        else:
            # Assume it's a single RSSI measurement
            self.process_rssi(data)

    def process_rssi(self, rssi: float):
        """
        Processes a single RSSI measurement through the Kalman Filter.

        Parameters:
        - rssi: Received Signal Strength Indicator.
        """
        # Prediction step
        self.predict()

        # Update step with the new RSSI measurement
        self.update(rssi)

        # Extract the filtered RSSI
        filtered_rssi = self.x[0]

        # Publish the filtered RSSI to the output topic
        output_event = Event(self.output_topic, filtered_rssi)
        event_system.publish(self.output_topic, output_event)

    def predict(self):
        """
        Prediction step of the Kalman Filter.
        """
        # Predict the next state
        self.x = self.A @ self.x

        # Predict the next covariance
        self.P = self.A @ self.P @ self.A.T + self.Q

    def update(self, measurement: float):
        """
        Update step of the Kalman Filter using the RSSI measurement.

        Parameters:
        - measurement: Received Signal Strength Indicator.
        """
        # Measurement residual
        y = measurement - (self.H @ self.x)

        # Residual covariance
        S = self.H @ self.P @ self.H.T + self.R

        # Kalman Gain
        K = self.P @ self.H.T @ np.linalg.inv(S)

        # Update the state estimate
        self.x = self.x + (K @ y).flatten()

        # Update the covariance matrix
        I = np.eye(self.P.shape[0])
        self.P = (I - K @ self.H) @ self.P

import numpy as np
import threading
from .Module import Module

class KalmanFilter(Module):
    def __init__(self,
                 dt: float = 1.0,
                 process_var: float = 1e-4,
                 measurement_var: float = 1.0,
                 initial_state: list = [0.0],
                 initial_uncertainty: np.ndarray = np.array([[1.0]])):
        """
        Initializes the Kalman Filter for filtering RSSI data.
        
        :param dt: Time step between updates.
        :param process_var: Process variance (uncertainty in the model).
        :param measurement_var: Measurement variance (uncertainty in RSSI).
        :param initial_state: Initial state vector [RSSI].
        :param initial_uncertainty: Initial uncertainty (covariance matrix).
        """
        super().__init__()
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

        # Start the processing thread
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        """
        Continuously processes incoming RSSI measurements from the input queue,
        applies the Kalman Filter, and outputs the filtered RSSI.
        """
        while True:
            try:
                # Retrieve the next RSSI measurement from the input queue
                data = self.input.get()
                if data is None:
                    # Sentinel value to terminate the thread
                    break

                # Check if the data is a list (multiple RSSI measurements)
                if isinstance(data, list):
                    for rssi in data:
                        self.process_rssi(rssi)
                else:
                    # Assume it's a single RSSI measurement
                    self.process_rssi(data)

            except Exception as e:
                print(f"KalmanFilter encountered an error: {e}")

    def process_rssi(self, rssi: float):
        """
        Processes a single RSSI measurement through the Kalman Filter.
        
        :param rssi: Received Signal Strength Indicator.
        """
        # Prediction step
        self.predict()

        # Update step with the new RSSI measurement
        self.update(rssi)

        # Extract the filtered RSSI
        filtered_rssi = self.x[0]

        # Output the filtered RSSI to the next module
        self.output.put(filtered_rssi)

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
        
        :param measurement: Received Signal Strength Indicator.
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

kalman_filter = KalmanFilter(
    dt=0.01,
    process_var=1e-4,
    measurement_var=1.0,
    initial_state=[-40.0],
    initial_uncertainty=np.array([[1.0]])
)
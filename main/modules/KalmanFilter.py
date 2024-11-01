import numpy as np

class KalmanFilter:
    def __init__(self,
            dt: 1.0,
            process_var: 1e-4,
            measurement_var: 1.0,
            initial_state: [0, 0],
            initial_uncertainty: np.array([[1, 0], [0, 1]]),
            rssi_0: float,
            path_loss_exp: 3
    ):
        """
        Initializes the Kalman Filter
        :param dt: Time step between updates.
        :param process_var: Process variance (uncertainty in the model).
        :param measurement_var: Measurement variance (uncertainty in RSSI).
        :param initial_state: Initial state vector [position, velocity].
        :param initial_uncertainty: Initial uncertainty (covariance matrix).
        :param rssi_0: RSSI at a distance of 1 meter.
        :param path_loss_exp: Path-loss exponent (depends on environment).
        """

        # Time step
        self.dt = dt

        # Parameters
        self.x = np.array(initial_state)
        self.P = np.array(initial_uncertainty)

        # State transmission matrix
        self.A = np.array([[1, self.dt],[0, 1]])

        # Control matrix
        self.B = np.array([0, 0])

        # Measurement matrix
        self.H = np.array([[1, 0]])

        # Process and measurement noise covariance
        self.Q = np.array([[process_var, 0], [0, process_var]])
        self.R = np.array([[measurement_var]])

        # RSSI distance parameters
        self.rssi_0 = rssi_0
        self.path_loss_exp = path_loss_exp


    def filter(self, measurements : list):
        """
        Computes the Kalman Filter given input data
        :param measurements: List of RSSI measurements.
        :return:
        """

        for rssi in measurements:
            self.predict()
            self.update(rssi)
            print("Estimated state:", self.x)

    def rssi_to_distance(self, rssi : float) -> float:
        """
        Converts the rssi data into distance units, using the path-loss model
        :param rssi:
        :return:
        """
        return 10 ** ((self.rssi_0 - rssi) / (10 * self.path_loss_exp))

    def predict(self):
        """
        Prediction step of the Kalman Filter
        :return:
        """

        # Predict state
        self.x = self.A @ self.x

        # Predict uncertainty
        self.P = self.A @ self.P @ self.A.T + self.Q

    def update(self, rssi):
        """
        Update step of the Kalman filter using the RSSI data
        :param rssi:
        :return:
        """

        # Convert RSSI to distance
        distance = self.rssi_to_distance(rssi)

        # Measurement residual
        y = distance - self.H @ self.x

        # Kalman Gain
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)

        # Update the state estimate
        self.x = self.x + K @ y

        # Update the uncertainty
        I = np.eye(self.P.shape[0])
        self.P = (I - K @ self.H) @ self.P
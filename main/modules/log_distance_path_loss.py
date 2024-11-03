from modules.module import Module
import threading
import math

'''
P_tx refers to the transmit power of the access point (AP) or device, measured in dBm.
Indoor Wi-Fi APs: Usually around 20 dBm.
'''

class LogdistancePathLossModel(Module):
    '''
    Log-distance path loss model that calibrates itself using initial RSSI measurements at a known distance.
    '''
    def __init__(self, initial_distance, P_tx, d_0=1, calibration_samples=10):
        '''
        initial_distance: The known distance at which initial RSSI measurements are taken.
        P_tx: Transmitted power in dBm.
        d_0: Reference distance (typically 1 meter).
        calibration_samples: Number of samples to collect during calibration.
        '''
        super().__init__()
        self.initial_distance = initial_distance
        self.P_tx = P_tx
        self.d_0 = d_0
        self.calibration_samples = calibration_samples
        self.calibration_rssi_values = []
        self.calibrated = False
        self.PL_0 = None
        self.n = None
        self.start()

    def start(self):
        self.process_thread = threading.Thread(target=self.process, daemon=True)
        self.process_thread.start()

    def stop(self):
        self.input.put(None)
        self.process_thread.join()

    def calibrate(self):
        # Calculate average RSSI during calibration
        avg_rssi = sum(self.calibration_rssi_values) / len(self.calibration_rssi_values)
        
        # Estimate PL_0
        self.PL_0 = self.P_tx - avg_rssi
        # Estimate n using the known initial distance
        if self.initial_distance != self.d_0:
            self.n = (self.P_tx - avg_rssi - self.PL_0) / (10 * math.log10(self.initial_distance / self.d_0))
        else:
            # If initial_distance equals d_0, path loss exponent n is undefined
            # Assume n = 2 (free space) or any typical value
            self.n = 2

        self.calibrated = True
        print(f"Calibration completed: PL_0 = {self.PL_0:.2f}, n = {self.n:.2f}")

    def process(self):
        while True:
            data = self.input.get()

            if data is None:
                break

            rssi = data

            if not self.calibrated:
                # Collect calibration samples
                self.calibration_rssi_values.append(rssi)
                if len(self.calibration_rssi_values) >= self.calibration_samples:
                    self.calibrate()
                continue

            # Ensure calibration has been done before processing
            if self.PL_0 is None or self.n is None:
                raise ValueError("Model is not calibrated.")

            # Log-distance path loss formula to estimate distance
            exponent = (self.P_tx - rssi - self.PL_0) / (10 * self.n)
            distance = self.d_0 * (10 ** exponent)
            
            # Output the estimated distance
            self.output.put(distance)

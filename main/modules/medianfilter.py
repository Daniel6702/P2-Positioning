import numpy as np

def median_filter(data: list, window_size = 3)-> list:
    """
    Apply a median filter to RSSI data to reduce outliers.

    Parameters:
    - data: List or numpy array of RSSI values.
    - window_size: Size of the moving window (should be an odd number).

    Returns:
    - filtered_data: List of filtered RSSI values.
    """
    half_window = window_size // 2 # integer division 3/2 = 1
    padded_data = np.pad(data, (half_window, half_window), mode='edge')
    mean_filtered = []

    for i in range(len(data)):
        # Extract the current window
        window = padded_data[i:i + window_size] #includes start, excludes end
        # Sort the window to find the median
        window_sorted = np.sort(window)

        # Calculate the median
        if window_size % 2 == 1:  # Odd window size
            median_value = window_sorted[half_window]
        else:  # Even window size
            median_value = (window_sorted[half_window - 1] + window_sorted[half_window]) / 2
        
        mean_filtered.append(median_value)
    
    return mean_filtered
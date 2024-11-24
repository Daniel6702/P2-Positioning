import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from scipy.stats import pearsonr
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw  # Ensure fastdtw is installed: pip install fastdtw

def plot_dynamic_results(csv_file="dynamic_results.csv", time_shift=0.0):
    """
    Plots the actual distance, estimated distance (with optional time shift), and error over time.
    Computes and prints quantitative metrics including Accuracy, MAE, RMSE, STD, SNR, Pearson's r,
    and Dynamic Time Warping (DTW) distance.

    Parameters:
    - csv_file (str): Path to the CSV file containing the results.
    - time_shift (float): Time shift to apply to the estimated distances in seconds.
                          Positive values delay the estimated data,
                          negative values advance the estimated data.
    """
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Check if required columns exist
    required_columns = {'time', 'actual_distance', 'estimated_distance'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"The CSV file must contain the following columns: {required_columns}")

    # Apply time shift to the estimated distances
    shifted_time = df['time'] + time_shift

    # Create a DataFrame with shifted time and estimated distance
    shifted_df = pd.DataFrame({
        'shifted_time': shifted_time,
        'estimated_distance': df['estimated_distance']
    })

    # Sort the shifted DataFrame by shifted_time to ensure proper interpolation
    shifted_df = shifted_df.sort_values('shifted_time')

    # Remove duplicate times by averaging (if any)
    shifted_df = shifted_df.groupby('shifted_time').mean().reset_index()

    # Create interpolation function for estimated distances
    interp_func = interp1d(
        shifted_df['shifted_time'],
        shifted_df['estimated_distance'],
        kind='linear',
        bounds_error=False,
        fill_value="extrapolate"
    )

    # Define a common time range based on actual distances
    common_time = df['time']

    # Get the shifted estimated distances aligned with the actual times
    aligned_estimated_distance = interp_func(common_time)
    #aligned_estimated_distance *= .6

    # Ensure aligned_estimated_distance is a 1-D numpy array
    aligned_estimated_distance = np.array(aligned_estimated_distance).ravel()

    # Compute the error after time shifting
    error = df['actual_distance'] - aligned_estimated_distance

    # Compute traditional metrics
    mae = np.mean(np.abs(error))
    rmse = np.sqrt(np.mean(error ** 2))

    # Compute Accuracy
    mean_actual = np.mean(df['actual_distance'])
    if mean_actual != 0:
        accuracy = 100 * (1 - (rmse / mean_actual))
    else:
        accuracy = np.nan  # Undefined if mean_actual is zero

    # Compute Standard Deviation (STD) of the error
    std_error = np.std(error)

    # Compute Signal-to-Noise Ratio (SNR)
    signal_power = np.var(df['actual_distance'])
    noise_power = np.var(error)
    if noise_power != 0:
        snr = 10 * np.log10(signal_power / noise_power)
    else:
        snr = np.inf  # Infinite SNR if noise power is zero

    # Compute Pearson's correlation coefficient (r)
    corr_coef, _ = pearsonr(df['actual_distance'], aligned_estimated_distance)

    # Compute Dynamic Time Warping (DTW) distance
    # Ensure both inputs are 1-D numpy arrays
    actual_distance = np.array(df['actual_distance']).reshape(-1, 1)
    estimated_distance = aligned_estimated_distance.reshape(-1, 1)

    # Handle cases where the sequences are too short for DTW
    if len(actual_distance) < 2 or len(estimated_distance) < 2:
        dtw_distance = np.nan
        print("Warning: Sequences are too short for DTW calculation.")
    else:
        dtw_distance, _ = fastdtw(actual_distance, estimated_distance, dist=euclidean)

    # Print out the metrics
    print(f"Performance Metrics:")
    print(f"--------------------")
    print(f"Mean Absolute Error (MAE): {mae:.4f} meters")
    print(f"Root Mean Squared Error (RMSE): {rmse:.4f} meters")
    print(f"Standard Deviation of Error (STD): {std_error:.4f} meters")
    if not np.isnan(accuracy):
        print(f"Accuracy: {accuracy:.2f}%")
    else:
        print("Accuracy: Undefined (Mean actual distance is zero)")
    print(f"Signal-to-Noise Ratio (SNR): {snr:.2f} dB")
    print(f"Pearson's Correlation Coefficient (r): {corr_coef:.4f}")
    if not np.isnan(dtw_distance):
        print(f"Dynamic Time Warping (DTW) Distance: {dtw_distance:.4f}")
    else:
        print("Dynamic Time Warping (DTW) Distance: Undefined (Insufficient data)")

    print(f'{mae:.4f},{rmse:.4f},{std_error:.4f},{accuracy:.2f},{snr:.2f},{corr_coef:.4f},{dtw_distance:.4f}')

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(14, 7))

    # Plot Actual Distance over Time
    ax.plot(df['time'], df['actual_distance'], label='Actual Distance', color='blue', linewidth=2)

    # Plot Shifted Estimated Distance over Time
    ax.plot(
        common_time,
        aligned_estimated_distance,
        label='Estimated Distance',
        color='orange',
        linestyle='--',
        linewidth=2
    )

    # Plot the error as a filled area
    ax.fill_between(common_time, error, color='red', alpha=0.3, label='Error (Actual - Estimated)')

    # Configure labels and title
    ax.set_xlabel('Time (s)', fontsize=14)
    ax.set_ylabel('Distance / Error (m)', fontsize=14)
    ax.set_title('Dynamic Test (Kalman)', fontsize=16)

    # Add legend
    ax.legend(loc='upper left')

    # Add grid for better readability
    ax.grid(True)

    # Enhance layout
    plt.tight_layout()

    # Display the plot
    plt.show()

if __name__ == "__main__":
    file = r'data\dynamic\test4\savitzky\dynamic_results_savitzky.csv' 
    time_shift = -2.3
    plot_dynamic_results(file, time_shift)

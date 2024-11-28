import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
from scipy.interpolate import interp1d

def plot_dynamic_results(ax, csv_file="dynamic_results.csv", time_shift=0.0):
    """
    Plots the actual distance, estimated distance (with optional time shift), and error over time
    on the provided axis for better readability.

    Parameters:
    - ax: Matplotlib axis to plot on.
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

    # Compute the error after time shifting
    error = df['actual_distance'] - aligned_estimated_distance

    # Plot Actual Distance over Time
    ax.plot(df['time'], df['actual_distance'], label='Actual Distance', color='blue', linewidth=2)

    # Plot Shifted Estimated Distance over Time
    ax.plot(
        common_time,
        aligned_estimated_distance,
        label=f'Estimated Distance',
        color='orange',
        linestyle='--',
        linewidth=2
    )

    # Highlight Error as a filled region
    ax.fill_between(common_time, error, color='red', alpha=0.3, label='Error (Actual - Estimated)')

    # Configure labels and title
    ax.set_xlabel('Time (s)', fontsize=12)
    ax.set_ylabel('Distance / Error (m)', fontsize=12)
    ax.set_title('Dynamic Test (No filter)', fontsize=14)

    # Add legend
    ax.legend(loc='upper left')

    # Add grid for better readability
    ax.grid(True)

def plot_data_streams(ax, csv_file_paths):
    """
    Reads multiple CSV files and plots their data streams on the provided axis.

    Parameters:
    - ax: Matplotlib axis to plot on.
    - csv_file_paths (list of str): List of paths to CSV files.
    """
    if not csv_file_paths:
        print("Error: No CSV file paths provided.")
        return

    # To keep track of test names (assuming files may belong to different tests)
    test_names = set()

    for file_path in csv_file_paths:
        if not os.path.isfile(file_path):
            print(f"Error: The file '{file_path}' does not exist. Skipping.")
            continue

        try:
            # Read the CSV file
            df = pd.read_csv(file_path)

            # Check if required columns exist
            if 'Timestamp' not in df.columns or 'Data' not in df.columns:
                print(f"Warning: '{file_path}' does not contain required columns. Skipping.")
                continue

            # Parse the Timestamp column to datetime objects
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])

            # Sort the dataframe by Timestamp in case it's unordered
            df = df.sort_values('Timestamp')

            # Extract the data stream identifier from the filename
            filename = os.path.basename(file_path)
            parts = filename.split('_')
            if len(parts) != 2:
                parts = parts[:2]

            test_name = parts[0]
            stream_id = parts[1].replace('.csv', '')
            test_names.add(test_name)

            # Plot the data
            ax.plot(df['Timestamp'], df['Data'], label=f"{stream_id}")

        except Exception as e:
            print(f"Error processing file '{file_path}': {e}")
            continue

    if not ax.has_data():
        print("No valid data streams to plot.")
        return

    # Customize the plot
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Data')

    # Determine the plot title based on test names
    ax.set_title('RSSI Data')

    ax.legend()
    ax.grid(True)

# Main script to combine the plots
if __name__ == "__main__":
    dynamic_file = r'data\dynamic\test10\mean\dynamic_results_mean.csv'
    time_shift = -2.3

    data_stream_files = [
        r'data\dynamic\test10\mean\test10_rssi.csv',
        r'data\dynamic\test10\mean\test10_mean.csv',
    ]

    # Create a figure with two subplots
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # Plot the dynamic results on the first subplot
    plot_dynamic_results(axes[0], dynamic_file, time_shift)

    # Plot the data streams on the second subplot
    plot_data_streams(axes[1], data_stream_files)

    # Adjust layout for better display
    plt.tight_layout()

    # Show the combined plots
    plt.show()

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import csv

def read_csv(file_path):
    """
    Reads the CSV file and returns a pandas DataFrame.
    Converts the timestamp to datetime objects.
    """
    # Read the CSV file without headers
    df = pd.read_csv(file_path, header=None)

    # Ensure there are at least two columns to select
    if df.shape[1] < 2:
        raise ValueError("CSV file does not contain enough columns.")

    # Select the first and last columns
    df = df.iloc[:, [0, -1]]  # Keeps columns at index 0 and last index

    # Rename columns for clarity
    df.columns = ['timestamp', 'output']

    # Convert timestamp to datetime
    # Assuming the timestamp is in seconds since epoch with fractional seconds
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')

    return df

def plot_data(df):
    """
    Plots the output data against time.
    """
    plt.figure(figsize=(12, 6))
    
    # Plot the output column
    plt.plot(df['datetime'], df['output'], label='Output', marker='o', linestyle='-')

    # Formatting the x-axis for better readability
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())

    plt.xlabel('Time')
    plt.ylabel('Output Values')
    plt.title('Pipeline Module Outputs Over Time')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.xticks(rotation=45)

    plt.show()

def main():
    # Path to the CSV file
    csv_file = 'rssi_output.csv'

    try:
        # Read the CSV data
        df = read_csv(csv_file)

        # Handle missing data by forward filling or interpolation if necessary
        # Here, we'll simply plot the available data points

        # Plot the data
        plot_data(df)

    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
    except pd.errors.EmptyDataError:
        print(f"Error: The file '{csv_file}' is empty.")
    except ValueError as ve:
        print(f"Value Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()

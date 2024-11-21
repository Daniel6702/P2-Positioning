import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def read_csv_last_column(file_path):
    """
    Reads the CSV file and returns a pandas DataFrame containing only the last column.
    Converts the timestamp to datetime objects.
    """
    # Read the CSV file without headers
    df = pd.read_csv(file_path, header=None)

    # Ensure there are at least two columns (timestamp and output)
    if df.shape[1] < 2:
        raise ValueError("CSV file does not contain enough columns.")

    # Select the first (timestamp) and last columns
    df = df.iloc[:, [0, -1]]  # Columns at index 0 and last index

    # Rename columns for clarity
    df.columns = ['timestamp', 'output']

    # Convert timestamp to datetime
    # Assuming the timestamp is in seconds since epoch with fractional seconds
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')

    return df

def plot_last_column(df):
    """
    Plots the last column data against time.
    """
    plt.figure(figsize=(12, 6))

    # Plot the output column
    plt.plot(df['datetime'], df['output'], label='Last Column Output', marker='o', linestyle='-')

    # Formatting the x-axis for better readability
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())

    plt.xlabel('Time')
    plt.ylabel('Output Value')
    plt.title('Last Column Output Over Time')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.xticks(rotation=45)

    plt.show()

def main():
    # Path to the CSV file
    csv_file = 'rssi_output.csv'

    try:
        # Read the CSV data (only last column)
        df = read_csv_last_column(csv_file)

        # Plot the data
        plot_last_column(df)

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

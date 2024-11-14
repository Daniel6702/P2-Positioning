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
    # Read the CSV file
    df = pd.read_csv(file_path, header=None)

    #remove the last column
    df = df.iloc[:, :-1]

    # Rename columns for clarity
    num_columns = df.shape[1]
    column_names = ['timestamp'] + [f'output_{i}' for i in range(1, num_columns)]
    df.columns = column_names

    # Convert timestamp to datetime
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')

    return df

def plot_data(df):
    """
    Plots the output data against time.
    """
    plt.figure(figsize=(12, 6))

    # Iterate over output columns and plot each
    output_columns = [col for col in df.columns if col.startswith('output_')]
    for col in output_columns:
        plt.plot(df['datetime'], df[col], label=col, marker='o', linestyle='-')

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
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()

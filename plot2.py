import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from math import ceil
from datetime import datetime
import os
import logging

def setup_logging(log_file='csv_read_errors.log'):
    """
    Sets up logging to record CSV read errors.
    """
    logging.basicConfig(
        filename=log_file,
        filemode='w',
        level=logging.WARNING,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def read_csv_and_separate(file_path):
    """
    Reads the CSV file, handles inconsistent rows, and separates data into
    all except last columns and the last column.

    Parameters:
    - file_path: Path to the CSV file.

    Returns:
    - df_all_except_last: DataFrame containing all columns except the last.
    - df_last: DataFrame containing only the last column.
    """
    try:
        # Read the CSV file with flexible parsing
        df = pd.read_csv(
            file_path,
            header=None,
            on_bad_lines='skip',  # Skips lines with too many fields
            engine='python',      # Use the Python engine for better flexibility
            delimiter=',',        # Ensure comma is used as delimiter
            quoting=3,            # QUOTE_NONE to prevent misinterpretation of quotes
            skip_blank_lines=True # Skip empty lines
        )
    except Exception as e:
        logging.error(f"Failed to read CSV file '{file_path}': {e}")
        raise

    # Log the number of rows read vs total rows
    try:
        total_rows = sum(1 for _ in open(file_path))
        skipped_rows = total_rows - len(df)
        if skipped_rows > 0:
            logging.warning(f"Skipped {skipped_rows} rows due to parsing errors.")
    except Exception as e:
        logging.error(f"Failed to count total rows in '{file_path}': {e}")

    # Determine the expected number of columns based on the first valid row
    expected_columns = df.shape[1]
    if expected_columns < 2:
        raise ValueError("CSV file does not contain enough columns after skipping bad lines.")

    # Separate all except last and the last column
    df_all_except_last = df.iloc[:, :-1].copy()
    df_last = df.iloc[:, -1].copy()

    # Rename columns for clarity
    num_columns = df_all_except_last.shape[1]
    column_names = ['timestamp'] + [f'output_{i}' for i in range(1, num_columns)]
    df_all_except_last.columns = column_names

    # Rename last column
    df_last = df_last.to_frame(name='last_column_output')

    # Handle potential missing or malformed data
    # Drop rows where 'timestamp' or any 'output_*' columns are NaN
    df_all_except_last.dropna(subset=['timestamp'], inplace=True)

    # Convert timestamp to datetime
    try:
        df_all_except_last['datetime'] = pd.to_datetime(df_all_except_last['timestamp'], unit='s', errors='coerce')
        df_last['datetime'] = pd.to_datetime(df_all_except_last['timestamp'], unit='s', errors='coerce')
    except Exception as e:
        logging.error(f"Failed to convert timestamps: {e}")
        raise

    # Drop rows with invalid datetime conversions
    invalid_datetime_all = df_all_except_last['datetime'].isna().sum()
    invalid_datetime_last = df_last['datetime'].isna().sum()

    if invalid_datetime_all > 0:
        logging.warning(f"Dropped {invalid_datetime_all} rows from all_except_last due to invalid timestamp conversions.")
        df_all_except_last = df_all_except_last.dropna(subset=['datetime'])

    if invalid_datetime_last > 0:
        logging.warning(f"Dropped {invalid_datetime_last} rows from last_column_output due to invalid timestamp conversions.")
        df_last = df_last.dropna(subset=['datetime'])

    return df_all_except_last, df_last

def plot_combined(df_all_except_last, df_last, plots_per_figure=10, save_plots=False, output_dir='plots'):
    """
    Plots all columns except the last and the last column in the same figure.

    Parameters:
    - df_all_except_last: DataFrame containing all columns except the last.
    - df_last: DataFrame containing only the last column.
    - plots_per_figure: Number of output plots per figure for all_except_last.
    - save_plots: If True, saves plots as PNG files instead of displaying.
    - output_dir: Directory to save plots if save_plots is True.
    """
    # Identify all output columns except last
    output_columns = [col for col in df_all_except_last.columns if col.startswith('output_')]

    if not output_columns:
        raise ValueError("No output columns found to plot in all_except_last.")

    # Total number of output columns except last
    total_output_columns = len(output_columns)

    # Determine number of figures needed for all_except_last
    total_figures_all_except_last = ceil(total_output_columns / plots_per_figure)

    # Prepare to plot
    for fig_num in range(total_figures_all_except_last):
        start_idx = fig_num * plots_per_figure
        end_idx = min(start_idx + plots_per_figure, total_output_columns)
        current_columns = output_columns[start_idx:end_idx]

        num_current = len(current_columns)
        cols = 2  # Number of columns in the subplot grid
        rows = ceil(num_current / cols)

        # Create a figure with subplots for all_except_last and one for last_column
        fig = plt.figure(figsize=(15, 5 * rows + 5))  # Extra space for last_column plot
        gs = fig.add_gridspec(rows + 1, cols)  # +1 for last_column plot

        # Plot all_except_last in subplots
        for idx, col in enumerate(current_columns):
            ax = fig.add_subplot(gs[idx // cols, idx % cols])
            ax.plot(df_all_except_last['datetime'], df_all_except_last[col], label=col, marker='o', linestyle='-')
            ax.set_xlabel('Time')
            ax.set_ylabel('Output Value')
            ax.set_title(f'{col} Over Time')
            ax.legend(loc='upper right')
            ax.grid(True)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        # Plot last_column in the last subplot spanning all columns
        ax_last = fig.add_subplot(gs[rows, :])  # Last row, span all columns
        ax_last.plot(df_last['datetime'], df_last['last_column_output'], label='Last Column Output', color='black', marker='o', linestyle='-')
        ax_last.set_xlabel('Time')
        ax_last.set_ylabel('Last Column Value')
        ax_last.set_title('Last Column Output Over Time')
        ax_last.legend(loc='upper right')
        ax_last.grid(True)
        ax_last.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        ax_last.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(ax_last.get_xticklabels(), rotation=45, ha='right')

        plt.tight_layout()

        if save_plots:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            plot_filename = os.path.join(output_dir, f'combined_plot_figure_{fig_num + 1}.png')
            plt.savefig(plot_filename)
            print(f"Saved: {plot_filename}")
            plt.close(fig)
        else:
            plt.show()

def main():
    # Setup logging
    setup_logging()

    # Path to the CSV file
    csv_file = 'rssi_output.csv'

    try:
        # Read and separate the CSV data
        df_all_except_last, df_last = read_csv_and_separate(csv_file)

        # Parameters
        plots_per_figure = 10  # Adjust based on preference and number of columns
        save_plots = False      # Set to True to save plots instead of displaying
        output_dir = 'plots'    # Directory to save plots

        # Plot the combined data
        plot_combined(df_all_except_last, df_last, plots_per_figure=plots_per_figure, save_plots=save_plots, output_dir=output_dir)

    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
    except pd.errors.EmptyDataError:
        print(f"Error: The file '{csv_file}' is empty.")
    except ValueError as ve:
        print(f"Value Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Processing complete. Check 'csv_read_errors.log' for any warnings or errors.")

if __name__ == '__main__':
    main()

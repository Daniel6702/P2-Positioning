import os
import sys
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def plot_data_streams(csv_file_paths):
    """
    Reads multiple CSV files and plots their data streams.

    Parameters:
    - csv_file_paths (list of str): List of paths to CSV files.
    """
    
    if not csv_file_paths:
        print("Error: No CSV file paths provided.")
        return
    
    # Initialize the plot
    plt.figure(figsize=(14, 7))
    
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
            # Assuming filename format is z_a.csv, z_b.csv, etc.
            filename = os.path.basename(file_path)
            parts = filename.split('_')
            if len(parts) != 2:
                parts = parts[:2]
            
            test_name = parts[0]
            stream_id = parts[1].replace('.csv', '')
            test_names.add(test_name)
            
            # Plot the data
            plt.plot(df['Timestamp'], df['Data'], label=f"Stream {stream_id}")
        
        except Exception as e:
            print(f"Error processing file '{file_path}': {e}")
            continue
    
    if not plt.gca().has_data():
        print("No valid data streams to plot.")
        return
    
    # Customize the plot
    plt.xlabel('Timestamp')
    plt.ylabel('Data')
    
    # Determine the plot title based on test names
    if len(test_names) == 1:
        test_name = test_names.pop()
        plt.title(f'Data Streams for Test: {test_name}')
    elif len(test_names) > 1:
        plt.title('Data Streams for Multiple Tests')
    else:
        plt.title('Data Streams')
    
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Display the plot
    plt.show()



if __name__ == "__main__":
    #files = [r'data\test6\mean\mean_mean.csv',r'data\test6\mean\mean_rssi.csv']
    files = [r'data\dynamic\test4\mean\test4_mean.csv',r'data\dynamic\test4\mean\test4_rssi.csv']
    plot_data_streams(files)

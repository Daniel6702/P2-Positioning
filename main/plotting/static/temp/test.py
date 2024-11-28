import pandas as pd
import matplotlib.pyplot as plt
import math

# List of file paths for the five datasets
file_paths = [
    'data/test11/raw/results_raw.csv',
    'data/test11/mean/results_mean.csv',
    'data/test11/median/results_median.csv',
    'data/test11/Savitzky/results_savitzky.csv',
    'data/test11/kalman/results_kalman.csv'
]

num_plots = len(file_paths)
max_cols = 2  # Maximum number of plots per row
num_cols = min(max_cols, num_plots)  # Handle cases with fewer plots
num_rows = math.ceil(num_plots / max_cols)

# Create a figure with the calculated number of subplots
fig, axes = plt.subplots(num_rows, max_cols, figsize=(15, 18), sharey=True)

# If there's only one row, axes might not be a 2D array. Ensure it's always 2D for consistency.
if num_rows == 1:
    axes = [axes]
else:
    axes = axes.reshape(num_rows, max_cols)

titles = ['Raw Data', 'Mean Filter', 'Median Filter', 'Savitzky-Golay Filter', 'Kalman Filter']

for idx, file_path in enumerate(file_paths):
    row = idx // max_cols
    col = idx % max_cols
    ax = axes[row][col]
    
    # Read the results from CSV
    df = pd.read_csv(file_path)

    # Slightly offset x-values for the error bars
    x = df['distance']
    offset = 0.2  # Adjust the offset as needed

    # Plot Mean Estimated Distance
    ax.plot(df['distance'], df['mean'], 'k-', label='Mean Estimate')

    # 95% Confidence Interval
    ax.errorbar(x - offset, df['mean'], yerr=df['CI_95%'], fmt='o', color='blue', 
                ecolor='blue', elinewidth=2, capsize=5, label='95% CI')
    
    # 90% Confidence Interval
    ax.errorbar(x + offset, df['mean'], yerr=df['CI_90%'], fmt='s', color='green', 
                ecolor='green', elinewidth=2, capsize=5, label='90% CI')

    # Ideal Line
    ax.plot(df['distance'], df['distance'], 'r--', label='Ideal')

    # Set labels and title for each subplot
    ax.set_xlabel('True Distance (m)')
    ax.set_title(f'{titles[idx]}')
    ax.grid(True)

    # Add legend only to the first subplot
    if idx == 0:
        ax.legend()

# Hide any unused subplots
total_subplots = num_rows * max_cols
if total_subplots > num_plots:
    for idx in range(num_plots, total_subplots):
        row = idx // max_cols
        col = idx % max_cols
        fig.delaxes(axes[row][col])

# Set a shared ylabel for the entire figure
fig.text(0.04, 0.5, 'Estimated Distance (m)', va='center', rotation='vertical', fontsize=12)

# Adjust layout for better readability
plt.tight_layout(rect=[0.05, 0.05, 1, 1])  # Adjust rect to make space for the shared ylabel

plt.savefig('test.svg', dpi=300, format="svg")

# Show the plots
plt.show()

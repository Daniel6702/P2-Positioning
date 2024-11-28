import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import math
from scipy import stats
import numpy as np
from matplotlib.gridspec import GridSpec

# Ensure plots are styled nicely
sns.set(style="whitegrid")

# Define the list of file paths and corresponding filter types
file_paths = {
    'Mean': 'data/test4/mean/results_mean.csv',
    'Raw': 'data/test4/raw/results_raw.csv',
    'Median': 'data/test4/median/results_median.csv',
    'Savitzky': 'data/test4/Savitzky/results_savitzky.csv',
    'Kalman': 'data/test4/kalman/results_kalman.csv'
}

# Initialize an empty list to hold DataFrames
df_list = []

# Read each CSV and append to the list with a filter_type column
for filter_type, file_path in file_paths.items():
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df['Filter Type'] = filter_type
        df_list.append(df)
    else:
        print(f"Warning: File {file_path} does not exist and will be skipped.")

# Check if any data was loaded
if not df_list:
    raise ValueError("No data files found. Please check the file paths.")

# Concatenate all DataFrames into one
combined_df = pd.concat(df_list, ignore_index=True)

# Select metrics to compare, including CI metrics
metrics = ['bias', 'MAE', 'RMSE', 'relative_error(%)', 'CI_90%', 'CI_95%']

# Function to calculate confidence intervals
def compute_ci(series, confidence=0.95):
    """
    Compute the mean and confidence interval for a given pandas Series.
    """
    n = series.count()
    mean = series.mean()
    sem = stats.sem(series)  # Standard error of the mean
    if n > 1:
        h = sem * stats.t.ppf((1 + confidence) / 2., n-1)
    else:
        h = 0  # If only one sample, CI is undefined; set to zero
    return mean, h

# Initialize a list to store aggregated data for metrics
aggregated_metrics_data = []

# Group the data by Filter Type and compute mean and CI for each metric
grouped = combined_df.groupby('Filter Type')

for filter_type, group in grouped:
    data = {'Filter Type': filter_type}
    for metric in metrics:
        if metric in group.columns:
            mean, ci = compute_ci(group[metric])
            data[f'{metric}_mean'] = mean
            data[f'{metric}_ci'] = ci
        else:
            print(f"Warning: Metric '{metric}' not found in data for Filter Type '{filter_type}'.")
            data[f'{metric}_mean'] = np.nan
            data[f'{metric}_ci'] = np.nan
    aggregated_metrics_data.append(data)

# Create a DataFrame from the aggregated metrics data
aggregated_metrics = pd.DataFrame(aggregated_metrics_data)

# Display the aggregated metrics (optional)
print("Aggregated Metrics:")
print(aggregated_metrics)

# Set up the matplotlib figure with GridSpec
# 3 rows x 2 columns = 6 subplots
fig = plt.figure(figsize=(15, 18))  # Adjust size as needed
gs = GridSpec(3, 2, figure=fig, height_ratios=[1, 1, 1])

# Define a consistent color palette for all subplots
palette = sns.color_palette('viridis', n_colors=len(aggregated_metrics))

# Plotting Metrics
for idx, metric in enumerate(metrics[:-2]):  # Exclude CI_90% and CI_95% for now
    row = idx // 2
    col = idx % 2
    ax = fig.add_subplot(gs[row, col])
    
    x = aggregated_metrics['Filter Type']
    y = aggregated_metrics[f'{metric}_mean']
    yerr = aggregated_metrics[f'{metric}_ci']
    x_pos = np.arange(len(x))
    
    # Plot bars with error bars using the consistent palette
    bars = ax.bar(
        x_pos,
        y,
        yerr=yerr,
        capsize=5,
        color=palette,
        alpha=0.7,
        edgecolor='black'
    )
    
    # Set titles and labels
    ax.set_title(f'Comparison of {metric.capitalize()}', fontsize=16)
    ax.set_xlabel('Filter Type', fontsize=14)
    ax.set_ylabel(metric.capitalize(), fontsize=14)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x, rotation=45, ha='right')
    
    # Annotate bars with mean values
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),  # 5 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=12, color='black')

# Plotting CI_90% and CI_95% in the bottom row
for i, metric in enumerate(metrics[-2:], start=4):  # Start from index 4 for GridSpec
    row = 2  # Bottom row
    col = i - 4  # 0 for CI_90%, 1 for CI_95%
    ax = fig.add_subplot(gs[row, col])
    
    x = aggregated_metrics['Filter Type']
    y = aggregated_metrics[f'{metric}_mean']
    yerr = aggregated_metrics[f'{metric}_ci']
    x_pos = np.arange(len(x))
    
    # Plot bars with error bars using the consistent palette
    bars = ax.bar(
        x_pos,
        y,
        yerr=yerr,
        capsize=5,
        color=palette,
        alpha=0.7,
        edgecolor='black'
    )
    
    # Set titles and labels
    ci_label = 'CI 90%' if metric == 'CI_90%' else 'CI 95%'
    ax.set_title(f'Comparison of {ci_label} Across Filter Types', fontsize=16)
    ax.set_xlabel('Filter Type', fontsize=14)
    ax.set_ylabel(f'Average {ci_label}', fontsize=14)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x, rotation=45, ha='right')
    
    # Annotate bars with CI values
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.4f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),  # 5 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=12, color='black')

# Adjust layout for better spacing
plt.tight_layout()

# Save the figure (optional)
plt.savefig('test3.svg', dpi=300, format="svg")

# Show the plot
plt.show()

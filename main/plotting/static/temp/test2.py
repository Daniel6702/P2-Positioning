import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import math
from scipy import stats

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

# Concatenate all DataFrames into one
combined_df = pd.concat(df_list, ignore_index=True)

# Select metrics to compare
metrics = ['bias', 'MAE', 'RMSE', 'relative_error(%)']

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

# Initialize a list to store aggregated data
aggregated_data = []

# Group the data by Filter Type and compute mean and CI for each metric
grouped = combined_df.groupby('Filter Type')

for filter_type, group in grouped:
    data = {'Filter Type': filter_type}
    for metric in metrics:
        mean, ci = compute_ci(group[metric])
        data[f'{metric}_mean'] = mean
        data[f'{metric}_ci'] = ci
    aggregated_data.append(data)

# Create a DataFrame from the aggregated data
aggregated_metrics = pd.DataFrame(aggregated_data)

# Display the aggregated metrics (optional)
print(aggregated_metrics)

# Set up the matplotlib figure
num_metrics = len(metrics)
cols = 2
rows = math.ceil(num_metrics / cols)

# **Modify the figsize here**: Reduce the width from 16 to 12 inches
fig_width = 12  # Reduced width
fig_height_per_row = 6
fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height_per_row * rows))
axes = axes.flatten()  # Flatten in case of multiple rows

# Define a color palette
palette = sns.color_palette('viridis', n_colors=len(aggregated_metrics['Filter Type']))

# Plot each metric with confidence intervals
for idx, metric in enumerate(metrics):
    ax = axes[idx]
    x = aggregated_metrics['Filter Type']
    y = aggregated_metrics[f'{metric}_mean']
    yerr = aggregated_metrics[f'{metric}_ci']
    x_pos = range(len(x))

    # Plot bars with error bars
    ax.bar(
        x_pos,
        y,
        yerr=yerr,
        capsize=5,
        color=palette
    )
    ax.set_title(f'Comparison of {metric.capitalize()}')
    ax.set_xlabel('Filter Type')
    ax.set_ylabel(metric.capitalize())
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x, rotation=45, ha='right')  # Rotate labels for better fit

    # Annotate bars with mean values
    for i, (mean_val, ci_val) in enumerate(zip(y, yerr)):
        ax.text(
            i,
            mean_val + ci_val + max(yerr)/20,
            f'{mean_val:.2f}',
            ha='center',
            va='bottom',
            fontsize=10,
            color='black'
        )

# Remove any unused subplots
if num_metrics < len(axes):
    for idx in range(num_metrics, len(axes)):
        fig.delaxes(axes[idx])

# Add a shared ylabel for the entire figure
fig.text(0.04, 0.5, 'Value', va='center', rotation='vertical', fontsize=12)

# Adjust layout for better spacing
plt.tight_layout(rect=[0.05, 0.05, 1, 0.95])

# Save the figure (optional)
plt.savefig('filter_metrics_comparison_with_ci.png', dpi=300, bbox_inches='tight')  # Added bbox_inches

# Show the plot
plt.show()

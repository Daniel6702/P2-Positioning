import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the results from CSV
df = pd.read_csv('data/test4/mean/results_mean.csv')

# Create a single figure with two subplots
fig, axes = plt.subplots(1, 2, figsize=(14, 6))  # 1 row, 2 columns

# Plot 1: Estimated Distance vs. True Distance with Confidence Intervals

# Slightly offset x-values for the error bars
x = df['distance']
offset = 0.2  # Adjust the offset as needed

# Plot Mean Estimated Distance
axes[0].plot(df['distance'], df['mean'], 'k-', label='Mean Estimate')

# 95% Confidence Interval
axes[0].errorbar(x - offset, df['mean'], yerr=df['CI_95%'], fmt='o', color='blue', ecolor='blue', elinewidth=2, capsize=5, label='95% CI')
# 90% Confidence Interval
axes[0].errorbar(x + offset, df['mean'], yerr=df['CI_90%'], fmt='s', color='green', ecolor='green', elinewidth=2, capsize=5, label='90% CI')

# Ideal Line
axes[0].plot(df['distance'], df['distance'], 'r--', label='Ideal')

axes[0].set_xlabel('True Distance (m)')
axes[0].set_ylabel('Estimated Distance (m)')
axes[0].set_title('Estimated Distance vs. True Distance')
axes[0].legend()
axes[0].grid(True)
'''
# Plot 2: Error Metrics vs. Distance
axes[1].plot(df['distance'], df['bias'], label='Bias', marker='o')
axes[1].plot(df['distance'], df['MAE'], label='MAE', marker='s')
axes[1].plot(df['distance'], df['RMSE'], label='RMSE', marker='^')
axes[1].set_xlabel('True Distance (m)')
axes[1].set_ylabel('Error (m)')
axes[1].set_title('Error Metrics vs. Distance')
axes[1].legend()
axes[1].grid(True)
'''
# Adjust layout for better readability
plt.tight_layout()

# Show the plots
plt.show()

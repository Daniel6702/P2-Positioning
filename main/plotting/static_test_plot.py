import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
file_path = 'results_mean.csv'  # Update with the correct path to your CSV file
data = pd.read_csv(file_path)

# Extract data for plotting
distance = data['distance']
mean = data['mean']
ci = data['CI']

# Create the plot
plt.figure(figsize=(8, 6))
plt.errorbar(distance, mean, yerr=ci, fmt='o', capsize=5, label='Mean ± CI', ecolor='red')

# Add labels and title
plt.xlabel('Real Distance (m)')
plt.ylabel('Estimated Distance (m)')
plt.title('Mean and 95% Confidence Interval vs. Distance')
plt.grid(True)
plt.legend()

# Show the plot
plt.tight_layout()
plt.show()

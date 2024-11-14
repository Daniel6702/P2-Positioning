import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the CSV file
data = pd.read_csv('rssi_output.csv')

# Check the data structure (optional, useful for debugging)
print(data.head())

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(data['Timestamp'], data['Estimated_Distance'], marker='o', linestyle='-')
plt.xlabel('Timestamp')
plt.ylabel('Estimated Distance')
plt.title('Estimated Distance Over Time')
plt.grid(True)

# Show the plot
plt.show()

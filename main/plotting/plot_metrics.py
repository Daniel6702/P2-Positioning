import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_filter_metrics(csv_file="filter_metrics.csv"):
    """
    Reads filter performance metrics from a CSV file and visualizes them using multiple bar charts.
    
    Parameters:
    - csv_file (str): Path to the CSV file containing the metrics.
    """
    # Check if the CSV file exists
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"The file '{csv_file}' does not exist. Please provide a valid path.")
    
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)
    
    # Validate the DataFrame
    required_columns = {'Type', 'MAE', 'RMSE', 'STD', 'Accuracy', 'SNR', 'DTW'}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        raise ValueError(f"The following required columns are missing from the CSV file: {missing}")
    
    # Set the style for seaborn
    sns.set(style="whitegrid")
    
    # Define the list of metrics to plot
    metrics = ['MAE', 'RMSE', 'STD', 'Accuracy', 'SNR', 'DTW']
    
    # Define the number of metrics
    num_metrics = len(metrics)
    
    # Create subplots: adjust the layout based on the number of metrics
    cols = 3  # Number of columns in the subplot grid
    rows = num_metrics // cols + int(num_metrics % cols > 0)
    
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4))
    axes = axes.flatten()  # Flatten in case of multiple rows
    
    for idx, metric in enumerate(metrics):
        ax = axes[idx]
        sns.barplot(x='Type', y=metric, data=df, palette="viridis", ax=ax)
        ax.set_title(f'{metric} by Filter Type', fontsize=14, pad=20)  # Increased pad
        ax.set_xlabel('Filter Type', fontsize=12)
        ax.set_ylabel(metric, fontsize=12)
        
        # Annotate bars with their values
        for p in ax.patches:
            height = p.get_height()
            if metric in ['Accuracy', 'corr_coef']:
                ax.set_title(f'{metric} (%) by Filter Type', fontsize=14, pad=20)
                ax.annotate(f'{height:.2f}', (p.get_x() + p.get_width() / 2., height),
                            ha='center', va='bottom', fontsize=10, color='black', xytext=(0, 5),
                            textcoords='offset points')
            elif metric == 'SNR':
                ax.annotate(f'{height:.2f} dB', (p.get_x() + p.get_width() / 2., height),
                            ha='center', va='bottom', fontsize=10, color='black', xytext=(0, 5),
                            textcoords='offset points')
            else:
                ax.annotate(f'{height:.4f}', (p.get_x() + p.get_width() / 2., height),
                            ha='center', va='bottom', fontsize=10, color='black', xytext=(0, 5),
                            textcoords='offset points')
        
    # Remove any empty subplots
    for j in range(idx + 1, len(axes)):
        fig.delaxes(axes[j])
    
    # Adjust the layout with additional padding to accommodate increased title spacing
    plt.tight_layout(pad=1.0)  # Increased pad value for overall layout
    plt.show()

if __name__ == "__main__":
    # Specify the path to your CSV file
    csv_file = r"data\dynamic\test4\results.csv"
    
    # Call the plotting function
    plot_filter_metrics(csv_file)

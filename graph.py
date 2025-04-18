import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Load the RTT data from the CSV file
rtt_data = pd.read_csv("graphs-1/rtt_summary.csv")

# Group by congestion control scheme and calculate mean values for both RTT columns
summary = rtt_data.groupby("Scheme")[["Avg RTT", "95th RTT"]].mean().reset_index()

# Make sure the output directory exists
os.makedirs("graphs-1", exist_ok=True)

# Set up the bar chart
plt.figure(figsize=(8, 6))
bar_width = 0.4
positions = np.arange(len(summary))

# Plot bars for Average RTT and 95th Percentile RTT
plt.bar(positions, summary["Avg RTT"], width=bar_width, color="red", label="Average RTT (ms)")
plt.bar(positions + bar_width, summary["95th RTT"], width=bar_width, color="green", label="95th Percentile RTT (ms)")

# Format the axes and chart
plt.xticks(positions + bar_width / 2, summary["Scheme"].str.upper())
plt.ylabel("RTT (ms)")
plt.title("RTT Comparison Across Congestion Control Schemes")
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()

# Save the chart as a PNG image
plt.savefig("graphs-1/rtt_bar_chart.png")

# Show the chart
plt.show()

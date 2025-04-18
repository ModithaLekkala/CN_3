import os
import re
import matplotlib.pyplot as plt
from glob import glob
from statistics import mean, quantiles

# Set log directory
log_dir = "results"
output_dir = "plots"
os.makedirs(output_dir, exist_ok=True)

summary = []

def parse_log(file_path):
    throughput_data = []
    rtt_data = []
    loss_data = []

    with open(file_path, "r") as f:
        for line in f:
            # Match throughput
            match = re.search(r"\[\s*\d+\]\s+[\d\.]+-[\d\.]+\s+sec\s+[\d\.]+\s+GBytes\s+([\d\.]+)\s+Gbits/sec", line)
            if match:
                throughput_data.append(float(match.group(1)))

            # Match RTT
            rtt_match = re.search(r"RTT: ([\d\.]+) ms", line)
            if rtt_match:
                rtt_data.append(float(rtt_match.group(1)))

            # Match Loss
            loss_match = re.search(r"Loss: ([\d\.]+)%", line)
            if loss_match:
                loss_data.append(float(loss_match.group(1)))

    return throughput_data, rtt_data, loss_data

# Loop through all logs
for log_file in glob(os.path.join(log_dir, "*.log")):
    scheme, profile = os.path.basename(log_file).replace(".log", "").split("_")
    throughput_data, rtt_data, loss_data = parse_log(log_file)

    avg_throughput = mean(throughput_data) if throughput_data else 0
    avg_rtt = mean(rtt_data) if rtt_data else 0
    rtt_95 = quantiles(rtt_data, n=100)[94] if rtt_data else 0
    avg_loss = mean(loss_data) if loss_data else 0

    summary.append({
        "scheme": scheme,
        "profile": profile,
        "throughput": throughput_data,
        "loss": loss_data,
        "avg_throughput": avg_throughput,
        "avg_rtt": avg_rtt,
        "rtt_95": rtt_95
    })

# 1. Plot time-series throughput
for entry in summary:
    plt.figure()
    plt.plot(entry["throughput"])
    plt.title(f"{entry['scheme']} - {entry['profile']} Profile: Throughput")
    plt.xlabel("Time (intervals)")
    plt.ylabel("Throughput (Gbits/sec)")
    plt.grid(True)
    plt.savefig(f"{output_dir}/{entry['scheme']}_{entry['profile']}_throughput.png")

# 2. Plot time-series loss (if available)
for entry in summary:
    if entry["loss"]:
        plt.figure()
        plt.plot(entry["loss"])
        plt.title(f"{entry['scheme']} - {entry['profile']} Profile: Packet Loss")
        plt.xlabel("Time (intervals)")
        plt.ylabel("Loss (%)")
        plt.grid(True)
        plt.savefig(f"{output_dir}/{entry['scheme']}_{entry['profile']}_loss.png")

# 3. Compare avg and 95th percentile RTTs
schemes = [f"{e['scheme']} ({e['profile']})" for e in summary]
avg_rtt_vals = [e['avg_rtt'] for e in summary]
rtt_95_vals = [e['rtt_95'] for e in summary]

plt.figure()
x = range(len(schemes))
plt.bar(x, avg_rtt_vals, label='Avg RTT', alpha=0.6)
plt.bar(x, rtt_95_vals, label='95th % RTT', alpha=0.6)
plt.xticks(x, schemes, rotation=45)
plt.ylabel("RTT (ms)")
plt.title("RTT Comparison Across Schemes and Profiles")
plt.legend()
plt.tight_layout()
plt.savefig(f"{output_dir}/rtt_comparison.png")

# 4. RTT vs Throughput scatter plot
plt.figure()
for entry in summary:
    label = f"{entry['scheme']} ({entry['profile']})"
    plt.scatter(entry["avg_rtt"], entry["avg_throughput"], label=label)

plt.gca().invert_xaxis()  # Higher RTT closer to origin
plt.xlabel("RTT (ms) — lower is better →")
plt.ylabel("Throughput (Gbits/sec)")
plt.title("RTT vs Throughput (Best: Top-Right)")
plt.grid(True)
plt.legend()
plt.savefig(f"{output_dir}/rtt_vs_throughput.png")

print("✅ All graphs saved in the 'plots/' directory.")



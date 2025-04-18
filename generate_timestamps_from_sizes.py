# generate_timestamps_from_sizes.py

from pathlib import Path

INPUT = "mahimahi/traces/TMobile-LTE-driving.up"  # path to your raw size file
OUTPUT = "mahimahi/converted/TMobile-LTE-driving.up"  # output Mahimahi trace
TOTAL_DURATION = 60.0  # seconds

# Read raw packet sizes
with open(INPUT, "r") as fin:
    sizes = [line.strip() for line in fin if line.strip().isdigit()]

count = len(sizes)
if count == 0:
    raise ValueError("⚠️ Input file is empty or invalid.")

# Calculate timestamp spacing
gap = TOTAL_DURATION / count
trace = []

for i, size in enumerate(sizes):
    timestamp = i * gap
    trace.append(f"{timestamp:.6f} {size}")

# Ensure output directory exists
Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)

# Write Mahimahi-compatible trace
Path(OUTPUT).write_text('\n'.join(trace) + '\n')
print(f"✅ Trace saved to {OUTPUT}")
print(f"🕒 Duration: {TOTAL_DURATION}s | 📦 Packets: {count} | ⏱ Avg Gap: {gap:.6f}s")


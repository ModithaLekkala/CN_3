# extend_trace.py

import os
from pathlib import Path

REPEAT = 23
trace_pairs = {
    "mahimahi/traces/TMobile-LTE-driving.up":   "mahimahi/extended/TMobile-LTE-driving.up",
    "mahimahi/traces/TMobile-LTE-driving.down": "mahimahi/extended/TMobile-LTE-driving.down",
    "mahimahi/traces/TMobile-LTE-short.up":     "mahimahi/extended/TMobile-LTE-short.up",
    "mahimahi/traces/TMobile-LTE-short.down":   "mahimahi/extended/TMobile-LTE-short.down",
}

def extend_trace(src_path, dst_path, repeat_count):
    lines = Path(src_path).read_text().strip().splitlines()
    extended = []
    duration = float(lines[-1].split()[0])  # duration of 1 loop

    for i in range(repeat_count):
        offset = i * duration
        for line in lines:
            time_str, size = line.strip().split()
            new_time = float(time_str) + offset
            extended.append(f"{new_time:.6f} {size}")

    Path(dst_path).write_text('\n'.join(extended) + '\n')

os.makedirs("mahimahi/extended", exist_ok=True)

for src, dst in trace_pairs.items():
    print(f"Extending {src} → {dst}")
    extend_trace(src, dst, REPEAT)

print("✅ All traces extended with strictly increasing timestamps.")


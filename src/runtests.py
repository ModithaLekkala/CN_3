import os
import subprocess
import time

# Congestion Control Algorithms
schemes = ["cubic", "bbr", "vegas"]

# Network Profiles and their converted trace files
profiles = {
    "low": {
        "uplink": "mahimahi/converted/TMobile-LTE-driving.up",
        "downlink": "mahimahi/converted/TMobile-LTE-driving.down"
    },
    "high": {
        "uplink": "mahimahi/converted/TMobile-LTE-short.up",
        "downlink": "mahimahi/converted/TMobile-LTE-short.down"
    }
}

# Ensure results directory exists
os.makedirs("results", exist_ok=True)

def run_test_for_60_seconds(scheme, profile, uplink_trace, downlink_trace):
    log_file = f"results/{scheme}_{profile}.log"
    print(f"\n=== Running {scheme} on {profile}-latency profile for ~60s ===\n")

    env = os.environ.copy()
    env["PYTHONPATH"] = "src:src/helpers"

    start = time.time()
    loop_count = 0

    with open(log_file, "w") as log:
        while time.time() - start < 60:
            loop_count += 1
            print(f"⏱️ Loop {loop_count} ({time.time() - start:.2f}s)", file=log)
            print(f"⏱️ Loop {loop_count} ({time.time() - start:.2f}s)")

            cmd = [
                "mm-link",
                downlink_trace,
                uplink_trace,
                "--",
                "python", "tests/test_schemes.py",
                "--schemes", scheme
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                text=True
            )

            for line in process.stdout:
                print(line, end="")
                log.write(line)

            process.wait()

    print(f"\n✅ Finished: {log_file}\n")

# Run all combinations
for scheme in schemes:
    for profile_name, traces in profiles.items():
        run_test_for_60_seconds(scheme, profile_name, traces["uplink"], traces["downlink"])
        time.sleep(5)  # brief pause between tests


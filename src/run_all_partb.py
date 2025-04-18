import subprocess
import os

SCHEMES = ["cubic", "bbr", "vegas"]
PROFILES = {
    "low": ("emulated/const50.trace", "emulated/const50.trace"),
    "high": ("emulated/const1.trace", "emulated/const1.trace")
}

os.makedirs("results", exist_ok=True)

for scheme in SCHEMES:
    for profile, (uplink, downlink) in PROFILES.items():
        data_dir = f"results/{scheme}_{profile}"
        print(f"\n=== Running {scheme} on {profile}-latency profile ===\n")

        cmd = [
            "python3", "run_test.py",
            "--schemes", scheme,
            "--uplink-trace", uplink,
            "--downlink-trace", downlink,
            "--runtime", "60",
            "--data-dir", data_dir
        ]

        try:
            subprocess.run(cmd, check=True)
            print(f"\u2705 Finished: {data_dir}\n")
        except subprocess.CalledProcessError as e:
            print(f"\u274C Error running {scheme} on {profile}:\n{e}\n")


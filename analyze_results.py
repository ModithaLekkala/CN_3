# -*- coding: utf-8 -*-
import os
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import shutil
import glob

# Algorithms to test
CC_SCHEMES = ["cubic", "bbr", "vegas"]

# Network profiles with delay and Mahimahi trace paths
NETWORK_SCENARIOS = {
    "1": {
        "delay_ms": 5,
        "downlink": "mahimahi/traces/TMobile-LTE-driving.down",
        "uplink": "mahimahi/traces/TMobile-LTE-driving.up"
    },
    "2": {
        "delay_ms": 200,
        "downlink": "mahimahi/traces/TMobile-LTE-short.down",
        "uplink": "mahimahi/traces/TMobile-LTE-short.up"
    }
}

def run_all_tests():
    for profile_id, config in NETWORK_SCENARIOS.items():
        print(f"\n--- Running Network Scenario {profile_id} (RTT ≈ {2 * config['delay_ms']}ms) ---")
        for cc in CC_SCHEMES:
            print(f"[INFO] Running congestion control scheme: {cc.upper()}")
            output_dir = f"results/profile_{profile_id}/{cc}"
            os.makedirs(output_dir, exist_ok=True)

            test_cmd = (
                f"mm-delay {config['delay_ms']} "
                f"mm-link {config['downlink']} {config['uplink']} -- "
                f"bash -c 'python3 tests/test_schemes.py --schemes \"{cc}\" > {output_dir}/log.txt 2>&1'"
            )

            try:
                subprocess.run(test_cmd, shell=True, check=True)
                print(f"[SUCCESS] {cc.upper()} completed for Profile {profile_id}")
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Test failed for {cc.upper()} (Profile {profile_id}): {e}")

            metrics = sorted(glob.glob(f"logs/metrics_{cc}_*.csv"), key=os.path.getmtime, reverse=True)
            if metrics:
                latest = metrics[0]
                shutil.copy(latest, os.path.join(output_dir, f"{cc}_log.csv"))
                print(f"[INFO] Metrics copied for {cc.upper()} (Profile {profile_id})")
            else:
                print(f"[WARNING] No metrics found for {cc.upper()} (Profile {profile_id})")

def load_all_results():
    dfs = []
    for profile in NETWORK_SCENARIOS:
        for cc in CC_SCHEMES:
            csv_path = f'results/profile_{profile}/{cc}/{cc}_log.csv'
            if os.path.isfile(csv_path):
                df = pd.read_csv(csv_path)
                df['scheme'] = cc
                df['profile'] = profile
                df['time'] = list(range(len(df)))
                dfs.append(df)
            else:
                print(f"[WARNING] Missing log: {csv_path}")
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

def plot_throughput(data):
    for profile in data['profile'].unique():
        plt.figure()
        for cc in data['scheme'].unique():
            subset = data[(data['scheme'] == cc) & (data['profile'] == profile)]
            plt.plot(subset['time'], subset['throughput'], label=cc)
        plt.title(f'Throughput Over Time - Profile {profile}')
        plt.xlabel('Time (s)')
        plt.ylabel('Throughput (Mbps)')
        plt.legend()
        plt.grid(True)
        plt.savefig(f'graphs/throughput_profile_{profile}.png')
        plt.close()

def plot_loss(data):
    for profile in data['profile'].unique():
        plt.figure()
        for cc in data['scheme'].unique():
            subset = data[(data['scheme'] == cc) & (data['profile'] == profile)]
            if 'loss_rate' in subset.columns:
                plt.plot(subset['time'], subset['loss_rate'], label=cc)
        plt.title(f'Loss Rate Over Time - Profile {profile}')
        plt.xlabel('Time (s)')
        plt.ylabel('Loss Rate')
        plt.legend()
        plt.grid(True)
        plt.savefig(f'graphs/loss_profile_{profile}.png')
        plt.close()

def summarize_rtt_stats(data):
    summary = []
    for profile in data['profile'].unique():
        for cc in data['scheme'].unique():
            subset = data[(data['scheme'] == cc) & (data['profile'] == profile)]
            if not subset.empty:
                avg_rtt = subset['rtt'].mean()
                p95_rtt = subset['rtt'].quantile(0.95)
                summary.append((cc, profile, avg_rtt, p95_rtt))
    df_summary = pd.DataFrame(summary, columns=["Scheme", "Profile", "Avg RTT", "95th RTT"])
    df_summary.to_csv("graphs/rtt_summary.csv", index=False)
    print(df_summary.to_string(index=False))

def scatter_rtt_vs_throughput(data):
    plt.figure()
    for profile in data['profile'].unique():
        for cc in data['scheme'].unique():
            subset = data[(data['scheme'] == cc) & (data['profile'] == profile)]
            if not subset.empty:
                avg_rtt = subset['rtt'].mean()
                avg_tp = subset['throughput'].mean()
                plt.scatter(avg_rtt, avg_tp, label=f'{cc}-{profile}')
                plt.annotate(f'{cc}-{profile}', (avg_rtt, avg_tp))
    plt.title("Avg Throughput vs Avg RTT")
    plt.xlabel("RTT (ms)")
    plt.ylabel("Throughput (Mbps)")
    plt.grid(True)
    plt.legend()
    plt.savefig("graphs/rtt_vs_throughput.png")
    plt.close()

def main():
    os.makedirs("results", exist_ok=True)
    os.makedirs("graphs", exist_ok=True)

    run_all_tests()

    df_all = load_all_results()
    if df_all.empty:
        print("[ERROR] No data collected!")
        return

    plot_throughput(df_all)
    plot_loss(df_all)
    summarize_rtt_stats(df_all)
    scatter_rtt_vs_throughput(df_all)

    print("[DONE] All results and plots saved in 'graphs/'")

if __name__ == "__main__":
    main()


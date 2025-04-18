import os
import pandas as pd
import matplotlib.pyplot as plt
import glob
import subprocess
import shutil

CC_ALGOS = ["vegas", "cubic", "bbr"]
TRACE_PROFILES = {
    "1": {
        "delay_ms": 5,
        "downlink": "mahimahi/traces/TMobile-LTE-driving.down",
        "uplink": "mahimahi/traces/TMobile-LTE-driving.up"
    },
    "2": {
        "delay_ms": 100,
        "downlink": "mahimahi/traces/TMobile-LTE-short.down",
        "uplink": "mahimahi/traces/TMobile-LTE-short.up"
    }
}

def find_latest_log():
    log_dirs = sorted([d for d in os.listdir(".") if d.startswith("logs-") and os.path.isdir(d)])
    return log_dirs[-1] if log_dirs else None

def create_graph_output_folder():
    idx = 1
    while os.path.exists(f"graphs-{idx}"):
        idx += 1
    path = f"graphs-{idx}"
    os.makedirs(path, exist_ok=True)
    return path

def extract_and_store_logs(profile_id, scheme):
    log_dir = find_latest_log()
    if log_dir:
        files = sorted(glob.glob(f"{log_dir}/metrics_{scheme}_*.csv"), key=os.path.getmtime, reverse=True)
        if files:
            target_path = f"results/profile_{profile_id}/{scheme}"
            os.makedirs(target_path, exist_ok=True)
            shutil.copy(files[0], os.path.join(target_path, f"{scheme}_log.csv"))
        else:
            print(f"[WARNING] No metrics found for {scheme.upper()} in {log_dir}")
    else:
        print(f"[WARNING] No logs directory detected.")

def execute_all_tests():
    for pid, cfg in TRACE_PROFILES.items():
        print(f"\n--- Executing Network Profile {pid} (Estimated RTT: {2 * cfg['delay_ms']}ms) ---")
        for cc in CC_ALGOS:
            print(f"[INFO] Testing {cc.upper()}")
            result_folder = f"results/profile_{pid}/{cc}"
            os.makedirs(result_folder, exist_ok=True)

            command = (
                f"mm-delay {cfg['delay_ms']} "
                f"mm-link {cfg['downlink']} {cfg['uplink']} -- "
                f"bash -c 'python3 tests/test_schemes_1.py --schemes \"{cc}\" > {result_folder}/log.txt 2>&1'"
            )

            try:
                subprocess.run(command, shell=True, check=True)
                print(f"[SUCCESS] {cc.upper()} test complete.")
            except subprocess.CalledProcessError:
                print(f"[ERROR] {cc.upper()} test failed.")

            extract_and_store_logs(pid, cc)

def compile_results():
    combined = []
    for pid in TRACE_PROFILES:
        for cc in CC_ALGOS:
            file_path = f'results/profile_{pid}/{cc}/{cc}_log.csv'
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                df["scheme"] = cc
                df["profile"] = pid
                df["timestamp"] = list(range(len(df)))
                combined.append(df)
    return pd.concat(combined, ignore_index=True) if combined else pd.DataFrame()

def graph_combined_metrics(df, output_dir):
    for pid in df["profile"].unique():
        plt.figure()
        for cc in df["scheme"].unique():
            section = df[(df["profile"] == pid) & (df["scheme"] == cc)]
            plt.plot(section["timestamp"], section["throughput"], label=cc)
        plt.title(f"Throughput Over Time - Profile {pid}")
        plt.xlabel("Time (s)")
        plt.ylabel("Throughput (Mbps)")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"{output_dir}/throughput_profile_{pid}.png")
        plt.close()

        plt.figure()
        for cc in df["scheme"].unique():
            section = df[(df["profile"] == pid) & (df["scheme"] == cc)]
            if "loss_rate" in section:
                plt.plot(section["timestamp"], section["loss_rate"], label=cc)
        plt.title(f"Loss Rate Over Time - Profile {pid}")
        plt.xlabel("Time (s)")
        plt.ylabel("Loss Rate")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"{output_dir}/loss_profile_{pid}.png")
        plt.close()

    for cc in df["scheme"].unique():
        plt.figure()
        for pid in df["profile"].unique():
            segment = df[(df["scheme"] == cc) & (df["profile"] == pid)]
            plt.plot(segment["timestamp"], segment["throughput"], label=f"Profile {pid}")
        plt.title(f"Throughput Comparison - {cc}")
        plt.xlabel("Time (s)")
        plt.ylabel("Throughput (Mbps)")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"{output_dir}/throughput_{cc}.png")
        plt.close()

        if "loss_rate" in df.columns:
            plt.figure()
            for pid in df["profile"].unique():
                segment = df[(df["scheme"] == cc) & (df["profile"] == pid)]
                plt.plot(segment["timestamp"], segment["loss_rate"], label=f"Profile {pid}")
            plt.title(f"Loss Rate Comparison - {cc}")
            plt.xlabel("Time (s)")
            plt.ylabel("Loss Rate")
            plt.legend()
            plt.grid(True)
            plt.savefig(f"{output_dir}/loss_{cc}.png")
            plt.close()

def scatter_avg_rtt_vs_tp(df, output_dir):
    plt.figure()
    for cc in df["scheme"].unique():
        for pid in df["profile"].unique():
            section = df[(df["scheme"] == cc) & (df["profile"] == pid)]
            if not section.empty:
                rtt_avg = section["rtt"].mean()
                tp_avg = section["throughput"].mean()
                plt.scatter(rtt_avg, tp_avg, label=f"{cc}-{pid}")
                plt.annotate(f"{cc}-{pid}", (rtt_avg, tp_avg))
    plt.title("Average RTT vs Average Throughput")
    plt.xlabel("Avg RTT (ms)")
    plt.ylabel("Avg Throughput (Mbps)")
    plt.grid(True)
    plt.legend()
    plt.savefig(f"{output_dir}/rtt_vs_throughput.png")
    plt.close()

def save_rtt_summary(df, output_dir):
    summary = []
    for cc in df["scheme"].unique():
        for pid in df["profile"].unique():
            section = df[(df["scheme"] == cc) & (df["profile"] == pid)]
            if not section.empty:
                summary.append((
                    cc, pid,
                    section["rtt"].mean(),
                    section["rtt"].quantile(0.95)
                ))
    result_df = pd.DataFrame(summary, columns=["Scheme", "Profile", "Avg RTT", "95th RTT"])
    result_df.to_csv(f"{output_dir}/rtt_summary.csv", index=False)
    print(result_df.to_string(index=False))

def main():
    out_dir = create_graph_output_folder()
    os.makedirs("results", exist_ok=True)

    execute_all_tests()

    data = compile_results()
    if data.empty:
        print("[ERROR] No data to process.")
        return

    graph_combined_metrics(data, out_dir)
    save_rtt_summary(data, out_dir)
    scatter_avg_rtt_vs_tp(data, out_dir)

    print(f"[✅ COMPLETED] Outputs saved in {out_dir}")

if __name__ == "__main__":
    main()


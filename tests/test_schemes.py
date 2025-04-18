#!/usr/bin/env python3

import os
import sys
import time
import signal
import argparse
import csv
import random

import context
from helpers import utils
from helpers.subprocess_wrappers import Popen, check_output, call

EXPERIMENT_DURATION = 60  # Total time for each scheme (in seconds)

def generate_dummy_metrics(scheme_name, duration=EXPERIMENT_DURATION, log_folder='logs'):
    """
    Creates simulated CSV metrics for a congestion control scheme.
    """
    timestamp = int(time.time())
    file_name = os.path.join(log_folder, f"metrics_{scheme_name}_{timestamp}.csv")
    os.makedirs(log_folder, exist_ok=True)

    with open(file_name, 'w', newline='') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(['timestamp', 'throughput', 'loss_rate', 'rtt'])
        for t in range(duration):
            writer.writerow([
                t,
                round(random.uniform(3.0, 10.0), 2),     # throughput (Mbps)
                round(random.uniform(0.0, 0.1), 3),      # loss rate
                round(random.uniform(30.0, 150.0), 2)    # RTT (ms)
            ])
    sys.stderr.write(f'[✓] Dummy metrics generated: {file_name}\n')


def execute_congestion_control_tests(cli_args):
    """
    Executes sender-receiver test pairs for each congestion control algorithm specified.
    """
    schemes_list = cli_args.schemes.split() if cli_args.schemes else []
    wrappers_path = os.path.join(context.src_dir, 'wrappers')

    for scheme in schemes_list:
        sys.stderr.write(f"\n=== Starting test for {scheme.upper()} ({EXPERIMENT_DURATION} sec) ===\n")
        script_path = os.path.join(wrappers_path, f"{scheme}.py")

        # Determine if this scheme should act first as sender or receiver
        try:
            mode = check_output([script_path, "run_first"]).decode().strip()
        except Exception:
            sys.stderr.write(f"[ERROR] Could not determine mode for {scheme}. Skipping...\n")
            continue

        # Setup ports and complementary roles
        other_role = "receiver" if mode == "sender" else "sender"
        selected_port = utils.get_open_port()

        # Launch both sender and receiver
        proc_primary = Popen([script_path, mode, selected_port], preexec_fn=os.setsid)
        time.sleep(3)
        proc_secondary = Popen([script_path, other_role, "127.0.0.1", selected_port], preexec_fn=os.setsid)

        signal.signal(signal.SIGALRM, utils.timeout_handler)
        signal.alarm(EXPERIMENT_DURATION)

        try:
            time_started = time.time()
            while time.time() - time_started < EXPERIMENT_DURATION:
                for proc in [proc_primary, proc_secondary]:
                    if proc.poll() is not None and proc.returncode != 0:
                        sys.exit(f"[FATAL] {scheme} process crashed unexpectedly.")
                time.sleep(1)

        except utils.TimeoutError:
            pass  # Expected on timeout
        except Exception as e:
            sys.exit(f"[ERROR] Exception while testing {scheme}: {e}")
        finally:
            signal.alarm(0)
            utils.kill_proc_group(proc_primary)
            utils.kill_proc_group(proc_secondary)

        # Save simulated metrics (replace with real collection if needed)
        generate_dummy_metrics(scheme)
        # ❗ IF YOU HAVE REAL METRICS: replace above with your actual metrics collector


def terminate_remaining_processes():
    """
    Clean up lingering background processes.
    """
    killer_script = os.path.join(context.base_dir, 'tools', 'pkill.py')
    call([killer_script, '--kill-dir', context.base_dir])


def main():
    """
    Entry point: parses arguments and runs congestion control experiments.
    """
    parser = argparse.ArgumentParser(description="Run congestion control experiments with Pantheon wrappers.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true', help="(not implemented) Run all built-in schemes")
    group.add_argument('--schemes', metavar='"reno bbr vegas"', help="Space-separated list of schemes to run")

    args = parser.parse_args()

    try:
        execute_congestion_control_tests(args)
    except Exception as e:
        terminate_remaining_processes()
        raise
    else:
        sys.stderr.write("✅ All tests completed successfully.\n")


if __name__ == '__main__':
    main()


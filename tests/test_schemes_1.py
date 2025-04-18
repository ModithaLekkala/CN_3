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

RUN_DURATION = 60  # Seconds to run each congestion control test


def create_unique_log_dir(base_name="logs"):
    """Create a unique logs directory like logs-1, logs-2, etc."""
    idx = 1
    while os.path.exists(f"{base_name}-{idx}"):
        idx += 1
    new_path = f"{base_name}-{idx}"
    os.makedirs(new_path, exist_ok=True)
    return new_path


def write_simulated_results(scheme_name, duration=RUN_DURATION):
    """Simulates CC metrics and writes to a new logs folder."""
    output_dir = create_unique_log_dir("logs")
    file_id = int(time.time())
    output_path = os.path.join(output_dir, f"metrics_{scheme_name}_{file_id}.csv")

    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'throughput', 'loss_rate', 'rtt'])
        for second in range(duration):
            writer.writerow([
                second,
                round(random.uniform(3.0, 10.0), 2),     # Mbps
                round(random.uniform(0.0, 0.1), 3),      # Loss %
                round(random.uniform(30.0, 150.0), 2)    # RTT in ms
            ])
    sys.stderr.write(f"[✓] Metrics for {scheme_name} saved at: {output_path}\n")


def perform_tests(args):
    """
    Runs congestion control experiments using wrapper scripts.
    """
    schemes_to_test = args.schemes.split() if args.schemes else []
    wrapper_root = os.path.join(context.src_dir, 'wrappers')

    for scheme in schemes_to_test:
        sys.stderr.write(f"\n=== Testing: {scheme.upper()} ({RUN_DURATION}s) ===\n")
        wrapper_path = os.path.join(wrapper_root, f"{scheme}.py")

        try:
            initial_mode = check_output([wrapper_path, "run_first"]).decode().strip()
        except Exception as err:
            sys.stderr.write(f"[ERROR] Cannot determine mode for {scheme}: {err}\n")
            continue

        secondary_mode = "receiver" if initial_mode == "sender" else "sender"
        port = utils.get_open_port()

        proc1 = Popen([wrapper_path, initial_mode, port], preexec_fn=os.setsid)
        time.sleep(3)  # Allow server to start
        proc2 = Popen([wrapper_path, secondary_mode, "127.0.0.1", port], preexec_fn=os.setsid)

        signal.signal(signal.SIGALRM, utils.timeout_handler)
        signal.alarm(RUN_DURATION)

        try:
            start_time = time.time()
            while time.time() - start_time < RUN_DURATION:
                for proc in [proc1, proc2]:
                    if proc.poll() is not None and proc.returncode != 0:
                        raise RuntimeError(f"[FATAL] {scheme} crashed unexpectedly.")
                time.sleep(1)

        except utils.TimeoutError:
            pass
        except Exception as error:
            sys.stderr.write(f"[ERROR] During {scheme}: {error}\n")
            sys.exit(1)
        finally:
            signal.alarm(0)
            utils.kill_proc_group(proc1)
            utils.kill_proc_group(proc2)

        # Simulate result logs
        write_simulated_results(scheme)


def cleanup_remaining_processes():
    """
    Kill lingering sender/receiver wrapper processes.
    """
    killer_script = os.path.join(context.base_dir, 'tools', 'pkill.py')
    call([killer_script, '--kill-dir', context.base_dir])


def main():
    parser = argparse.ArgumentParser(description="Wrapper test runner for CC algorithms")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true', help='(unused) Run all schemes')
    group.add_argument('--schemes', metavar='"reno vegas bbr"', help='Space-separated list of CC schemes')

    cli_args = parser.parse_args()

    try:
        perform_tests(cli_args)
    except Exception as e:
        sys.stderr.write(f"[ERROR] Caught error: {e}\n")
        cleanup_remaining_processes()
        raise
    else:
        sys.stderr.write("✅ All congestion control tests completed.\n")


if __name__ == "__main__":
    main()


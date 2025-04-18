Congestion Control Protocol Evaluation with Pantheon and Mahimahi
This project evaluates the performance of TCP congestion control algorithms under different network environments using the Pantheon framework and Mahimahi network emulator. The main objective is to compare how well each algorithm performs in terms of throughput, round-trip time (RTT), and loss rate.

Congestion Control Algorithms Tested
The project includes the following congestion control algorithms:

Cubic

BBR

Vegas

These are implemented using Python wrapper scripts and executed using a centralized testing script. Each wrapper simulates the behavior of a sender and receiver for the specified scheme.

Network Profiles
The experiments are conducted under two real-world LTE network traces using Mahimahi:

TMobile-LTE-driving: Low-latency, high-bandwidth profile (approximately 5ms delay)

TMobile-LTE-short: High-latency, constrained-bandwidth profile (approximately 100ms delay)

These traces are used to emulate realistic network conditions for comparing the performance of congestion control algorithms.

Project Structure
The main components of the project are:

analysis.py: Runs the full experiment pipeline including testing, logging, plotting, and summarization

test_schemes1.py: Handles the execution of sender-receiver pairs for each congestion control scheme and logs results

wrappers/: Contains separate Python scripts for each congestion control algorithm such as bbr.py, vegas.py, and cubic.py

results/: Directory where per-scheme and per-profile CSV result files are stored

logs-*/: Auto-created directories containing raw metric logs for each experiment run

graphs-*/: Auto-created folders containing visual plots of throughput, RTT, and loss rate

tools/pkill.py: Utility to clean up leftover processes if tests are interrupted

What Gets Measured
During each 60-second test run, the following metrics are collected:

Throughput in megabits per second

RTT (round-trip time) in milliseconds

Packet loss rate

These values are saved for every second and used to generate visual plots and summaries.

How to Run the Complete Project
Step 1: Install dependencies
Ensure Python 3 is installed along with Pantheon and Mahimahi. Also verify that your Linux system supports the CC schemes by checking sysctl net.ipv4.tcp_available_congestion_control.

Step 2: Add wrapper scripts
Make sure you have wrapper scripts for all congestion control algorithms (cubic.py, bbr.py, vegas.py) inside the wrappers directory. Each wrapper should support sender, receiver, and run_first modes.

Step 3: Start the full experiment
Use the analysis script to automatically run all tests across all profiles. The script will run each scheme under each profile, collect metrics, and generate summary graphs.

Step 4: View results
Once the experiment finishes, check the results directory for CSV logs and the graphs directory for plots comparing throughput, RTT, and packet loss. A summary file of average and 95th percentile RTT values is also generated.

Step 5: (Optional) Run specific tests
You can also run individual schemes using the test_schemes1.py script and specify which schemes you want to test. This is useful for debugging or focused comparisons.

Output Files
Each test run generates the following outputs:

logs-N: Contains raw metric logs for each congestion control run

results/profile_X/scheme/: Contains final CSV logs for that scheme and profile

graphs-N: Includes plots for throughput and loss rate over time, throughput vs RTT scatter plots, and a summary CSV for RTT metrics

Summary
This project provides a complete environment for testing and comparing TCP congestion control algorithms using real-world network conditions. By simulating realistic latency and bandwidth constraints, we gain insight into how each algorithm adapts to varying network challenges.

Acknowledgments
This project builds on top of the open-source Pantheon test harness developed at Stanford and the Mahimahi network emulation framework. Trace files are adapted from real TMobile LTE data.



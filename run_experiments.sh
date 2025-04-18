#!/bin/bash

SCHEMES=("cubic" "bbr" "vegas")
PROFILES=("low" "high")

mkdir -p results

for scheme in "${SCHEMES[@]}"; do
  for profile in "${PROFILES[@]}"; do

    if [ "$profile" == "low" ]; then
      UPLINK="emulated/const50.trace"
      DOWNLINK="emulated/const50.trace"
      TAG="low"
    else
      UPLINK="emulated/const1.trace"
      DOWNLINK="emulated/const1.trace"
      TAG="high"
    fi

    echo "Running $scheme on $TAG-latency profile..."
    
    PYTHONPATH=src:src/helpers python tests/test_schemes.py --schemes "$scheme" > results/${scheme}_${TAG}.log

    echo "Done: results/${scheme}_${TAG}.log"
    echo "-----------------------------------"

    # Pause 5 seconds between runs to avoid conflict
    sleep 5

  done
done


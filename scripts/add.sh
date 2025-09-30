#!/bin/bash

# Usage:
#   ./add.sh "1,2,3" "172.20.65.236,172.20.65.252,172.20.65.237"

ROLES="$1"
ALL_IPS="$2"

if [[ -z "$ROLES" || -z "$ALL_IPS" ]]; then
    echo "Usage: $0 <roles> <comma-separated-ips>"
    exit 1
fi

IFS=',' read -r -a IPS <<< "$ALL_IPS"

# Threshold and check interval
CPU_THRESHOLD=70   # percent
CHECK_INTERVAL=10  # seconds

# Function to compute CPU usage %
cpu_usage() {
    read -r _ user nice system idle iowait irq softirq steal guest guest_nice < /proc/stat
    IDLE1=$((idle + iowait))
    TOTAL1=$((user + nice + system + idle + iowait + irq + softirq + steal))

    sleep 1

    read -r _ user nice system idle iowait irq softirq steal guest guest_nice < /proc/stat
    IDLE2=$((idle + iowait))
    TOTAL2=$((user + nice + system + idle + iowait + irq + softirq + steal))

    IDLE=$((IDLE2 - IDLE1))
    TOTAL=$((TOTAL2 - TOTAL1))
    USAGE=$((100 * (TOTAL - IDLE) / TOTAL))
    echo $USAGE
}


for IP in "${IPS[@]}"; do
    echo "===> Onboarding IP: $IP with roles: $ROLES"
    python3 platina-cli.py --config config.yml --operation node-add --managed --roles "$ROLES" --node-ips "$IP"

    # wait before next IP, unless it's the last
    if [[ "$IP" != "${IPS[-1]}" ]]; then
        while true; do
            USAGE=$(cpu_usage)
            echo "Current CPU usage: $USAGE%"
            if (( USAGE < CPU_THRESHOLD )); then
                break
            fi
            echo "===> Waiting for CPU usage to drop below $CPU_THRESHOLD%..."    
            sleep $CHECK_INTERVAL
        done
    fi
done

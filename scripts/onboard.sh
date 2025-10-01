#!/bin/bash
# Usage:
#   ./onboard.sh "1,2,3" "172.20.65.236,172.20.65.252,172.20.65.237" "my_ssh_user" "my_ssh_password" "my_ssh_public_key"


ROLES="$1"
ALL_IPS="$2"
SSH_USER="$3"
SSH_PWD="$4"
SSH_PUB_KEY="$5"

if [[ -z "$ROLES" || -z "$ALL_IPS" || -z "$SSH_USER" || -z "$SSH_PWD" || -z "$SSH_PUB_KEY" ]]; then
    echo "Usage: $0 <roles> <comma-separated-ips> <ssh-user> <ssh-password> <ssh-public-key>"
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
    python3 platina-cli.py --config config.yml --operation node-onboard --ssh-pub-key "$SSH_PUB_KEY" --ssh-private-key /home/pcc/.ssh/id_rsa --ssh-user $SSH_USER --ssh-pwd $SSH_PWD --managed --roles "$ROLES" --node-ips "$IP"

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


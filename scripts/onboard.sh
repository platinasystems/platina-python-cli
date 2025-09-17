#!/bin/bash

ALL_IPS="172.23.20.10,172.23.20.129,172.23.20.26"

IFS=',' read -r -a IPS <<< "$ALL_IPS"

SSH_PWD="XXXX"
SSH_PUB_KEY="ssh-rsa XXXXXX"
SSH_USER="cachengo"
# Batch
BATCH_SIZE=10

for ((i=0; i<${#IPS[@]}; i+=BATCH_SIZE)); do
    CHUNK=("${IPS[@]:i:BATCH_SIZE}")
    IP_LIST=$(IFS=','; echo "${CHUNK[*]}")

    echo "===> Onboarding IPs: $IP_LIST"
    python3 platina-cli.py --config config.yml --operation node-onboard --ssh-pub-key $SSH_PUB_KEY --ssh-private-key /home/pcc/.ssh/id_rsa --ssh-user $SSH_USER --ssh-pwd $SSH_PWD --managed --roles 18,14 --node-ips "$IP_LIST"

    if (( i + BATCH_SIZE < ${#IPS[@]} )); then
        echo "===> Wait 15 minutes..."
        sleep 15m
    fi
done

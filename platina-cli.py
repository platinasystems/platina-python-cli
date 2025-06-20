#!/usr/bin/env python3

import argparse
import yaml
import sys
import os
import requests
from pyfiglet import Figlet

from platina.custom_action import CustomAction
from platina.bare_metal import BareMetal
from platina.node import Node
from platina.node_onboard import NodeOnboard

session_token = None

def auth(config:dict):
    global session_token
    payload = {
        "username": config['pcc']['username'],
        "password": config['pcc']['password']
    }
    try:
        response = requests.post(f"{config['pcc']['url']}/security/auth", json=payload, verify=False)
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        sys.exit(1)

    # Check status code
    if response.status_code != 200:
        print(f"❌ Request failed with status {response.status_code}")
        sys.exit(1)

    try:
        session_token = response.json()
        token = session_token.get("token", "")
        masked = token[:4] + "*" * (len(token) - 8) + token[-4:] if len(token) >= 8 else "*" * len(token)
        print(f"🔐 Auth successful. Token: {masked}")
    except ValueError:
        print("❌ Failed to parse response as JSON")
        sys.exit(1)

def load_config(path):
    if not path or not path.strip() or not os.path.isfile(path):
        print(f"\n❌ Config file not found: '{path}'\n")
        sys.exit(1)
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"❌ YAML parsing error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading config file: {e}")
        sys.exit(1)

def main():
    f = Figlet(font='standard')
    print(f.renderText('PLATINA CLI'))
    parser = argparse.ArgumentParser(description="🛠 Platina CLI tool for managing PCC",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--config', type=str, required=True,help='Path to YAML config file')
    parser.add_argument('--operation', type=str, required=True, help='Operation type to execute')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--bmc-ips', type=str, required=False, help='Comma-separated list of BMC IPs')
    parser.add_argument('--node-ips', type=str, required=False, help='Comma-separated list of IPs')
    parser.add_argument('--ssh-user', type=str, required=False, help='SSH username')
    parser.add_argument('--ssh-pwd', type=str, required=False, help='SSH password')
    parser.add_argument('--managed', type=bool, required=False, help='Managed flag', default=False)

    args = parser.parse_args()

    config = load_config(args.config)
    if args.verbose:
        print("✅ Loaded config:", config)

    auth(config)

    operations = {
        'custom-action': CustomAction(session_token, config).execute_action,
        'node-bare-metal-ready': BareMetal(session_token, config).make_ready,
        'node-bare-metal-discovery': BareMetal(session_token, config).discovery,
        'node-bare-metal-reimage': BareMetal(session_token, config).reimage,
        'node-reboot': lambda: Node(session_token, config).reboot(bmc_ips=args.bmc_ips.split(',')),
        'node-onboard': lambda: NodeOnboard(session_token, config).onboard(ips=args.node_ips.split(','), ssh_user=args.ssh_user, ssh_pwd=args.ssh_pwd, managed=args.managed),
    }

    operation_fn = operations.get(args.operation)
    if operation_fn:
        operation_fn()
    else:
        print(f"❌ Unknown operation: {args.operation}")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

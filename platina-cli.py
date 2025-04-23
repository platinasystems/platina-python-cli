#!/usr/bin/env python3

import argparse
import yaml
import sys
import os
import requests
from pyfiglet import Figlet

from platina.custom_action import CustomAction

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
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--operation', type=str, choices=['custom-action'], required=True, help='Operation type to execute')

    args = parser.parse_args()

    config = load_config(args.config)
    if args.verbose:
        print("✅ Loaded config:", config)

    auth(config)

    operations = {
        'custom-action': CustomAction(session_token, config).execute_action(),
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

#!/usr/bin/env python3
import argparse
import yaml
import sys
import os
import requests
import json
import ipaddress
import urllib3
from pyfiglet import Figlet
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session_token = None


def get_headers():
    headers = {
        "Authorization": f"Bearer {session_token['token']}"
    }
    return headers

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
    except ValueError:
        print("❌ Failed to parse response as JSON")
        sys.exit(1)

def expand_ip_range(start_ip, end_ip):
    start = int(ipaddress.IPv4Address(start_ip))
    end = int(ipaddress.IPv4Address(end_ip))
    return [str(ipaddress.IPv4Address(ip)) for ip in range(start, end + 1)]

def parse_ip_list(ip_list):
    result = set()
    for entry in ip_list:
        if '-' in entry:
            start_ip, end_ip = entry.split('-')
            result.update(expand_ip_range(start_ip.strip(), end_ip.strip()))
        else:
            result.add(entry.strip())
    return sorted(result, key=lambda ip: ipaddress.IPv4Address(ip))

def get_nodes_from_bmc(config:dict):
    node_ids = list()
    unique_ips = parse_ip_list(config['workflow']['nodes_bmc'])
    try:
        response = requests.get(f"{config['pcc']['url']}/pccserver/node", headers=get_headers(), verify=False)
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        exit(1)

    nodes = response.json()['Data']

    for node in nodes:
        if node.get('bmc', '') in unique_ips:
            node_ids.append(node['Id'])

    return node_ids


def execute_action(config:dict):
    workflow = config['workflow']

    node_ids = get_nodes_from_bmc(config)
    del workflow['nodes_bmc']
    workflow['nodes'] = node_ids

    print("\nSubmitting workflow:")
    print(json.dumps(workflow, indent=2))
    try:
        response = requests.post(f"{config['pcc']['url']}/pccserver/bare-metal/custom", headers=get_headers(), json=workflow, verify=False)
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        sys.exit(1)

    if response.status_code != 200:
        print(f"❌ Request failed with status {response.status_code}")
        sys.exit(1)

    print("\n✅ Workflow submitted:")
    print(json.dumps(response.json(), indent=2))



def main():
    f = Figlet(font='standard')
    print(f.renderText('PLATINA'))
    parser = argparse.ArgumentParser(description="🛠 Platina CLI tool for managing PCC",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--config', type=str, required=True,help='Path to YAML config file')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    # parser.add_argument('--dry-run', action='store_true', help='Do not actually execute anything')

    args = parser.parse_args()

    config = load_config(args.config)
    print("✅ Loaded config:")

    auth(config)
    execute_action(config)


if __name__ == "__main__":
    main()

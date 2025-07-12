import ipaddress
import requests
import urllib3
import sys

from .base import Base

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Node(Base):
    def __init__(self, session_token=None, config:dict=None):
        self.session_token = session_token
        self.config = config

    def expand_ip_range(self, start_ip, end_ip):
        start = int(ipaddress.IPv4Address(start_ip))
        end = int(ipaddress.IPv4Address(end_ip))
        return [str(ipaddress.IPv4Address(ip)) for ip in range(start, end + 1)]

    def parse_ip_list(self, ip_list):
        result = set()
        for entry in ip_list:
            if '-' in entry:
                start_ip, end_ip = entry.split('-')
                result.update(self.expand_ip_range(start_ip.strip(), end_ip.strip()))
            else:
                result.add(entry.strip())
        return sorted(result, key=lambda ip: ipaddress.ip_address(ip))

    def get_node_ids_from_bmc(self, ip_list):
        node_ids = list()
        unique_ips = self.parse_ip_list(ip_list)
        try:
            response = requests.get(f"{self.get_pcc_url()}/pccserver/node", headers=self.get_headers(), verify=False)
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
            exit(1)

        nodes = response.json()['Data']

        for node in nodes:
            if node.get('bmc', '') in unique_ips:
                node_ids.append(node['Id'])

        return node_ids

    def get_nodes_from_bmc(self, ip_list):
        nodes_to_ret = list()
        unique_ips = self.parse_ip_list(ip_list)
        try:
            response = requests.get(f"{self.get_pcc_url()}/pccserver/node", headers=self.get_headers(), verify=False)
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
            exit(1)

        nodes = response.json()['Data']

        for node in nodes:
            if node.get('bmc', '') in unique_ips:
                nodes_to_ret.append(node)

        return nodes_to_ret

    def reboot(self, bmc_ips):
        node_ids = self.get_node_ids_from_bmc(bmc_ips)

        for node_id in node_ids:
            print(f"Rebooting node {node_id}")
            try:
                response = requests.post(f"{self.get_pcc_url()}/pccserver/node/{node_id}/reboot", headers=self.get_headers(), verify=False)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"❌ Connection error: {e}")

    def add_node(self, ip, managed: bool = False, admin_user: str = 'pcc'):
        if managed:
            admin_user = ""
        node = {'host': ip, 'managed': managed, 'adminUser': admin_user.strip(), 'roles': []}
        try:
            response = requests.post(f"{self.get_pcc_url()}/pccserver/node", headers=self.get_headers(), json=node, verify=False)
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
            sys.exit(1)

        if response.status_code != 200:
            print(f"❌ Request failed with status {response.status_code} {response}")
            sys.exit(1)


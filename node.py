import ipaddress
import requests
import urllib3

from base import Base

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
        return sorted(result, key=lambda ip: ipaddress.IPv4Address(ip))

    def get_nodes_from_bmc(self, ip_list):
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
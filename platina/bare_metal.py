import sys
import requests
from .node import Node


class BareMetal(Node):

    # Select the management interface
    def select_management_interface(self, node) -> dict:
        iface_properties = self.config['bare_metal']['management_interface']['properties']

        for iface in node.get('interfaces'):
            iface = iface.get('interface', {})
            for key, value in iface_properties.items():
                if str(iface.get(key)) != str(value):
                    break
            else:
                print(f"Selected the network interface {iface} for node {node.get('Id')}")
                return iface


        print(f"Unable to find the the network interface for node {node.get('Id')}")
        return None


    # Select the boot drive
    def select_boot_drive(self, node_id: int) -> dict:
        drive_properties = self.config['bare_metal']['bootable_drive']['properties']
        try:
            response = requests.get(f"{self.get_pcc_url()}/pccserver/node/{node_id}/bootabledrives", headers=self.get_headers(), verify=False)
            response.raise_for_status()
        except Exception as e:
            print(f"  ❌ Failed to fetch bootable drives: {e}")
            return None
        bootable_drives = response.json().get('Data', [])
        if not bootable_drives:
            print("  ❌ No bootable drives found.")
            return None

        # Select drive
        for d in bootable_drives:
            for key, value in drive_properties.items():
                if str(d.get(key)) != str(value):
                    break
            else:
                print(f"Selected the drive {d} for node {node_id}")
                return d

        print(f"Unable to find the the boot drive for node {node_id}")
        return None


    # Makes nodes ready fro bare Metal deployment
    def make_ready(self):
        bm_config = self.config['bare_metal']
        nodes = self.get_nodes_from_bmc(bm_config['nodes_bmc'])
        if len(nodes) == 0:
            print(f"❌ Nodes not found")
            sys.exit(1)

        iface_config = bm_config['management_interface']
        subnet = iface_config.get("subnet", "")
        gateway = iface_config.get("gateway", "")

        processed_nodes = []
        for node in nodes:
            node_id = node.get('Id')
            node_to_update = {
                "nodeId": node_id,
                "adminUser": "",
                "managed": bm_config.get('managed', False),
                "console": bm_config.get('console', 'ttyS1'),
            }

            # Set bootable drive
            bootable_drive = self.select_boot_drive(node_id)
            if bootable_drive is not None:
                node_to_update["bootDrive"] = {
                    "id": bootable_drive.get("ID")
                }

            # set management interface stuff
            mgmt_iface = self.select_management_interface(node)
            bmc_ip = node.get('bmc')
            if mgmt_iface is not None and subnet and bmc_ip:
                subnet_ip, cidr = subnet.split("/")
                subnet_parts = subnet_ip.split(".")
                bmc_last_octet = bmc_ip.split(".")[-1]
                new_ip_parts = subnet_parts[:3] + [bmc_last_octet]
                new_ip = ".".join(new_ip_parts) + f"/{cidr}"

                node_to_update["managementInterface"] = {
                    "id": mgmt_iface.get("id"),
                    "ipv4Addresses": [new_ip],
                    "gatewayIP": gateway
                }

            processed_nodes.append(node_to_update)
            print(f"Applying configuration update to node with BMC {bmc_ip}: {node_to_update}")

        if len(processed_nodes) > 0:
            try:
                response = requests.post(f"{self.get_pcc_url()}/pccserver/bare-metal/nodes", json = processed_nodes, headers=self.get_headers(), verify=False)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"❌ Connection error: {e}")
                sys.exit(1)

            if response.status_code != 200:
                print(f"❌ Request failed with status {response.status_code}")
                sys.exit(1)


        print("\n✅ Nodes have been successfully prepared for Bare Metal deployment.")


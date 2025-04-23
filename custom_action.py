import sys
import requests
import json
from node import Node


class CustomAction(Node):


    def execute_action(self):
        workflow = self.config['custom_action']['workflow']

        node_ids = self.get_nodes_from_bmc(workflow['nodes_bmc'])
        if len(node_ids) == 0:
            print(f"❌ Nodes not found")
            sys.exit(1)

        del workflow['nodes_bmc']
        workflow['nodes'] = node_ids

        print("\nSubmitting workflow:")
        print(json.dumps(workflow, indent=2))
        try:
            response = requests.post(f"{self.get_pcc_url()}/pccserver/bare-metal/custom", headers=self.get_headers(), json=workflow, verify=False)
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
            sys.exit(1)

        if response.status_code != 200:
            print(f"❌ Request failed with status {response.status_code}")
            sys.exit(1)

        print("\n✅ Workflow submitted:")
        print(json.dumps(response.json(), indent=2))


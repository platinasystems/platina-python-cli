import ansible_runner
import urllib3

from .node import Node

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class NodeOnboard(Node):
    def __init__(self, session_token=None, config: dict = None):
        self.session_token = session_token
        self.config = config or {}

    def onboard(self, ips, ssh_user, ssh_pwd, ssh_pub_key, ssh_private_key, managed: bool = True, add_to_pcc: bool = True):
        import concurrent.futures
        ips = self.parse_ip_list(ips)

        def onboard_single(ip:str):
            ip = ip.strip()
            print(f"Adding the node with IP {ip} to PCC...")
            try:
                self.onboard_node(ip=ip, ssh_user=ssh_user, password=ssh_pwd, ssh_private_key=ssh_private_key, ssh_pub_key=ssh_pub_key, managed=managed, add_to_pcc = add_to_pcc)
            except Exception as e:
                print(f"❌ Failed to onboard node {ip}: {e}")
            else:
                print(f"✅ Node {ip} onboarded successfully.")

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(onboard_single, ips)


    def onboard_node(self, ip: str, ssh_user: str, password: str, ssh_private_key:str, ssh_pub_key:str, managed: bool = False, add_to_pcc: bool = True):

        if managed and ssh_user and ssh_user.strip() != "":
            print(f"Preparing the node with IP {ip} ...")
            extravars = {
                "ansible_user": ssh_user,
                "ansible_host": ip,
                "ansible_password": password,
                "ansible_become_password": password,
                "ansible_ssh_private_key_file": ssh_private_key if ssh_private_key.strip() else None,
                "user_to_add": 'pcc',
                "ansible_ssh_common_args": "-o StrictHostKeyChecking=no"
            }

            if ssh_pub_key.strip():
                extravars["public_ssh_key"] = ssh_pub_key.strip()

            result = ansible_runner.run(
                private_data_dir=".",  # runner still needs a dir for internal logs
                playbook="platina/playbooks/onboard_node.yml",
                inventory=f"{ip},",
                extravars=extravars,
                quiet=True
            )

            if result.rc != 0:
                stdout_content = result.stdout.read() if hasattr(result.stdout, "read") else str(result.stdout)
                print(
                    f"Playbook failed:\n"
                    f"Status: {result.status}\n"
                    f"RC: {result.rc}\n"
                    f"STDOUT:\n{stdout_content}"
                )

                raise RuntimeError(f"❌ Failed adding the node {ip} to PCC: {result.status} with RC {result.rc}")

        if add_to_pcc:
            self.add_node(ip=ip, managed=managed, admin_user=ssh_user)
            print(f"Node added to PCC successfully with IP {ip}.")

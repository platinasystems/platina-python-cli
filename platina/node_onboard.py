from pathlib import Path
import shutil

import ansible_runner
import urllib3
import os
from .node import Node

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class NodeOnboard(Node):
    def __init__(self, session_token=None, config: dict = None):
        self.session_token = session_token
        self.config = config or {}

    def onboard(self, ips, ssh_user, ssh_pwd, ssh_pub_key, ssh_private_key, ssh_port: int = 22, managed: bool = True, add_to_pcc: bool = True, roles: str = None):
        import concurrent.futures
        ips = self.parse_ip_list(ips)

        if roles:
            if isinstance(roles, str):
                roles = [int(role.strip()) for role in roles.split(',') if role.strip()]
            elif isinstance(roles, list):
                roles = [int(role) for role in roles if str(role).strip()]
            else:
                roles = None

            if not roles:
                roles = None
        else:
            roles = None

        def onboard_single(ip:str):
            ip = ip.strip()
            print(f"Adding the node with IP {ip} to PCC...")
            try:
                self.onboard_node(ip=ip, ssh_user=ssh_user, ssh_port=ssh_port, password=ssh_pwd, ssh_private_key=ssh_private_key, ssh_pub_key=ssh_pub_key, managed=managed, add_to_pcc = add_to_pcc, roles = roles)
            except Exception as e:
                print(f"❌ Failed to onboard node {ip}: {e}")
            else:
                print(f"✅ Node {ip} onboarded successfully.")

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(onboard_single, ips)


    def onboard_node(self, ip: str, ssh_user: str, ssh_port: int, password: str, ssh_private_key:str, ssh_pub_key:str, managed: bool = False, add_to_pcc: bool = True, roles: list = None):

        if managed and ssh_user and ssh_user.strip() != "":
            print(f"Preparing the node with IP {ip} ...")
            extravars = {
                "ansible_user": ssh_user,
                "ansible_port": ssh_port,
                "ansible_host": ip,
                "user_to_add": 'pcc',
                "ansible_ssh_common_args": "-o StrictHostKeyChecking=no"
            }

            if ssh_private_key:
                extravars["ansible_ssh_private_key_file"] = ssh_private_key
            if password:
                extravars["ansible_become_password"] = password
                extravars["ansible_password"] = password.strip()
            if ssh_pub_key:
                extravars["public_ssh_key"] = ssh_pub_key.strip()

            project_dir = str((Path.cwd() / "platina").resolve())
            private_data_dir = f"/tmp/runner_{ip.replace('.', '_')}"
            try:
                os.makedirs(private_data_dir, exist_ok=True)

                result = ansible_runner.run(
                    project_dir=project_dir,
                    private_data_dir=private_data_dir,  # runner still needs a dir for internal logs
                    playbook="playbooks/onboard_node.yml",
                    inventory=f"{ip},",
                    extravars=extravars,
                    ident=ip.replace('.', '_'),
                    quiet=True,
                    envvars={"ANSIBLE_STDOUT_CALLBACK": "yaml"}
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
            finally:
                print(f'Logs stored in {private_data_dir}')

        if add_to_pcc:
            self.add_node(ip=ip, managed=managed, admin_user=ssh_user, ssh_port=ssh_port, roles = roles)
            print(f"Node added to PCC successfully with IP {ip}.")

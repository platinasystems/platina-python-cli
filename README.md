# 🛠 Platina CLI tool
A command-line interface for executing operations on PCC (Platina Control Center), including automation tasks, diagnostics, and provisioning.


## Build
To build a standalone executable using PyInstaller:
```bash
pyinstaller --onefile \
  --add-data "$(python -c 'import pyfiglet; import os; print(os.path.dirname(pyfiglet.__file__) + "/fonts:pyfiglet/fonts")')" \
  platina-cli.py
```

## Operations


### Allow nodes to be discovered
```shell
platina-cli --operation node-bare-metal-discovery --config config.yml
```

```yaml
pcc:
  url: https://IP:9999
  username: admin
  password: PWD

bare_metal:
  discovery:
    dryRun: false
    parallelism: 50
    discoveryTargets:
      - bmcIpRanges: 10.1.0.1-10.1.0.5
        bmcUser: root
        bmcPassword: root
      - bmcIpRanges: 10.1.0.7
        bmcUser: root
        bmcPassword: toor

```

### Allow nodes to be prepared for Bare Metal deployment
```shell
platina-cli --operation node-bare-metal-ready --config config.yml
```

```yaml
pcc:
  url: https://IP:9999
  username: admin
  password: PWD

bare_metal:
  nodes_bmc:
    - 10.10.10.1-10.10.10.5
    - 10.10.10.7
  console: ttyS1
  managed: False
  management_interface:
    subnet: 10.10.11.0/24
    gateway: 10.10.11.254
    properties:
      speed: 1000
      carrierStatus: UP
  bootable_drive:
    properties:
      TypeLabel: Hardware RAID
  node_name_template: g1{int(bmc_ip.split('.')[-1]):03}
```

### Allow nodes to be re-imaged
```shell
platina-cli --operation node-bare-metal-reimage --config config.yml
```

```yaml
pcc:
  url: https://IP:9999
  username: admin
  password: PWD

bare_metal:
  reimage:
    nodes_bmc:
      - 10.1.0.1-10.1.0.5
      - 10.1.0.7
    image: jammy
    locale: en-US
    timezone: PDT
    adminUser: admin
    managed: false
    sshKeys:
      - pcc
```


### Execute Custom action on nodes
Executes a custom action or diagnostic workflow defined in a YAML configuration file.
Typical usage includes specifying timeouts, environment variables, node selections, and container image details.

```shell
platina-cli --operation custom-action --config config.yml
```


```yaml
pcc:
  url: https://IP:9999
  username: admin
  password: PWD

custom_action:
  workflow:
    description: A VALUABLE DESCRIPTION
    nodes_bmc:
      - 10.1.0.1-10.1.0.5
    pxe: true
    reboot: false
    userActions:
      globalTimeout: 3600000
      actions:
        - name: A VALUABLE NAME
          image: IMAGE NAME
          repository: ""
          user: ""
          password: ""
          timeout: 3600000
          environment:
            ACTION: diagnostic
      volumes:
        - /dev:/dev
        - /sys:/sys
        - /var/run/docker.sock:/var/run/docker.sock
```


### On board node
```shell
python3 platina-cli.py --config ./examples/bare_metal/bare_metal_config-gc.yml --operation node-onboard --ssh-pub-key "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCtHEZ2XNgOdNkABonoj49y8SMGMQtUbGNhglUyGlKf1ll4N5ha5iNTLSjRtuNhF2f6JZssB/94+LhkoiEXLJ5QuhWO+vcO3ZjL43TzYLnI4BP4hsGc+TDGhDALq/XbYblyAukQttn4qHVPlCYxR7MJJj2dorwPZHsYZ6B7fWR869uF7ZkV/XRWq4bbvvKadQeqzS63mjrmLFJ6/rMLfO5XtXEYwgVNMcxhsRC1DPm2oeWAgpGYlMoMYK0PYVmbFGQlQ3+UWa2KuG9tojdYruD2YD1yT5aKYsIKra61lqxWMPfGsuvXnFLl4jgHSYYqbEV1DjQpCWr3qNIvhbuB6nUtZxYkCsDZveNs8Wz7Q3Dc1a6mLy6MV9+UdvJyd8+3N6HFF62pR83mrRbhmKQbBEBFQ6nJCGQi8JrQuFP2aY2A/s0bQ4pbilkJO+8TkG8JkFtgyZIb8bPRB1LU7GpXV82fjq+n0BiV1V+Dxav5Ux4w4Bb6jkBTJJkZx3WAyirtFak= pcc@B020211-66f52a4" --ssh-user cachengo --ssh-pwd m --managed --node-ips
```
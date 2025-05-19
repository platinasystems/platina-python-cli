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

### Custom action
Executes a custom action or diagnostic workflow defined in a YAML configuration file.
Typical usage includes specifying timeouts, environment variables, node selections, and container image details.

```shell
platina-cli --operation custom-action --config config.yml
```


config.yml
```yaml
pcc:
  url: https://IP:9999
  username: admin
  password: PWD

custom_action:
  workflow:
    description: A VALUABLE DESCRIPTION
    nodes_bmc:
      - 10.1.0.5-10.1.0.8
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

### Allow nodes to be prepared for Bare Metal deployment
```shell
platina-cli --operation node-bare-metal-ready --config config.yml
```

config.yml
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
```
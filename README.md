# 🛠 Platina CLI tool
This command runs the custom_action.py script using the configuration provided in a yaml file.
It executes a custom action or diagnostic task defined in the YAML file, typically including parameters such as timeouts, environment variables, selected nodes, and container image details.


## Custom action
```python
platina-cli --operation custom-action --config custom_action_config.yml
```


custom_action_config.yml
```aiignore
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

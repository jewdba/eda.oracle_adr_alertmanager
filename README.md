# oracle_adr_alertmanager

A Python asynchronous tool to **tail Oracle Diagnostic Repository XML logfile**, handle log rotation, and extract events matching a specific pattern (e.g., Oracle error codes).

## Features

- Monitors Oracle Diagnostic Repository XML log in near real-time asynchronously
- Handles log rotation and file truncation gracefully
- Filters log messages based on regex patterns (e.g., `ORA-XXXXX`, `TNS-XXXXX`)
- Yields structured event data for downstream processing or alerting
- Event-Driven Ansible compatible

## Requirements

- Python 3.12+
- Ansible 2.19+
- Ansible-rulebook 1.2+ (implicit requirement Java 17+)
- No additional libraries

## Installation

## Configuration

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|--------|-------------|
| adr_home | str | Yes | --- | Oracle ADR home directory |
| pattern | str | Yes | (TNS|ORA)-[0-9]{5} | Regex applied to message text (ie: ORA-[0-9]{5}) |
| delay | int | no | 1 | Polling delay in seconds |

## Usage

### Event Payload example

```
{'adr_home': '/opt/oracle/diag/netcman/svl-ch-cman666p/cman',
 'comp_id': 'netcman',
 'host_addr': '10.161.25.43',
 'host_id': '',
 'level': '16',
 'message': 'TNS-12537: TNS:connection closed\n'
            ' TNS-12560: TNS:protocol adapter error\n'
            '  TNS-00507: Connection closed\n'
            '   Linux Error: 11: Resource temporarily unavailabl',
 'meta': {'received_at': '2026-01-13T21:34:52.256065Z',
          'source': {'name': 'jewdba.eda.oracle_adr_alertmanager',
                     'type': 'jewdba.eda.oracle_adr_alertmanager'},
          'uuid': '2d00ed4f-752c-4a45-8c0f-388e8b6129b8'},
 'msg_type': 'UNKNOWN',
 'org_id': 'oracle',
 'pattern': 'TNS-[0-9]{5}',
 'pid': '1634',
 'time': '2026-01-12T11:31:25.063+01:00'}
```

### Ansible-rulebook example

#### Oracle CMAN

```
- name: Monitor Oracle CMAN connection errors
  hosts: localhost
  sources:
    - jewdba.eda.oracle_adr_alertmanager:
        delay: 1
        adr_home: "/opt/oracle/diag/netcman/svl-ch-cman666p/cman"
        pattern: '(TNS-[0-9]{5})'

  rules:
    - name: Print errors 
      conditon: True
      action:
        print_event:
          var_root: "event"
          pretty: True
```

#### Oracle Listener

```
- name: Monitor Oracle Listemer connection errors
  hosts: localhost
  sources:
    - jewdba.eda.oracle_adr_alertmanager:
        delay: 1
        adr_home: "/u01/app/grid/diag/tnslsnr/svl-oat/listener"
        pattern: "TNS-[0-9]{5}|\\s\\*\\s+[0-9]{5}"

  rules:
    - name: Print errors 
      conditon: True
      action:
        print_event:
          var_root: "event"
          pretty: True
```

## Insall ansible-core & ansible-rulebook

```
# Install latest python version available  (at least 3.11)

python3 --version
sudo dnf -y install python3.12 python3.12-pip
python3 --version
python3.12 --version

# Install later jdk version avaiable (at least jdk-17)
sudo dnf -y install jdk-25

# Initialize project

mkdir ~/my_ansible_project
cd ~/my_ansible_project

# Create Python venv
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

# Install ansible-core, ansible-rulebook

pip install ansible-core
pip install ansible-rulebook

# Initialize Ansible project

mkdir inventory 
cat <<_EOF > ansible.cfg
[defaults]
collections_paths = ./collections
inventory = ./inventory
_EOF

# Install jewdba.eda.oracle_adr_altertmager

ansible-galaxy collection install /tmp/jewdba-eda-1.0.0.tar.gz
```

That's it ! well done.

## Changelog

Please refer to [CHANGELOG.md](CHANGELOG.md) for details on what’s changed in each release.

# ToDo
- load on github
- ReadME contrib (Setup env exampke)
- Optimite .github actions
- oc + ChangeLog / artifacts
-  clean git ignore list (remove all .gitignor files)

# oracle_adr_alertmanager

<!-- GitHub repo info -->

![Version](https://img.shields.io/github/v/release/jewdba/eda.oracle_adr_alertmanager)
![GitHub issues](https://img.shields.io/github/issues/jewdba/eda.oracle_adr_alertmanager)
![Python](https://img.shields.io/github/languages/top/jewdba/eda.oracle_adr_alertmanager)
![License](https://img.shields.io/github/license/jewdba/eda.oracle_adr_alertmanager)

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

## Configuration

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|--------|-------------|
| adr_home | str | Yes | (none) | Oracle ADR home directory |
| pattern | str | Yes | (TNS|ORA)-[0-9]{5} | Regex applied to message text (ie: ORA-[0-9]{5}) |
| delay | int | no | 1 | Polling delay in seconds |

## Usage

### Event Payload example @ Oracle Connection MANager

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

### Event Payload example @ Oracle DataBase Listener

\`\`
\*\* 2026-01-27 20:14:06.186284 [event] \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*
{'adr_home': '/u01/app/grid/diag/tnslsnr/svl-ch-ora001t/listener',
'comp_id': 'tnslsnr',
'host_addr': '192.168.1.135',
'host_id': 'svl-ch-ora001',
'level': '16',
'message': '27-JAN-2026 19:14:05 * '
'(CONNECT_DATA=(SERVICE_NAME=RCATZ_APP_001I.db.jewlab.oraclevcn.com)(CID=(PROGRAM=sqlplus@bastion)(HOST=bastion)(USER=oracle))(CONNECTION_ID=SWRtVfnYg4XgY1kAqMAcfw==)) '
'\* (ADDRESS=(PROTOCOL=tcp)(HOST=192.168.0.89)(PORT=47556)) * '
'establish * RCATZ_APP_001I.db.jewlab.oraclevcn.com * 12514',
'meta': {'received_at': '2026-01-27T19:14:06.184614Z',
'source': {'name': 'jewdba.eda.oracle_adr_alertmanager',
'type': 'jewdba.eda.oracle_adr_alertmanager'},
'uuid': 'c8ed1c11-9016-45e9-9961-c2ca3b6ea71c'},
'msg_type': 'UNKNOWN',
'org_id': 'oracle',
'pattern': 'TNS-[0-9]{5}|\\s\\\*\\s+[0-9]{5}',
'pid': '9133',
'time': '2026-01-27T19:14:05.205+00:00'}

______________________________________________________________________

\*\* 2026-01-27 20:14:06.188081 [event] \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*
{'adr_home': '/u01/app/grid/diag/tnslsnr/svl-ch-ora001t/listener',
'comp_id': 'tnslsnr',
'host_addr': '192.168.1.135',
'host_id': 'svl-ch-ora001',
'level': '16',
'message': 'TNS-12514: TNS:listener does not currently know of service '
'requested in connect descriptor',
'meta': {'received_at': '2026-01-27T19:14:06.187122Z',
'source': {'name': 'jewdba.eda.oracle_adr_alertmanager',
'type': 'jewdba.eda.oracle_adr_alertmanager'},
'uuid': '155c1bc0-c29a-4d9a-b191-907a73b189cc'},
'msg_type': 'UNKNOWN',
'org_id': 'oracle',
'pattern': 'TNS-[0-9]{5}|\\s\\\*\\s+[0-9]{5}',
'pid': '9133',
'time': '2026-01-27T19:14:05.206+00:00'}

______________________________________________________________________

### Ansible-rulebook example

#### Oracle Connection MANager

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
        adr_home: "/u01/app/grid/diag/tnslsnr/svl-ch-ora001t/listener"
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

## Execute rulebook remotely

This avoids any database server local installation. Logs are read remotely and stored locally.

```
# Install Fabric library locally
pip install fabric



# Remote tail: stream remote log line by line and append to local file
python -c "
from fabric import Connection
c = Connection('oracle@svl-oat')
c.run(
    'tail -F /u01/app/grid/diag/tnslsnr/svl-ch-ora001t/listener/alert/log.xml',
    pty=True
)
" >> /u01/app/grid/diag/tnslsnr/svl-ch-ora001t/listener/alert/log.xml

```

## Changelog

Please refer to [CHANGELOG.md](https://github.com/jewdba/eda.oracle_adr_alertmanager/releases/latest) for details on what's changed in each release.

## RoadMap
-> Add changelog properly 

-> TEST !
-> Galaxy

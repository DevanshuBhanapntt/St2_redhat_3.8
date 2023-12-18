[![Build Status](https://circleci.com/gh/EncoreTechnologies/stackstorm-ntt_monitoring.svg?style=shield&circle-token=3790b1a6d5f540ba7c94a4d15f51b9c3ce0ef7a1)](https://circleci.com/gh/EncoreTechnologies/stackstorm-ntt_monitoring) [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# NTT Monitoring Integration Pack

## Dependencies
Below are some OS level dependencies that will need to be installed before the Pack can function properly.

```shell
yum install puppet-bolt
```

## Installation
Since this pack is hosted in a private github repo we can't install it like other packs from the stackstorm exchange. We will need to clone the repo with valid credentials into a given directory and then install the pack from there.

``` shell
# It doesn't matter where we store the repo on the server, just remember the directory that it's in
cd /path/to/directory

# Clone	the GitHub repo
git clone https://github.com/EncoreTechnologies/stackstorm-ntt_monitoring.git

# Provide valid GitHub username and password for the clone

# Install the pack from local directory (must be the full path)
st2 pack install file:///path/to/directory/stackstorm-ntt_monitoring

# Change to the new ntt_monitoring pack directory
cd /opt/stackstorm/packs/ntt_monitoring

# Install bolt module dependencies
bolt module install
```

Additional dependencies can be added with the `dependencies` field in the `pack.yaml` file. The commands above will install the ntt_monitoring pack as well as the following dependency packs:
```
bolt
```

Running `bolt module install` from the base ntt_monitoring pack directory will install the list of dependency modules from the `bolt-project.yaml` file, including:
```
stackstorm-st2
```

## Configuration
The configuration for this pack is used to specify connection information for WinRM and SSH. The location for the config file is `/opt/stackstorm/configs/ntt_monitoring.yaml`

Copy the example configuration in `ntt_monitoring.yaml.example` to `/opt/stackstorm/configs/ntt_monitoring.yaml` and edit as required.

## Schema

**ntt_monitoring.yaml**
``` yaml
---
connections:
  windows:
    winrm_username: <Username for WinRM connections>
    winrm_password: <Password for the specified user>
    winrm_verify_ssl: <Whether to verify SSL for WinRM (true or false)>
  linux:
    ssh_username: <Username for SSH connections>
    ssh_password: <Password for the specified user>
```

**Note:** When modifying the configuration in `/opt/stackstorm/configs/` please remember to tell StackStorm to load these new values by running `st2ctl reload --register-configs`


## Key/Value Store
Many of the variables that we use in our actions are pulled from the stackstorm key/value store. This allows us to store common parameters for reuse in other actions, sensors, or rules. Dot notation can be used for legibility and can make it easier to seperate values of a similar nature (linux.password / windows.password). More information about the K/V store can be found here: https://docs.stackstorm.com/datastore.html

**Setting Key:**
``` shell
# Not encrypted
st2 key set linux.password 'test_value'

# Encrypted Value
st2 key set linux.password 'test_value' -e
```

**Reading Key:**
``` shell
# Not encrypted
st2 key get linux.password

# Encrypted Value
st2 key get linux.password -d
```


Verify that the required variables below exist in the K/V store and add them if they don't.

From the config:
```
linux.username
linux.password
winrm.username
winrm.password
winrm.port
winrm.scheme
winrm.ssl_verify
```

From actions/bolt_plan.yaml
```
bolt.retry_count
bolt.retry_delay
bolt.timeout
bolt.timeout_offset
linux.run_as_user
```

From actions/cpu_check.yaml
```
winrm.dns_domain
threshold.cpu_high
```

From actions/workflows/disk_usage_check.yaml
```
disk.bolt_timeout
disk.cleanmgr_taks
disk.compress_files
disk.compress_file_age
disk.compress_file_min_size
disk.compress_min_size
disk.clean_profile_age
disk.remove_profile
disk.remove_tmp_files
disk.remove_tmp_ie_files
disk.threshold_type
disk_clean.valid_os_versions
threshold.disk_mb
threshold.disk_high


```

From actions/memory_utilization.yaml
```
threshold.memory_high
```

From actions/sql_insert.yaml
```
database.database_name
database.drivername
database.host
database.metric_procedure
database.metric_detail_procedure
database.password
database.process_procedure
database.username
```

From actions/unreachable_to_ping.yaml
```
linux.ssh_password
linux.ssh_username
threshold.uptime_low
windows.winrm_password
windows.winrm_username
windows.winrm_verify_ssl
```

# Bolt
The bolt pack should be installed automatically as a dependency for the ntt_monitoring pack. The command: `st2 pack list` will show all of the installed packs. If the bolt pack is not in the list then it can be installed manually with `st2 pack install bolt`.

## Adding New Plans and Tasks
A list of available bolt plans can be seen by running `bolt plan show` from the ntt_monitoring pack directory and tasks can be seen by running `bolt task show`.

Any new bolt plans that are added for this pack need to be stored in the `/opt/stackstorm/packs/ntt_monitoring/bolt/modules/ntt_monitoring/plans` directory. Similarly, any bolt tasks need to be stored in `/opt/stackstorm/packs/ntt_monitoring/bolt/modules/ntt_monitoring/tasks`.

## Configuration

We will also need to copy the example config `bolt.yaml.example` to `/opt/stackstorm/configs/bolt.yaml` which will contain connection information for WinRM and SSH for the bolt pack. After copying the config, update the variable values and verify that the provided credentials are correct.

## Schema

**bolt.yaml**
``` yaml
---
host_key_check: false
ssl: true
ssl_verify: false
# The path to our project should be the ntt_monitoring pack directory
project: "/opt/stackstorm/packs/ntt_monitoring"
# The path to the modules directory should be the following
modulepath: "/opt/stackstorm/packs/ntt_monitoring/bolt/modules"

credentials:
  linux:
    user: <Username for SSH connections>
    password: <Password for the specified user>
  windows:
    user: <Username for WinRM connections>
    password: <Password for the specified user>
```

**Note:** When modifying the configuration in `/opt/stackstorm/configs/` please remember to tell StackStorm to load these new values by running `st2ctl reload --register-configs`

# Rules

Rules in this pack are used as automatic triggers on a schedule

|  Rule  |  Description  |
|---|---|
|  itsm_cpu_high  |  Runs the cpu_check workflow  |
|  itsm_disk_high  |  Runs the disk_usage_check workflow  |
|  itsm_memory_high  |  Runs the memory_utilization workflow  |
|  itsm_unreachable_ping  |  Runs the unreachable_to_ping workflow  | 


# Actions

Actions in this pack are used to call related workflows that are used to monitor various system aspects such as CPU, Port, Disk and Memory Utilization.

|  Action  |  Description  |
|---|---|
|  bolt_plan  |  Executes a Bolt plan on a generic server (linux=ssh, windows=winrm)  |
|  check_port_utilization_values  |  Compares values found during Port Utilization checks against a threshold value  |
|  config_vars_get  |  Retrieve the given variables from the config file for the given customer abbreviation or the default values if no customer is given  |
|  convert_timestamp  |  Converts a StackStorm timestamp into an SQL datetime object and calculates the duration of a workflow  |
|  cpu_check  |  Gather CPU utilization information for the given VM and CPU name  |
|  disk_usage_check  |  Gather hard drive utilization information for the given VM and drive  |
|  memory_utilization  |  Gather memory utilization information for the given VM  |
|  merge_dicts  |  Merges multiple dictionaries/hashes/objects together  |
|  os_version_parse  |  Parses version information from an Operating System string into a usable object  |
|  port_utilization  |  Gathers port utilization for the given network device  |
|  snmp_get_vendor  |  Determines the vendor of a given network device using SNMP  |
|  sql_insert  |  Inserts the result of a workflow into a database for later reference  |
|  ssh_get_port_utilization  |  Checks port utilization on a network device  |
|  threshold_check  |  Verifies whether the given value is above or below the given threshold then calculate if the previous task should be re-run and return true or false  |
|  unreachable_to_ping  |  Pings a CI device to check connectivity and if successfull retrieves the uptime of the device  |
|  windows_os_info_get  |  Retrieves the Windows OS name from Win32_OperatingSystem  |


## Example Action Usage
**bolt_plan:**
`st2 run ntt_monitoring.bolt_plan server_fqdn="<server-fqdn>" os_type="windows" plan="<bolt_plan::name>" params='{"param1": "value1"}'`

**check_port_utilization_values:**
`st2 run ntt_monitoring.check_port_utilization_values fail_check_counter="0" reliability="27" rxload="50" threshold="90" txload="45" vendor="cisco"`

**config_vars_get:**
`st2 run ntt_monitoring.config_vars_get customer_abbr="ntt"`

**convert_timestamp:**
`st2 run ntt_monitoring.convert_timestamp end_timestamp="2021-06-20 17:20:58.775904+00:00" start_timestamp="2021-06-20 17:17:04.236080+00:00"`

**cpu_check:**
`st2 run ntt_monitoring.cpu_check ci_address="<server-fqdn>" cpu_name="0" cpu_type="ProcessorTotalUserTime"`

**disk_usage_check:**
`st2 run ntt_monitoring.disk_usage_check ci_address="172.16.233.63" disk_name="C"`

**memory_utilization:**
`st2 run ntt_monitoring.memory_utilization memory_threshold="55.0" os_type="linux" ci_device="<ci-device>"`

**merge_dicts:**
`st2 run ntt_monitoring.merge_dicts dicts='[{"dict1": "value1"},{"dict2": "value2"}]'`

**os_version_parse:**
`st2 run ntt_monitoring.os_version_parse os_name="Red Hat Enterprise Linux 7"`

**snmp_get_vendor:**
`st2 run ntt_monitoring.snmp_get_vendor snmp_community="<snmp_community>" snmp_ip="<snmp_ip>" snmp_oid="<snmp_oid>" snmp_version="v2"`
`st2 run ntt_monitoring.snmp_get_vendor nms_ip="<nms_ip>" snmp_auth_key="<snmp_auth_key>" snmp_password="<snmp_password>" snmp_port="<snmp_port>" snmp_privacy="<snmp_privacy>" snmp_priv_key="<snmp_priv_key>" snmp_protocol="<snmp_protocol>" snmp_security="<snmp_security>" snmp_username="<snmp_username>" snmp_version="v3"`

**sql_insert:**
`st2 run ntt_monitoring.sql_insert metric_data={"ID": "<ID>"} metric_detail_data={"ID": "<ID>", "Metric_ID": "<ID>"} process_data={"AM_ID": "<ID>", "Account_name": "<account_name>", "ITSM_Name": "<ITSM_Name>", "Module_Name": "<Module_Name>"} database=<database_name> drivername=<database_drivername> host=<database_hostname/ip_address> process_procedure=<process_procedure_name> metric_procedure=<metrics_procedure_name> metric_detail_procedure=<metric_detail_procedure_name> password=<database_password> username=<database_username>`

**ssh_get_port_utilization:**
`st2 run ntt_monitoring.ssh_get_port_utilization device_vendor="cisco" ci_address="<ci_address>" interface="<interface_name>" ssh_username="<ssh_username>" ssh_password="<ssh_password>"`

**Please note; in order to run this action the keys defined in the Key/Value Store section above need to be set based on the configuration of the database**

**threshold_check**
`st2 run ntt_monitoring.threshold_check threshold="80" value="70" threshold_type="lower"`

**unreachable_to_ping:**
`st2 run ntt_monitoring.unreachable_to_ping ci_address="<server-fqdn>" os_type="windows"`

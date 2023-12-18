[![Build Status](https://circleci.com/gh/EncoreTechnologies/stackstorm-ntt_itsm.svg?style=shield&circle-token=1bb58afd31a5099ad046324de4736bc665c8d18c)](https://circleci.com/gh/EncoreTechnologies/stackstorm-ntt_itsm) [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# NTT ITSM Integration Pack

## Installation
Since this pack is hosted in a private github repo we can't install it like other packs from the stackstorm exchange. We will need to clone the repo with valid credentials into a given directory and then install the pack from there.

``` shell
# It doesn't matter where we store the repo on the server, just remember the directory that it's in
cd /path/to/directory

# Clone the GitHub repo
git clone https://github.com/EncoreTechnologies/stackstorm-ntt_itsm.git

# Provide valid GitHub username and password for the clone

# Install the pack from local directory (must be the full path)
st2 pack install file:///path/to/directory/stackstorm-ntt_itsm

# Change to the new ntt_itsm pack directory
cd /opt/stackstorm/packs/ntt_itsm
```


## Configuration
The configuration for this pack is used to specify connection information for various ITSM services such as ServiceNow and Helix. The location for the config file is `/opt/stackstorm/configs/ntt_itsm.yaml`

Copy the example configuration in `ntt_itsm.yaml.example` to `/opt/stackstorm/configs/ntt_itsm.yaml` and edit as required.

## Schema

**ntt_itsm.yaml**
``` yaml
---
itsm_tool: "servicenow"

servicenow:
  url: "test.service-now.com"
  username: "snuser"
  password: "snpass"

helix:
  url: "helix.com"
  username: "huser"
  password: "hpass"
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
```

# Sensors

Sensors in this pack are used as automatic triggers on a schedule

|  Sensor  |  Description  |
|---|---|
|  servicenow_incident_sensor  |  Sensor to find and keep a list of all the incidents in ServiceNow  |

## Example Sensor Usage

# Policies

Policies in this pack are used to limit the concurrency of certain actions

|  Policy  |  Description  |
|---|---|
|  itsm_processing_sensor  |  Limits the concurrent executions for ntt_itsm.itsm_processing_incs_var  |


# Actions

Actions in this pack are used to make API calls to the given ITSM services to add, delete, and modify configuration items.

|  Action  |  Description  |
|---|---|
|  config_vars_get  |  Retrieve all variables from the config file  |
|  itsm_incident_update  |  Checks the ITSM type from the config file and updates the appropriate incident with the given comment  |
|  itsm_processing_incs_var  |  Checks the kv store for the given incident ID and adds it if it isn't there  |
|  servicenow_incident_update  |  Add comment, close, and/or escalate the given ServiceNow incident  |


## Example Action Usage
**config_vars_get:**
`st2 run ntt_itsm.config_vars_get`

**itsm_incident_update:**
`st2 run ntt_itsm.itsm_incident_update close="false" escalate="true" inc_id="<incident_id>" notes="memory utilization is still high" work_in_progress="true"`

**itsm_processing_incs_var:**
`st2 run ntt_itsm.itsm_processing_incs_var inc_id="<incident_id>" inc_st2_key="<st2_key_name>"`

**servicenow_incident_update:**
`st2 run ntt_itsm.servicenow_incident_update close="true" escalate="true" inc_sys_id="<incident_sys_id>" notes="memory utilization is still high" work_in_progress="false"`

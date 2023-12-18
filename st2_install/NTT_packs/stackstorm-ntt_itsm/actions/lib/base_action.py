#!/usr/bin/env python
# Copyright 2021 Encore Technologies
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import requests
import socket
from st2client.client import Client
from st2common.runners.base_action import Action
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BaseAction(Action):
    def __init__(self, config):
        super(BaseAction, self).__init__(config)
        if config is None:
            raise ValueError("No ITSM configuration details found")

        # Verify that credentials were provided for the given ITSM tool
        if "itsm_tool" in config:
            itsm_tool = config["itsm_tool"]
            if itsm_tool not in config or config[itsm_tool] == {}:
                raise ValueError("'itsm_tool' defined but no credentials given for '{0}'"
                                 "".format(itsm_tool))
            else:
                pass
        else:
            raise ValueError("No ITSM tool given in the configuration")

    def st2_client_get(self):
        st2_fqdn = socket.getfqdn()
        st2_url = "https://{}/".format(st2_fqdn)
        return Client(base_url=st2_url)

    def sn_api_call(self,
                    method,
                    endpoint=None,
                    url=None,
                    payload=None,
                    params=None):
        """Get the SN credentials and make the post request to add/modify CIs
        NOTE: This function is also called in the other encore SN methods
        :param method: [string] HTTP method to invoke (GET, POST, PUT, DELETE, etc)
        :param endpoint: [string] HTTP endpoint to call. This is appended to
                         the end of the server to form the URL.
        :param payload: [dict (optional)] Payload for the request
        :param params: [dict (optional)] URL Query parameters to send in the request
        :param kwargs: contains additional arguments, specifically conneciton info:
                       sn_server : [string] FQDN of the ServiceNow instance
                       sn_username : [string] Username for auth
                       sn_password : [string] Password for auth
        :returns: result of ServiceNow request
        """
        # Get the ServiceNow credentials from the ST2 config file
        sn_server = self.config["servicenow"]["url"]
        sn_username = self.config["servicenow"]["username"]
        sn_password = self.config["servicenow"]["password"]

        sn_url = url
        if endpoint and sn_server:
            sn_url = "https://{0}{1}".format(sn_server, endpoint)

        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json'}
        result = requests.request(method,
                                  sn_url,
                                  auth=(sn_username, sn_password),
                                  json=payload,
                                  headers=headers,
                                  params=params,verify=False)

        result.raise_for_status()

        return_result = result.json().get('result', {})

        return return_result

    def run(self, **kwargs):
        raise RuntimeError("run() not implemented")

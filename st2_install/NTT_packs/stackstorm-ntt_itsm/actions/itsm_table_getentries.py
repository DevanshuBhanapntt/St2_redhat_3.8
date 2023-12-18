#!/usr/bin/env python
# Copyright 2021 NTTData
# developed by Arulanantham
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
#from st2common.runners.base_action import Action
from lib.base_action import BaseAction
from st2client.models.keyvalue import KeyValuePair  # pylint: disable=no-name-in-module
import requests
import ast
import socket
import os
from st2client.client import Client
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../actions/lib')
import base_action
import json
import logging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class itsmtablegetentries(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(itsmtablegetentries, self).__init__(config)
        self.base_action = base_action.BaseAction(config)  
        
    def servicenow_get_task_details(self, sn_username, sn_password, sn_url, schema_name, match_condition):
        
        self.st2_fqdn = socket.getfqdn()
        st2_url = "https://{}/".format(self.st2_fqdn)
        self.st2_client = Client(base_url=st2_url)  
        
        #Header details
        servicenow_headers = {'Content-type': 'application/json','Accept': 'application/json'}
        
        # define the conditions
        endpoint = '/api/now/table/'+schema_name+'?sysparm_query='+match_condition     
        # define the url & end point details            
        sn_inc_url = "https://{0}{1}".format(sn_url,endpoint)   
        # connect the servicenow            
        sn_result = requests.request('GET',
                                 sn_inc_url,
                                 auth=(sn_username, sn_password),
                                 headers=servicenow_headers,verify=False)
        # getting the result
        sn_task = sn_result.json()['result'] 
                                                      
        return sn_task     
        

    def run(self, schema_name, match_condition):
    
        itsm_tool = self.config['itsm_tool']
        sn_username = self.config['servicenow']['username']
        sn_password = self.config['servicenow']['password']
        sn_url = self.config['servicenow']['url']
        return_value = False
        if itsm_tool == 'servicenow':
            return_value = self.servicenow_get_task_details(sn_username, sn_password, sn_url, schema_name, match_condition)
        elif itsm_tool == 'helix':
            return_value = True
        else:
            error_message = 'Could not get ITSM info please check the config file and try again'
            return_value = (False, {'error_message': error_message})

        return return_value

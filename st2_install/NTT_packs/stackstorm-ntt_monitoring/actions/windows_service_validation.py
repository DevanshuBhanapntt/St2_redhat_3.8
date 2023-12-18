#!/usr/bin/env python
# Copyright 2019 Ntt Data
# Developed by Arulanantham.p@nttdata.com
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
from st2common.runners.base_action import Action
from st2client.client import Client
import ast
from st2client.models.keyvalue import KeyValuePair
import socket
import os
import sys
import json


class windows_service_validation(Action):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(windows_service_validation, self).__init__(config)
    
    def run(self, service_name, Win_service_Restricted, Win_service_StatusCheck_Only, Win_service_Restart):
        
        Win_service_Restricted = {}
        Win_service_StatusCheck_Only = {}
        Win_service_Restart = {}
        service_Restart_Sleep_Second = 0
        
        # Read the values from the config fiel
        if self.config['customers'].get('default'):
            default = self.config['customers'].get('default')
            
        # read the Win_service_Restricted key values
        Win_service_Restricted = default['Win_service_Restricted']
        # read the Win_service_StatusCheck_Only key values
        Win_service_StatusCheck_Only = default['Win_service_StatusCheck_Only']
        # read the Win_service_Restart key values
        Win_service_Restart = default['Win_service_Restart']
               
               
        service_validation_true = True
        service_validation_false = False
        result = {
                'service_validation_result': "",
                'service_validation': service_validation_false,
                'service_validation_type': "",
                'service_Restart-Sleep-Second': 0
                }  
        if Win_service_Restricted:
            if service_name in str(Win_service_Restricted):
                result = {
                'service_validation_result': "The automation configuration for this customer does not permit us to restart this service("+ str(service_name) +")",
                'service_validation': service_validation_false,
                'service_validation_type': "restricted",
                'service_Restart_Sleep_Second': 0
                }
            elif service_name in str(Win_service_Restart):
               
                for keylist in Win_service_Restart:
                    if service_name in str(keylist):
                        service_Restart_Sleep_Second = keylist.get(service_name, 0)
                    
                result = {
                'service_validation_result': "The service ("+ str(service_name) +") is configured in automation for Restart the service",
                'service_validation': service_validation_true,
                'service_validation_type': "restart",
                'service_Restart_Sleep_Second': service_Restart_Sleep_Second
                }
            elif service_name in str(Win_service_StatusCheck_Only):
                result = {
                'service_validation_result': "The service ("+ str(service_name) +") is configured in automation for status check only",
                'service_validation': service_validation_true,
                'service_validation_type': "status_check",
                'service_Restart_Sleep_Second': 0
                }
            else:
                result = {
                'service_validation_result': "There is no configuration found from Automation for this service("+ str(service_name) +")",
                'service_validation': service_validation_false,
                'service_validation_type': "nothing",
                'service_Restart_Sleep_Second': 0
                }  
        
        else:
            result = {
                'service_validation_result': "There is no data from the Automation service configuration details",
                'service_validation': service_validation_false,
                'service_validation_type': "nothing",
                'service_Restart_Sleep_Second': 0
                }  
        
        
        #for key, value in default.items():
        #    print(key)
        #    print(value)
            
        #result = service_name            
                        
        return result

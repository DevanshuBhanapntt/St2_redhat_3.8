#!/usr/bin/env python
# Copyright 2021 NTTData
# Developed by Arulanantham

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
from lib.base_action import BaseAction
from st2client.models.keyvalue import KeyValuePair  # pylint: disable=no-name-in-module
import ast
import requests
import json


class helixprocessingchangecheck(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(helixprocessingchangecheck, self).__init__(config) 
    def get_token_Helix(self,helix_url, helix_username ,helix_password): 
        
        headers = {'Content-type': 'application/x-www-form-urlencoded' }
        #headers = {'Content-type': 'application/json'}
        data = {"grant_type" : "password",
        "username" : helix_username,
        "password" : helix_password}
        
        endpoint = '/api/jwt/login'
        helix_inc_url = "https://{0}{1}".format(helix_url,endpoint)
        response = requests.post(helix_inc_url, headers=headers, data=data, verify=True)  
        return response.text
    def run(self, inc_st2_key):
    
        helix_username = self.config['helix']['username']
        helix_password = self.config['helix']['password']
        helix_url = self.config['helix']['url']
        
        helix_token =''
        helix_token = self.get_token_Helix(helix_url,helix_username,helix_password)        
            
        st2_client = self.st2_client_get()
        processing_incs = st2_client.keys.get_by_name(inc_st2_key)

        processing_incs = [] if processing_incs is None else ast.literal_eval(processing_incs.value)

        for change_id in processing_incs[:]:
        
            headers = {'Content-type': 'application/json' ,'Authorization': 'AR-JWT '+str(helix_token),'Accept': 'application/json' }
            # define the API for getting all the fields for change
            endpoint = '/api/arsys/v1/entry/CHG:Infrastructure Change Classic?q=%27Infrastructure Change ID%27%3D%22'+change_id+'%22'
            helix_inc_url = "https://{0}{1}".format(helix_url,endpoint)
            response = requests.get(helix_inc_url, headers=headers,verify=True)
            # get the API Response
            data = response.text
            # converting dictionary
            value = json.loads(data)
            
            res_length = 0
            try:
              if not value:
                res_length = 0
              else:
                res_length = 1
                sn_incidents = value["entries"]
              #res_length = len(value["entries"])
            except Exception as e:
                return "arul "+ str(e)
                
            if res_length == 0:
                print('No change found with ID: ' + change_id)
                processing_incs.remove(change_id)
                continue
            
                          
            if (value["entries"][0]["values"]["Change Request Status"] == 'completed' or value["entries"][0]["values"]["Change Request Status"] == 'closed' or value["entries"][0]["values"]["Change Request Status"] == 'cancelled' or value["entries"][0]["values"]["Change Request Status"] == 'rejected' ) :
                print('Removing change: ' + change_id + ' as it is no longer open')
                processing_incs.remove(change_id)

        incs_str = str(processing_incs)
        kvp = KeyValuePair(name=inc_st2_key, value=incs_str)
        st2_client.keys.update(kvp)
        
        # loggout the session
        headers = {"Authorization": helix_token}
        endpoint = '/api/jwt/logout'
        helix_inc_logout = "https://{0}{1}".format(helix_url,endpoint)
        response_logout = requests.post(helix_inc_logout, headers=headers,verify=True)

        return processing_incs

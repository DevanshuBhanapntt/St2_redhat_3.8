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

class itsmchangegetentries(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(itsmchangegetentries, self).__init__(config)
        self.base_action = base_action.BaseAction(config) 
        
    def get_description(self, sn_change):
        
        if sn_change[0]['assignment_group'] and sn_change[0]['assignment_group']['link']:
            response = self.base_action.sn_api_call(method='GET',
                                                    url=sn_change[0]['assignment_group']['link'])
            assign_group_name = response['name']
        else:
            self._logger.info('Assignment Group not found for task: ' + sn_change[0]['number'])
            assign_group_name = ''
                
        if sn_change[0]['assigned_to'] and sn_change[0]['assigned_to']['link']:
            response = self.base_action.sn_api_call(method='GET',
                                                    url=sn_change[0]['assigned_to']['link'])
            assigned_to_name = response['name']
        else:
            self._logger.info('Assignment Group not found for task: ' + sn_change[0]['number'])
            assigned_to_name = ''
        
        if sn_change[0]['company'] and sn_change[0]['company']['link']:
            response = self.base_action.sn_api_call(method='GET',
                                                    url=sn_change[0]['company']['link'])
            company_name = response['name']
        else:
            self._logger.info('Assignment Group not found for task: ' + sn_change[0]['number'])
            company_name = ''
            
        
        
            
        return assign_group_name, assigned_to_name, company_name
        
    def servicenow_get_change_details(self, sn_username, sn_password, sn_url, change_id):
        
        self.st2_fqdn = socket.getfqdn()
        st2_url = "https://{}/".format(self.st2_fqdn)
        self.st2_client = Client(base_url=st2_url)  
        
        #Header details
        servicenow_headers = {'Content-type': 'application/json','Accept': 'application/json'}
        
        # define the conditions
        endpoint = '/api/now/table/change_request?sysparm_query=number='+change_id       
        # define the url & end point details            
        sn_inc_url = "https://{0}{1}".format(sn_url,endpoint)   
        # connect the servicenow            
        sn_result = requests.request('GET',
                                 sn_inc_url,
                                 auth=(sn_username, sn_password),
                                 headers=servicenow_headers)
        # getting the result
        sn_change = sn_result.json()['result'] 
        
        # getting the description and numbers
        assign_group_name,assigned_to_name,company_name = self.get_description(sn_change)
               
        # Adding assign_group_name into api result
        sn_change[0]['assign_group_name'] = assign_group_name
        
        # Adding assigned_to_name into api result
        sn_change[0]['assigned_to_name'] = assigned_to_name
        
        # Adding company_name into api result
        sn_change[0]['company_name'] = company_name
             
         
                                 
        return sn_change 
        
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
        
    def helix_get_change_details(self,helix_url, helix_username ,helix_password,  change_id):
        helix_token =''
        helix_token = self.get_token_Helix(helix_url,helix_username,helix_password)
        if len(helix_token) > 0 :
           headers = {'Content-type': 'application/json' ,'Authorization': 'AR-JWT '+str(helix_token),'Accept': 'application/json' }
           # define the API for getting all the fields for Change
           endpoint = '/api/arsys/v1/entry/CHG:Infrastructure Change Classic?q=%27Infrastructure Change ID%27%3D%22'+change_id+'%22'  
           # define the API for getting only particular fields for Change
           #endpoint += '&fields=values(Infrastructure Change ID,Description,Impact,Company,Support Group Name)'
           
           helix_inc_url = "https://{0}{1}".format(helix_url,endpoint)
           response = requests.get(helix_inc_url, headers=headers,verify=True)
           
           # loggout the session
           headers = {"Authorization": helix_token}
           endpoint = '/api/jwt/logout'
           helix_inc_logout = "https://{0}{1}".format(helix_url,endpoint)
           response_logout = requests.post(helix_inc_logout, headers=headers,verify=True)
           
           # get the API Response
           data = response.text
           # converting dictionary
           value = json.loads(data)
           # return value["entries"][0]["values"]["<<Specifi Field name"]
           #return helix_inc_url
           return value["entries"][0]["values"] 
    
    def run(self, change_id):
    
        itsm_tool = self.config['itsm_tool']
        
        return_value = False
        if itsm_tool == 'servicenow':
            sn_username = self.config['servicenow']['username']
            sn_password = self.config['servicenow']['password']
            sn_url = self.config['servicenow']['url']
            return_value = self.servicenow_get_change_details(sn_username, sn_password, sn_url, change_id)
        elif itsm_tool == 'helix':
            helix_username = self.config['helix']['username']
            helix_password = self.config['helix']['password']
            helix_url = self.config['helix']['url']            
            return_value = self.helix_get_change_details(helix_url,helix_username, helix_password, change_id)
        else:
            error_message = 'Could not get ITSM info please check the config file and try again'
            return_value = (False, {'error_message': error_message})

        return return_value

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

class itsmtaskgetentries(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(itsmtaskgetentries, self).__init__(config)
        self.base_action = base_action.BaseAction(config)  
    def get_description(self, sn_task):
        
        if sn_task[0]['assignment_group'] and sn_task[0]['assignment_group']['link']:
            response = self.base_action.sn_api_call(method='GET',
                                                    url=sn_task[0]['assignment_group']['link'])
            assign_group_name = response['name']
        else:
            self._logger.info('Assignment Group not found for task: ' + sn_task[0]['number'])
            assign_group_name = ''
        
        if sn_task[0]['company'] and sn_task[0]['company']['link']:
            response = self.base_action.sn_api_call(method='GET',
                                                    url=sn_task[0]['company']['link'])
            company_name = response['name']
        else:
            self._logger.info('Assignment Group not found for task: ' + sn_task[0]['number'])
            company_name = ''        
        
        if sn_task[0]['location'] and sn_task[0]['location']['link']:
            try:
                response = self.base_action.sn_api_call(method='GET',
                                                    url=sn_task[0]['location']['link'])
                location_name = response['name']
            except Exception as e:
                logging.exception('Location not found for task: ' + sn_task[0]['number'])
                location_name = ''
        else:
            self._logger.info('Assignment Group not found for task: ' + sn_task[0]['number'])
            location_name = ''
            
        if sn_task[0]['request'] and sn_task[0]['request']['link']:
            response = self.base_action.sn_api_call(method='GET',
                                                    url=sn_task[0]['request']['link'])
            request_number = response['number']
        else:
            self._logger.info('Assignment Group not found for task: ' + sn_task[0]['number'])
            request_number = ''

        if sn_task[0]['request_item'] and sn_task[0]['request_item']['link']:
            response = self.base_action.sn_api_call(method='GET',
                                                    url=sn_task[0]['request_item']['link'])
            request_item_number = response['number']
        else:
            self._logger.info('Assignment Group not found for task: ' + sn_task[0]['number'])
            request_item_number = ''
            
                
        
        return assign_group_name , company_name, location_name,request_number,request_item_number
        
    def servicenow_get_task_details(self, sn_username, sn_password, sn_url, task_id):
        
        self.st2_fqdn = socket.getfqdn()
        st2_url = "https://{}/".format(self.st2_fqdn)
        self.st2_client = Client(base_url=st2_url)  
        
        #Header details
        servicenow_headers = {'Content-type': 'application/json','Accept': 'application/json'}
        
        # define the conditions
        endpoint = '/api/now/table/sc_task?sysparm_query=number='+task_id       
        # define the url & end point details            
        sn_inc_url = "https://{0}{1}".format(sn_url,endpoint)   
        # connect the servicenow            
        sn_result = requests.request('GET',
                                 sn_inc_url,
                                 auth=(sn_username, sn_password),
                                 headers=servicenow_headers)
        # getting the result
        sn_task = sn_result.json()['result'] 
        
        # getting the description and numbers
        assign_group_name, company_name,location_name,request_number,request_item_number = self.get_description(sn_task)
               
        # Adding assign_group_name into api result
        sn_task[0]['assign_group_name'] = assign_group_name
        # Adding company_name into api result
        sn_task[0]['company_name'] = company_name
        # Adding location_name into api result
        sn_task[0]['location_name'] = location_name
        # Adding request_number into api result
        sn_task[0]['request_number'] = request_number
        # Adding request_item_number into api result
        sn_task[0]['request_item_number'] = request_item_number       
         
        return sn_task
        
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
        
    def helix_get_task_details(self,helix_url,helix_username,helix_password,task_id):
        helix_token =''
        helix_token = self.get_token_Helix(helix_url,helix_username,helix_password)         
        if len(helix_token) > 0 : 
           headers = {'Content-type': 'application/json' ,'Authorization': 'AR-JWT '+str(helix_token),'Accept': 'application/json' }
           # define the API for getting all the fields for Workorder details
           endpoint = '/api/arsys/v1/entry/WOI:WorkOrder?q=%27Work%20Order%20ID%27%3D%22'+task_id+'%22'
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
                     
    def run(self, task_id):    
        itsm_tool = self.config['itsm_tool']
        sn_username = self.config['servicenow']['username']
        sn_password = self.config['servicenow']['password']
        sn_url = self.config['servicenow']['url']
        return_value = False
        if itsm_tool == 'servicenow':
            return_value = self.servicenow_get_task_details(sn_username, sn_password, sn_url, task_id)
        elif itsm_tool == 'helix':
            helix_username = self.config['helix']['username']
            helix_password = self.config['helix']['password']
            helix_url = self.config['helix']['url']             
            return_value = self.helix_get_task_details(helix_url,helix_username, helix_password, task_id)
        else:
            error_message = 'Could not get ITSM info please check the config file and try again'
            return_value = (False, {'error_message': error_message})

        return return_value

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

class itsmtaskvariablesgetentries(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(itsmtaskvariablesgetentries, self).__init__(config)
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
            response = self.base_action.sn_api_call(method='GET',
                                                    url=sn_task[0]['location']['link'])
            location_name = response['name']
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
       

        # getting sc_item_option sys id 
        # define the conditions
        endpoint = '/api/now/table/sc_item_option_mtom?sysparm_query=request_item.number='+request_item_number+'&sysparm_fields=sc_item_option'     
        # define the url & end point details            
        sn_inc_url = "https://{0}{1}".format(sn_url,endpoint)   
          
        # connect the servicenow            
        sn_result = requests.request('GET',
                                 sn_inc_url,
                                 auth=(sn_username, sn_password),
                                 headers=servicenow_headers)
        # getting the result
        sn_task_sc_item_option_mtom = sn_result.json()['result'] 
        
        # format the request variable sys id      
        Each_var_sysid_Format = ""
        for var_sysid in sn_task_sc_item_option_mtom:
            if len(Each_var_sysid_Format) > 0:
                Each_var_sysid_Format = Each_var_sysid_Format+"^OR"+"sys_id="+var_sysid['sc_item_option']['value']
            else:
                Each_var_sysid_Format = "sys_id="+ var_sysid['sc_item_option']['value']       
                  
        # getting the variable details
        endpoint = '/api/now/table/sc_item_option?sysparm_query='+Each_var_sysid_Format+'&sysparm_fields=item_option_new%2Cvalue'       
        # define the url & end point details            
        sn_inc_url = "https://{0}{1}".format(sn_url,endpoint)   
          
        # connect the servicenow            
        sn_result = requests.request('GET',
                                 sn_inc_url,
                                 auth=(sn_username, sn_password),
                                 headers=servicenow_headers)
        # getting the result
        sn_task_var_details = sn_result.json()['result'] 
        
        Dict_variables = {}
        
        for var_sysid in sn_task_var_details:        
            endpoint = '/api/now/table/item_option_new/'+var_sysid['item_option_new']['value']
            sn_inc_url = "https://{0}{1}".format(sn_url,endpoint)  
            # connect the servicenow            
            sn_result = requests.request('GET',
                                     sn_inc_url,
                                     auth=(sn_username, sn_password),
                                     headers=servicenow_headers)
            # getting the result
            sn_task_var_details_question = sn_result.json()['result'] 
            Dict_variables[sn_task_var_details_question['question_text']] = var_sysid['value']       
         
        return Dict_variables     
        

    def run(self, task_id):
    
        itsm_tool = self.config['itsm_tool']
        sn_username = self.config['servicenow']['username']
        sn_password = self.config['servicenow']['password']
        sn_url = self.config['servicenow']['url']
        return_value = False
        if itsm_tool == 'servicenow':
            return_value = self.servicenow_get_task_details(sn_username, sn_password, sn_url, task_id)
        elif itsm_tool == 'helix':
            return_value = True
        else:
            error_message = 'Could not get ITSM info please check the config file and try again'
            return_value = (False, {'error_message': error_message})

        return return_value

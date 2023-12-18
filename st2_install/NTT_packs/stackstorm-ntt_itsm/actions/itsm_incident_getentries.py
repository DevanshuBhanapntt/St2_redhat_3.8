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
import requests
import ast
import socket
import os
from st2client.client import Client
import sys
import datetime as dt 
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../actions/lib')
import base_action
import json

class itsmincidentgetentries(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(itsmincidentgetentries, self).__init__(config)
        self.base_action = base_action.BaseAction(config) 
    def get_company_and_ag_and_ciname(self, inc):
        configuration_item_env = ''
        try:
            if inc[0]['assignment_group'] and inc[0]['assignment_group']['link']:                        
              response = self.base_action.sn_api_call(method='GET',
                                                        url=inc[0]['assignment_group']['link'])
              assign_group_name = response['name']                        
            else:              
              assign_group_name = ''
        except Exception as e:              
              assign_group_name = '' 
        try:
            if inc[0]['company'] and inc[0]['company']['link']:
                response = self.base_action.sn_api_call(method='GET',
                                                       url=inc[0]['company']['link'])
                company_name = response['name']
            else:                
                company_name = ''
        except Exception as exCompany:              
              company_name = ''
        
        try:        
            if inc[0]['cmdb_ci'] and inc[0]['cmdb_ci']['link']:
                response = self.base_action.sn_api_call(method='GET',
                                                       url=inc[0]['cmdb_ci']['link'])
                configuration_item_name = response['name']
                configuration_item_env = response['u_environment'].lower()
            else:             
                configuration_item_name = ''
                configuration_item_env = ''
        except Exception as exCompany:              
              configuration_item_name = ''
              configuration_item_env = ''
              
        return assign_group_name, company_name,configuration_item_name,configuration_item_env
        
    def get_details_incident_SOM(self,som_url, som_username ,som_password,som_company_sys_id,  incident_id):
        
        # define the condifion
        # REST API for getting incident details with all fields.        
        sn_inc_endpoint = '/api/now/table/incident?sysparm_query=number='+incident_id
        # Scripted API for getting incident specific fields details(assignment_group,category, cmdb_ci,company,description,
        # impact,number,requested_by,short_description,subcategory,sys_id). if we need more fields contact ServiceNow Team
        #sn_inc_endpoint = '/api/ntt11/incident_automation_stackstorm/GetIncidentData?number='+incident_id
        
        #sn_inc_endpoint = sn_inc_endpoint + '^company.sys_id='+som_company_sys_id
        #sn_inc_endpoint = sn_inc_endpoint + '^descriptionLIKEnot%20responding%20to%20Ping'
        
        # define the which fiels needs to return from SOM API
        #sn_inc_endpoint = sn_inc_endpoint + '&sysparm_fields=number,description' 
        
        sn_inc_url = "https://{0}{1}".format(som_url,
                                             sn_inc_endpoint)
        servicenow_headers = {'Content-type': 'application/json',
                                   'Accept': 'application/json'}
        sn_result = requests.request('GET',
                                     sn_inc_url,
                                     auth=(som_username, som_password),
                                     headers=servicenow_headers)
         
        sn_result.raise_for_status()
        sn_incidents = sn_result.json()['result']         
        assign_group_name, company_name, configuration_item_name,configuration_item_env = self.get_company_and_ag_and_ciname(sn_incidents)
        
        if ((assign_group_name != None) and (len(str(assign_group_name)) > 0)): 
            sn_incidents[0]['assign_group_name'] = assign_group_name
            
        if ((company_name != None) and (len(str(company_name)) > 0)):    
            sn_incidents[0]['company_name'] = company_name
            
        if ((configuration_item_name != None) and (len(str(configuration_item_name)) > 0)):     
            sn_incidents[0]['configuration_item_name'] = configuration_item_name
            
        if ((configuration_item_env != None) and (len(str(configuration_item_env)) > 0)):    
            sn_incidents[0]['configuration_item_env'] = configuration_item_env
           
        for inc in sn_incidents:            
            return inc
            
                
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
        
    def get_details_incident_Helix(self,helix_url, helix_username ,helix_password,  incident_id):
       
        helix_token =''
        helix_token = self.get_token_Helix(helix_url,helix_username,helix_password)
        
        if len(helix_token) > 0 :    

           headers = {'Content-type': 'application/json' ,'Authorization': 'AR-JWT '+str(helix_token),'Accept': 'application/json' }
           # define the API for getting all the fields for incident
           endpoint = '/api/arsys/v1/entry/HPD:IncidentInterface?q=%27Incident+Number%27%3D%22'+incident_id+'%22'  
           # endpoint = '/api/arsys/v1/entry/HPD:IncidentInterface?q=%27Incident+Number%27%3D%22'+incident_id+'%22%20and%20%27Detailed%20Decription%27LIKE%22%25Port%25Down%25%3A%25ifIndex%25%22'            
           # define the API for getting only particular fields for incident
           # endpoint = '/api/arsys/v1/entry/HPD:IncidentInterface?q=%27Incident+Number%27%3D%22'+incident_id+'%22'+'&fields=values(Description,HPD_CI)'
                     
           
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
            
           
    def run(self, incident_id):
    
        itsm_tool = self.config['itsm_tool']
        # itsm_tool = 'servicenow'
        # itsm_tool = 'helix'
        return_value = False
        if itsm_tool == 'servicenow':
            som_username = self.config['servicenow']['username']
            som_password = self.config['servicenow']['password']
            som_url = self.config['servicenow']['url']  
            som_company_sys_id =  self.config['servicenow']['company_sys_id']              
            return_value = self.get_details_incident_SOM(som_url,som_username,som_password,som_company_sys_id,incident_id)
             
        elif itsm_tool == 'helix':
            helix_username = self.config['helix']['username']
            helix_password = self.config['helix']['password']
            helix_url = self.config['helix']['url']        
            return_value = self.get_details_incident_Helix(helix_url,helix_username,helix_password,incident_id)
        else:
            error_message = 'Could not get ITSM info please check the config file and try again'
            return_value = (False, {'error_message': error_message})

        return return_value

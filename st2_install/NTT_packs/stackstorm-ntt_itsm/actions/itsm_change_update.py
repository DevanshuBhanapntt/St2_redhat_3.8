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
import datetime as dt 
import requests
import json
import os

class ITSMChangeUpdate(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(ITSMChangeUpdate, self).__init__(config)

    def servicenow_change_update(self, close, escalate, change_sys_id, notes, implementation_in_progress):
        endpoint = '/api/now/table/change_request/' + change_sys_id
        
        if implementation_in_progress:
            payload = {
                'assigned_to': 'Automation Service',
                'state': '6'
            }
            if notes:
                payload['work_notes'] = notes                       
        else:
            raise Exception("One of close, escalate,pending,priorityupgrade or work_in_progress must be set to True!")

        change = self.sn_api_call('PATCH', endpoint, payload=payload)

        return change
    def helix_setup(self):
        self.helix_username = self.config['helix']['username']
        self.helix_password = self.config['helix']['password']
        self.helix_url = self.config['helix']['url']
        self.helix_Automation_Login_ID = self.config['helix']['Automation_Login_ID']
        self.helix_Automation_Login_Name = self.config['helix']['Automation_Login_Name']
        
    def get_token_Helix(self): 

        headers = {'Content-type': 'application/x-www-form-urlencoded' }      
        data = {"grant_type" : "password",
        "username" : self.helix_username,
        "password" : self.helix_password}
        
        endpoint = '/api/jwt/login'
        helix_inc_url = "https://{0}{1}".format(self.helix_url,endpoint)
        response = requests.post(helix_inc_url, headers=headers, data=data, verify=True)  
        return response.text
        
    def helix_change_update(self, close, escalate, change_sys_id, notes, implementation_in_progress,Actual_Start_Date,Actual_End_Date):
        
        self.helix_setup()
        helix_token =''
        helix_token = self.get_token_Helix()
        endpoint = '/api/arsys/v1/entry/CHG:Infrastructure Change/'+change_sys_id
        headers = {'Authorization': 'AR-JWT '+str(helix_token),'Accept': 'application/json','Content-type': 'application/json'}
        response_update_Change = ''
        response_update_Change_notes =''
        content_notes =''
        content =''
        if len(helix_token) > 0 :
          if implementation_in_progress:
              content = '{  '
              content += '"values": { '               
              content += '"ASCHG" : "'+self.helix_Automation_Login_Name +'",'
              content += '"Change Request Status" : "implementation in progress"'                                           
              content += ' } '
              content += ' } '
          elif close:
              content = '{  '
              content += '"values": { '               
              content += '"Actual Start Date" : "'+Actual_Start_Date +'",'
              content += '"Actual End Date" : "'+Actual_End_Date +'",'
              content += '"Change Request Status" : "completed",'
              content += '"Performance Rating" : "5",'
              content += '"Status Reason" : "successful",' 
              content += '"ASCHG" : "'+self.helix_Automation_Login_Name +'"'
              content += ' } '
              content += ' } '
          if len(notes) > 0: 
            if len(helix_token) > 0 :
               worknotes =[]
               worknotes.append(notes)
               worknotes =str(worknotes)
               endpoint_change_Worknote = '/api/arsys/v1/entry/CHG:WorkLog/'+change_sys_id
               content_notes = '{  '
               content_notes += '"values": { '               
               content_notes += '"Work Log Type" : "general information",'
               content_notes += '"Detailed Description" : "'+worknotes+'",'
               content_notes += '"Description" : "Automation Work Info update"'                                          
               content_notes += ' } '
               content_notes += ' } '
               helix_change_update_notes = "https://{0}{1}".format(self.helix_url,endpoint_change_Worknote)
               response_update_Change_notes = requests.put(helix_change_update_notes, headers=headers, data=content_notes, verify=True)              
          else:
             raise Exception("One of close, escalate,pending,priorityupgrade or work_in_progress must be set to True!")
          
          if len(content) > 0:          
            helix_inc_update = "https://{0}{1}".format(self.helix_url,endpoint)
            response_update_Change = requests.put(helix_inc_update, headers=headers, data=content, verify=True)
        
        
           
        
        # loggout the session
        headers = {"Authorization": helix_token}
        endpoint = '/api/jwt/logout'
        helix_inc_logout = "https://{0}{1}".format(self.helix_url,endpoint)
        response_logout = requests.post(helix_inc_logout, headers=headers,verify=True)
                       
        return {"Response Change Update":response_update_Change,"Change Update":content ,"Response Change Update Notes":response_update_Change_notes,"Change Update Notes":content_notes}
    
    def run(self, close, escalate, change_sys_id, notes, implementation_in_progress,Actual_Start_Date,Actual_End_Date):
        itsm_tool = self.config['itsm_tool']
        return_value = False
        if itsm_tool == 'servicenow':
            return_value = self.servicenow_change_update(close, escalate, change_sys_id, notes, implementation_in_progress)
        elif itsm_tool == 'helix':
            return_value = self.helix_change_update(close,escalate, change_sys_id, notes, implementation_in_progress,Actual_Start_Date,Actual_End_Date)
        else:
            error_message = 'Could not get ITSM info please check the config file and try again'
            return_value = (False, {'error_message': error_message})

        return return_value

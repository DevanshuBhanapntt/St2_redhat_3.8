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
from lib.base_action import BaseAction
import datetime as dt
import requests
import json

class ITSMTaskUpdate(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(ITSMTaskUpdate, self).__init__(config)

    def task_update(self, close,cancel, escalate, task_sys_id, notes, work_in_progress, pending, pending_mins):
        endpoint = '/api/now/table/sc_task/' + task_sys_id

        if work_in_progress:
            payload = {
                'assigned_to': 'Automation Service',                 
                'state': '2'
            }
            if notes:
                payload['work_notes'] = notes
        elif close:
            payload = {                
                'state': '3'
            }
            if notes:
                payload['work_notes'] = notes 
        elif cancel:
            payload = {                
                'state': '4',
                'u_cancel_reason': 'Incorrect Request Information'
            }
            if notes:
                payload['work_notes'] = notes                
        elif escalate:
            payload = {
                'assigned_to': 'NIL ',                 
                'state': '1'
            }
            if notes:
                payload['work_notes'] = notes
        elif pending:
            nowtime = dt.datetime.now() + dt.timedelta(minutes = pending_mins)                                                          
            now_plus_pendingmins = dt.datetime.strftime(nowtime, "%Y-%m-%d %H:%M:%S")         
            payload = {                
                'u_state_reason': 'Awaiting Customer Action',
                'u_pending_end_date_time': now_plus_pendingmins,
                'state': '-5'
            }
            if notes:
                payload['work_notes'] = notes        
        elif len(notes) > 0:
            payload = { 
                'work_notes': notes
            }                
        else:
            raise Exception("One of work_in_progress or close or escalate or pending  must be set to True!")

        inc = self.sn_api_call('PATCH', endpoint, payload=payload)

        return inc
    def helix_setup(self):
        self.helix_username = self.config['helix']['username']
        self.helix_password = self.config['helix']['password']
        self.helix_url = self.config['helix']['url']
        self.helix_Automation_Login_ID = self.config['helix']['Automation_Login_ID']
        self.helix_Automation_Login_Name = self.config['helix']['Automation_Login_Name']
        self.Status_Reason = self.config['helix']['Status_Reason']
        self.Resolution_Category = self.config['helix']['Resolution_Category']
        self.Resolution_Category_Tier_2 = self.config['helix']['Resolution_Category_Tier_2']
        self.Resolution_Category_Tier_3 = self.config['helix']['Resolution_Category_Tier_3']
        self.Resolution_Method = self.config['helix']['Resolution_Method']
        self.Generic_Categorization_Tier_1 = self.config['helix']['Generic_Categorization_Tier_1']
        
    def get_token_Helix(self):
        headers = {'Content-type': 'application/x-www-form-urlencoded' }      
        data = {"grant_type" : "password",
        "username" : self.helix_username,
        "password" : self.helix_password}
        
        endpoint = '/api/jwt/login'
        helix_inc_url = "https://{0}{1}".format(self.helix_url,endpoint)
        response = requests.post(helix_inc_url, headers=headers, data=data, verify=True)  
        return response.text   
        
    def helix_update(self, close,cancel, escalate, task_sys_id, notes, work_in_progress, pending, pending_mins):
        self.helix_setup()
        helix_token =''
        helix_token = self.get_token_Helix()         
        endpoint = '/api/arsys/v1/entry/WOI:WorkOrder/'+task_sys_id
        if len(helix_token) > 0 : 
           headers = {'Authorization': 'AR-JWT '+str(helix_token),'Accept': 'application/json','Content-type': 'application/json'}
           
           if work_in_progress:
             content = '{  '
             content += '"values": { '
             content += '"Assigned To" :  "'+self.helix_Automation_Login_ID+'",'
             content += '"Request Assignee" : "'+self.helix_Automation_Login_Name +'",'
             content += '"Status" : "4"'
             content += ' } '
             content += ' } '
             
           elif close:
             content = '{  '
             content += '"values": { '
             content += '"Assigned To" :  "'+self.helix_Automation_Login_ID+'",'
             content += '"Request Assignee" : "'+self.helix_Automation_Login_Name +'",'
             content += '"Status" : "5"',
             content += '"Status Reason" : "5000"'
             content += ' } '
             content += ' } '
             
           elif escalate:
             content = '{  '
             content += '"values": { '              
             content += '"Request Assignee" :  '',
             content += '"Status" : "1"'              
             content += ' } '
             content += ' } '             
           else:
             raise Exception("One of close, escalate,pending,priorityupgrade or work_in_progress must be set to True!")
           
           
           helix_inc_update = "https://{0}{1}".format(self.helix_url,endpoint)
           response_update = requests.put(helix_inc_update, headers=headers, data=content, verify=True)
             
           # loggout the session
           headers = {"Authorization": helix_token}
           endpoint = '/api/jwt/logout'
           helix_inc_logout = "https://{0}{1}".format(self.helix_url,endpoint)
           response_logout = requests.post(helix_inc_logout, headers=headers,verify=True)
                       
           return {"Response":response_update,"Content":content }  
        
    def run(self,  close,cancel, escalate, task_sys_id, notes, work_in_progress, pending, pending_mins):
        itsm_tool = self.config['itsm_tool']

        return_value = False
        if itsm_tool == 'servicenow':
            return_value = self.task_update( close,cancel, escalate, task_sys_id, notes, work_in_progress, pending, pending_mins)
        elif itsm_tool == 'helix':
            return_value = self.helix_update( close,cancel, escalate, task_sys_id, notes, work_in_progress, pending, pending_mins)
        else:
            error_message = 'Could not get ITSM info please check the config file and try again'
            return_value = (False, {'error_message': error_message})

        return return_value

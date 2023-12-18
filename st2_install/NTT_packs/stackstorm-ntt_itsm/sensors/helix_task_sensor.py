#!/usr/bin/env python
# Copyright 2021 NTT Technologies
# devloped by Arulanantham
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
# https://www.w3schools.com/python/trypython.asp?filename=demo_ref_string_split3
from st2reactor.sensor.base import PollingSensor
from st2client.models.keyvalue import KeyValuePair  # pylint: disable=no-name-in-module
import requests
import ast
import socket
import os
from st2client.client import Client
import sys
import json

__all__ = [
    'helixtasksensor'
]


class helixtasksensor(PollingSensor):
    def __init__(self, sensor_service, config=None, poll_interval=None):
        super(helixtasksensor, self).__init__(sensor_service=sensor_service,
                                                       config=config,
                                                       poll_interval=poll_interval)
        self._logger = self._sensor_service.get_logger(__name__)
         

    def setup(self):
        self.helix_username = self.config['helix']['username']
        self.helix_password = self.config['helix']['password']
        self.helix_url = self.config['helix']['url'] 
        self.Company_name = self.config['helix']['Company_name'] 
        
        self.st2_fqdn = socket.getfqdn()
        st2_url = "https://{}/".format(self.st2_fqdn)
        self.st2_client = Client(base_url=st2_url)
        
    def get_token_Helix(self): 

        headers = {'Content-type': 'application/x-www-form-urlencoded' }      
        data = {"grant_type" : "password",
        "username" : self.helix_username,
        "password" : self.helix_password}
        
        endpoint = '/api/jwt/login'
        helix_inc_url = "https://{0}{1}".format(self.helix_url,endpoint)
        response = requests.post(helix_inc_url, headers=headers, data=data, verify=True)  
        return response.text
        
    def poll(self):
        
        helix_token =''
        helix_token = self.get_token_Helix()
        
        if len(helix_token) > 0 :    
           # = %3D
           # ' %27
           # space %20
           # " %22
           # (  %28
           # , %2C
           # ) %29
           # % %25
           # : %3A
           # ! %21
           # use this URL to encode the details  https://www.w3schools.com/html/html_urlencode.asp
           
           headers = {'Content-type': 'application/json' ,'Authorization': 'AR-JWT '+str(helix_token),'Accept': 'application/json' }
           # define the API for getting all the fields for incident
           endpoint = '/api/arsys/v1/entry/WOI:WorkOrder?'
           # (Status=0 OR Status=1)  0 -->new 1-->assigned
           endpoint = endpoint + 'q=%28Status%3D0%20OR%20Status%3D1%29'                    
           # and Company='xxxxxxx'           
           endpoint = endpoint + '%20and%20Customer%20Company%3D%22'+self.Company_name+'%22' 
           
           # and (
           endpoint = endpoint + '%20AND%28'
                    
                      
           # 'Work Order Type' = "General"
           endpoint = endpoint + '%27Work%20Order%20Type%27%3D%22General%22'
           # AND
           endpoint = endpoint + '%20AND%20'           
           # 'Summary' LIKE "%Monthly Patching - AUTO%" 
           endpoint = endpoint + '%27Summary%27LIKE%22%25Monthly+Patching+-+AUTO%25%22'           
           #  AND 
           endpoint = endpoint + '%20AND%20'  
           
           # 'Summary' !="Validate DNS -NB-AUTO" 
           endpoint = endpoint + '%27Summary%27%21%3D%27%Validate%20DNS%20-NB-AUTO%27'
           #  AND 
           endpoint = endpoint + '%20AND%20'  
           #  'Summary'!="Account Approval - AUTO")
           endpoint = endpoint + '%27Summary%27%21%3D%27%Account%20Approval%20-%20AUTO%27'
           
           # )
           endpoint = endpoint + '%20%29'
           
                  
           # define the API for getting only particular fields for incident
           #endpoint = endpoint + '&fields=values(Entry ID,Company,Incident Number,Description,Detailed Decription,HPD_CI,Assigned Group,Status,Urgency,Impact,Priority)'
           
           helix_inc_url = "https://{0}{1}".format(self.helix_url,endpoint)
           response = requests.get(helix_inc_url, headers=headers,verify=True)
           
           self._logger.info('Helix Processing task url : ' + helix_inc_url)
           
           # loggout the session
           headers = {"Authorization": helix_token}
           endpoint = '/api/jwt/logout'
           helix_inc_logout = "https://{0}{1}".format(self.helix_url,endpoint)
           response_logout = requests.post(helix_inc_logout, headers=headers,verify=True)
           
           # get the API Response
           data = response.text
           # converting dictionary
           value = json.loads(data)
           # return value["entries"][0]["values"]["<<Specifi Field name"]
           res_length = 0
           try:
              if not value:
                res_length = 0
              else:
                res_length = 1
                self.check_tasks(value["entries"])
              #res_length = len(value["entries"])
           except Exception as e:
                return "arul "+ str(e)
           

    def check_tasks(self, sn_incidents):
        ''' Create a trigger to run cleanup on any open incidents that are not being processed
        '''
        inc_st2_key = 'helix.tasks_processing'
        processing_incs = self.st2_client.keys.get_by_name(inc_st2_key)
        processing_incs = [] if processing_incs is None else ast.literal_eval(processing_incs.value)

        for inc in sn_incidents:
            # skip any incidents that are currently being processed
            if inc["values"]["Work Order ID"] in processing_incs:
                # self._logger.info('Already processing INC: ' + inc['number'])
                continue
            else:
                self._logger.info('Helix Processing Task: ' + inc["values"]["Work Order ID"])
                processing_incs.append(inc["values"]["Work Order ID"])
                incs_str = str(processing_incs)
                kvp = KeyValuePair(name=inc_st2_key, value=incs_str)
                self.st2_client.keys.update(kvp)                
                self.check_description(inc)
                
        #for inc in sn_incidents:
        #    self._logger.info('Helix Processing INC: ' + inc["values"]["Incident Number"])
    
        
    def betweenString(self,value, a, b):
        # Find and validate before-part.
        pos_a = value.find(a)
        if pos_a == -1: return ""
        # Find and validate after part.
        pos_b = value.rfind(b)
        if pos_b == -1: return ""
        # Return middle part.
        adjusted_pos_a = pos_a + len(a)
        if adjusted_pos_a >= pos_b: return ""
        return value[adjusted_pos_a:pos_b]
    
    def afterString(self,value, a):
        # Find and validate first part.
        pos_a = value.rfind(a)
        if pos_a == -1: return ""
        # Returns chars after the found string.
        adjusted_pos_a = pos_a + len(a)
        if adjusted_pos_a >= len(value): return ""
        return value[adjusted_pos_a:]
            
    def beforeString(self,value, a):
        # Find first part and return slice before it.
        pos_a = value.find(a)
        if pos_a == -1: return ""
        return value[0:pos_a]
            
    def check_description(self, inc):
        desc = inc["values"]["Detailed Description"].lower()
        desc_org = inc["values"]["Detailed Description"]
        Notification_Test = inc["values"]["Notification_Test"]
        Status = inc["values"]["Status"]        
        company = inc["values"]["Customer Company"]        
        assign_group = inc["values"]["Support Group Name"]
         
        
        self._logger.info('Helix Processing task Det.desc : ' + desc)
        self._logger.info('Helix Processing task Notification_Test : ' + Notification_Test) 
        self._logger.info('Helix Processing task Company : ' + company)        
         
                  
    def cleanup(self):
        pass

    def add_trigger(self, trigger):
        pass

    def update_trigger(self, trigger):
        pass

    def remove_trigger(self, trigger):
        pass

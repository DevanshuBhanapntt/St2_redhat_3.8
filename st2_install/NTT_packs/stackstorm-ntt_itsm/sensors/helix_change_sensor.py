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
    'helixchangesensor'
]


class helixchangesensor(PollingSensor):
    def __init__(self, sensor_service, config=None, poll_interval=None):
        super(helixchangesensor, self).__init__(sensor_service=sensor_service,
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
           endpoint = '/api/arsys/v1/entry/CHG:Infrastructure Change Classic?'
           
           # ('Description' LIKE "%T%R % Automation%]%") 
           # AND ('Change Request Status' = 7) AND ('Vendor Ticket Number' = NULL) 
           # AND (('Scheduled End Date' < $TIME$ + 900) AND ('Scheduled End Date' > $TIME$ - 900)) 
           # AND NOT ('Detailed Description' LIKE "%patchingcheck-auto%")
           
           endpoint = endpoint + 'q='                       
           # and Company='xxxxxxx'           
           endpoint = endpoint + '%20Customer%20Company%3D%22'+self.Company_name+'%22' 
                      
           # AND
           endpoint = endpoint + '%20AND%20'
           # ('Change Request Status' = 7)
           endpoint = endpoint + '%28%27Change+Request+Status%27+%3D+7%29'
           
           # AND
           endpoint = endpoint + '%20AND%20'
           # ('Description' LIKE "%T%R % Automation%]%")
           endpoint = endpoint + '%28%27Description%27+LIKE+%22%25T%25R+%25+Automation%25%5D%25%22%29+'
           
           # AND
           endpoint = endpoint + '%20AND%20'           
           # ('Vendor Ticket Number' = NULL)            
           endpoint = endpoint + '%28%27Vendor+Ticket+Number%27+%3D+NULL%29'
           
           # AND
           endpoint = endpoint + '%20AND%20'           
           # (('Scheduled End Date' < $TIME$ + 900) AND ('Scheduled End Date' > $TIME$ - 900))
           endpoint = endpoint + '%28%28%27Scheduled+End+Date%27+%3C+%24TIME%24+%2B+900%29+AND+%28%27Scheduled+End+Date%27+%3E+%24TIME%24+-+900%29%29'
           
           # AND
           endpoint = endpoint + '%20AND%20' 
           endpoint = endpoint + 'NOT+%28%27Detailed+Description%27+LIKE+%22%25patchingcheck-auto%25%22%29'
                    
                  
           # define the API for getting only particular fields for incident
           #endpoint = endpoint + '&fields=values(Infrastructure Change ID,Description,Impact,Company,Support Group Name)'

           
           helix_change_url = "https://{0}{1}".format(self.helix_url,endpoint)
           response = requests.get(helix_change_url, headers=headers,verify=True)
           
           #self._logger.info('Helix Processing Change url : ' + helix_change_url)
           
           # loggout the session
           headers = {"Authorization": helix_token}
           endpoint = '/api/jwt/logout'
           helix_change_logout = "https://{0}{1}".format(self.helix_url,endpoint)
           response_logout = requests.post(helix_change_logout, headers=headers,verify=True)
           
           # get the API Response
           data = response.text
           # converting dictionary
           value = json.loads(data)
           # return value["entries"][0]["values"]["<<Specifi Field name"]
           res_length = 0
           try:
              if not value:
                res_length = 0
                self._logger.info('There is no changes in Helix as per the Automation filter condition')
              else:
                res_length = 1
                self.check_change(value["entries"])
              #res_length = len(value["entries"])
           except Exception as e:
                return "arul "+ str(e)
           

    def check_change(self, sn_changes):
        ''' Create a trigger to run cleanup on any open incidents that are not being processed
        '''
        inc_st2_key = 'helix.change_processing'
        processing_incs = self.st2_client.keys.get_by_name(inc_st2_key)
        processing_incs = [] if processing_incs is None else ast.literal_eval(processing_incs.value)

        for inc in sn_changes:
            # skip any incidents that are currently being processed
            if inc["values"]["Infrastructure Change ID"] in processing_incs:
                # self._logger.info('Already processing INC: ' + inc['number'])
                continue
            else:
                self._logger.info('Helix Processing Change: ' + inc["values"]["Infrastructure Change ID"])
                processing_incs.append(inc["values"]["Infrastructure Change ID"])
                incs_str = str(processing_incs)
                kvp = KeyValuePair(name=inc_st2_key, value=incs_str)
                self.st2_client.keys.update(kvp)                
                self.check_description(inc)
                
        #for inc in sn_changes:
        #    self._logger.info('Helix Processing Change: ' + inc["values"]["Infrastructure Change ID"])
    
        
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
        notes_desc = inc["values"]["Detailed Description"].lower()
        notes_desc_org = inc["values"]["Detailed Description"]
        summary = inc["values"]["Description"]       
        Status = inc["values"]["Change Request Status"]        
        company = inc["values"]["Customer Company"]        
        assign_group = inc["values"]["Support Group Name"]
         
        
        self._logger.info('Helix Processing Change Det.desc : ' + desc)
        self._logger.info('Helix Processing Change summary : ' + summary) 
        self._logger.info('Helix Processing Change Company : ' + company)        
         
                  
    def cleanup(self):
        pass

    def add_trigger(self, trigger):
        pass

    def update_trigger(self, trigger):
        pass

    def remove_trigger(self, trigger):
        pass

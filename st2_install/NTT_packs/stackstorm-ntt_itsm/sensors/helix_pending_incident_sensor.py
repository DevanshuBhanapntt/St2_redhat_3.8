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
    'helixpendingincidentsensor'
]


class helixpendingincidentsensor(PollingSensor):
    def __init__(self, sensor_service, config=None, poll_interval=None):
        super(helixpendingincidentsensor, self).__init__(sensor_service=sensor_service,
                                                       config=config,
                                                       poll_interval=poll_interval)
        self._logger = self._sensor_service.get_logger(__name__)
         

    def setup(self):
        self.helix_username = self.config['helix']['username']
        self.helix_password = self.config['helix']['password']
        self.helix_url = self.config['helix']['url'] 
        self.Company_name = self.config['helix']['Company_name'] 
        self.helix_Automation_Login_ID = self.config['helix']['Automation_Login_ID']
        self.helix_Automation_Login_Name = self.config['helix']['Automation_Login_Name']
        
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
           # < %3C
           # > %3E
           # use this URL to encode the details  https://www.w3schools.com/html/html_urlencode.asp
           
           headers = {'Content-type': 'application/json' ,'Authorization': 'AR-JWT '+str(helix_token),'Accept': 'application/json' }
           # define the API for getting all the fields for incident
           endpoint = '/api/arsys/v1/entry/HPD:IncidentInterface?'
           # (Status=3 OR Status=1)  3 -->pending
           endpoint = endpoint + 'q=%28Status%3D3%20%29'                     
           # and Company='xxxxxxx'           
           endpoint = endpoint + '%20and%20Company%3D%22'+self.Company_name+'%22' 
            
           
           # and 
           endpoint = endpoint + '%20AND%28'
           # LIKE "%BAO Account%"
           endpoint = endpoint + '%27Assignee%27LIKE%22%25'+self.helix_Automation_Login_Name +'%25%22'
                      
           endpoint = endpoint + '%20AND%20'
           #(('27PendingED__c' < $TIME$ + 900) and ('27PendingED__c' > $TIME$))
           endpoint = endpoint + '%28%28%27PendingED__c%27+%3C+%24TIME%24+%2B+900%29+and+%28%27PendingED__c%27+%3E+%24TIME%24%29%29'
           
           #  OR 
           endpoint = endpoint + '%20OR%20'
           # 'Detailed Description'LIKE"%Memory Usage on%"'
           endpoint = endpoint + '%27Detailed%20Decription%27LIKE%22%25Memory%20Usage%20on%25%22'
           
           #  OR 
           endpoint = endpoint + '%20OR%20'
           # 'Detailed Description'LIKE"%Memory Used on%"'
           endpoint = endpoint + '%27Detailed%20Decription%27LIKE%22%25Memory%20Used%20on%25%22'
           
           
           # )
           endpoint = endpoint + '%20%29'
                  
           # define the API for getting only particular fields for incident
           endpoint = endpoint + '&fields=values(Entry ID,Company,Incident Number,Description,Detailed Decription,HPD_CI,Assigned Group,Status,Urgency,Impact,Priority,PendingSD__c,PendingED__c)'
           
           helix_inc_url = "https://{0}{1}".format(self.helix_url,endpoint)
           response = requests.get(helix_inc_url, headers=headers,verify=True)
           
           self._logger.info('Helix Processing url : ' + helix_inc_url)
           
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
                   
           #if value["entries"]:
           self.check_incidents(value["entries"])

    def check_incidents(self, sn_incidents):
        ''' Create a trigger to run cleanup on any open incidents that are not being processed
        '''
        inc_st2_key = 'helix.Pending_incidents_processing' 
        processing_incs = self.st2_client.keys.get_by_name(inc_st2_key)
        processing_incs = [] if processing_incs is None else ast.literal_eval(processing_incs.value)

        for inc in sn_incidents:
            # skip any incidents that are currently being processed
            if inc["values"]["Incident Number"] in processing_incs:
                # self._logger.info('Already processing INC: ' + inc['number'])
                continue
            else:
                self._logger.info('Helix Processing INC: ' + inc["values"]["Incident Number"])
                processing_incs.append(inc["values"]["Incident Number"])
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
        desc = inc["values"]["Detailed Decription"].lower()
        desc_org = inc["values"]["Detailed Decription"]
        short_desc = inc["values"]["Description"]
        company = inc["values"]["Company"]
        assign_group = inc["values"]["Assigned Group"]
        configuration_item_name = inc["values"]["HPD_CI"]
        incident_state = '2'
        if ('Pending' in inc["values"]["Status"]):
          incident_state = '-5'
        else:
          incident_state = '2'
        
        #self._logger.info('Helix Processing INC Det.desc : ' + desc)
        #self._logger.info('Helix Processing INC short.desc : ' + short_desc) 
        #self._logger.info('Helix Processing INC Company : ' + company)        
         
        
        if (('memory usage on' in desc or 'memory used on' in desc) and ('intel' in assign_group.lower() or 'wintel' in assign_group.lower())):
            
            #ci_address_begin = desc.split('memory usage on ')[-1]
            #ci_address = ci_address_begin.split(' ')[0]
            ci_address = ''
            rec_short_desc = ''
            rec_detailed_desc = ''
            
            if ', th is' in desc:
                threshold_begin = desc.split(', th is ')[-1]
                threshold = threshold_begin.split('%')[0]
            else:
                threshold = None
                
            if 'memory usage on' in desc:
                rec_short_desc = 'memory%20usage%20on'
                rec_detailed_desc = 'memory%20usage%20on'
                ci_address_begin = desc.split('memory usage on ')[-1]
                ci_address = ci_address_begin.split(' ')[0]                
            elif 'memory used on' in desc: 
                rec_short_desc = 'memory%20used%20on'
                rec_detailed_desc = 'memory%20used%20on'
                ci_address_begin = desc.split('memory used on ')[-1]
                ci_address = ci_address_begin.split(' ')[0]  
            
            
            if 'physical memory' in desc:
                memory_type = 'Physical'
            elif 'virtual' in desc:
                memory_type = 'Virtual'
            elif ('physical' in desc or 'windows | memory usage |' in desc or  'memory utilization' in desc or 'memory usage on' in desc ):
                memory_type = 'Physical'
            elif ('high memory paging' in desc or 'paging is now' in desc):
               memory_type = 'PagesPerSec'
            elif ('paging file usage' in desc):
               memory_type = 'PagingFile'
            elif ('threshold of memory not met' in desc):
               memory_type = 'MemoryAvailableBytes'
            elif ('memory low:' in desc):
               memory_type = 'MemoryUsedBytesPct'
            else:
               memory_type = 'Physical'
            #cmdb_ci.name
            payload = {
                'assignment_group': assign_group,
                'ci_address': ci_address,
                'customer_name': company,
                'detailed_desc': desc_org,
                'inc_number': inc["values"]['Incident Number'],
                'inc_sys_id': inc["values"]['Entry ID'],
                'os_type': 'windows',
                'short_desc': short_desc,
                'threshold_percent': threshold,
                'incident_state': incident_state,
                'rec_short_desc': rec_short_desc,
                'rec_detailed_desc': rec_detailed_desc,
                'configuration_item_name': configuration_item_name,
                'memory_type':memory_type
            }
            self._sensor_service.dispatch(trigger='ntt_itsm.win_memory_high', payload=payload)           
                  
    def cleanup(self):
        pass

    def add_trigger(self, trigger):
        pass

    def update_trigger(self, trigger):
        pass

    def remove_trigger(self, trigger):
        pass

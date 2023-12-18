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
    'helixincidentsensor'
]


class helixincidentsensor(PollingSensor):
    def __init__(self, sensor_service, config=None, poll_interval=None):
        super(helixincidentsensor, self).__init__(sensor_service=sensor_service,
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
           # use this URL to encode the details  https://www.w3schools.com/html/html_urlencode.asp
           
           headers = {'Content-type': 'application/json' ,'Authorization': 'AR-JWT '+str(helix_token),'Accept': 'application/json' }
           # define the API for getting all the fields for incident
           endpoint = '/api/arsys/v1/entry/HPD:IncidentInterface?'
           # (Status=0 OR Status=1)  0 -->new 1-->assigned
           endpoint = endpoint + 'q=%28Status%3D0%20OR%20Status%3D1%29'
           # ('Priority'="Medium" OR 'Priority'="Low")          
           endpoint = endpoint + '%20and%20%28%27Priority%27%3D%22Medium%22%20OR%20%27Priority%27%3D%22Low%22%29'           
           # and Company='xxxxxxx'           
           endpoint = endpoint + '%20and%20Company%3D%22'+self.Company_name+'%22' 
           
           # and (
           endpoint = endpoint + '%20AND%28'
           
           # 'Detailed Description'LIKE"%Port%Down%:%ifIndex=%"'
           #endpoint = endpoint + '%20and%20%27Detailed%20Decription%27LIKE%22%25Port%25Down%25%3A%25ifIndex%25%22'
           
           # 'Detailed Description'LIKE"%System Up Time"'
           endpoint = endpoint + '%27Detailed%20Decription%27LIKE%22%25System%20Up%20Time%25%22'
           #  OR 
           endpoint = endpoint + '%20OR%20'           
           # 'Detailed Description'LIKE"%is not responding to Ping"'
           endpoint = endpoint + '%27Detailed%20Decription%27LIKE%22%25is%20not%20responding%20to%20Ping%25%22'           
           #  OR 
           endpoint = endpoint + '%20OR%20'           
           # 'Detailed Description'LIKE"%CPU Utilization on%"'
           endpoint = endpoint + '%27Detailed%20Decription%27LIKE%22%25CPU%20Utilization%20on%25%22'
           #  OR 
           endpoint = endpoint + '%20OR%20'  
           # 'Detailed Description'LIKE"%C:%Logical Disk Free Space%"'
           endpoint = endpoint + '%27Detailed%20Decription%27LIKE%22%25C%3A%25Logical%20Disk%20Free%20Space%25%22'
           
           #  OR 
           endpoint = endpoint + '%20OR%20'
           # 'Detailed Description'LIKE"%Memory Usage on%"'
           endpoint = endpoint + '%27Detailed%20Decription%27LIKE%22%25Memory%20Usage%20on%25%22'
           
           #  OR 
           endpoint = endpoint + '%20OR%20'
           # 'Detailed Description'LIKE"%Memory Used on%"'
           endpoint = endpoint + '%27Detailed%20Decription%27LIKE%22%25Memory%20Used%20on%25%22'
           
           #  OR 
           endpoint = endpoint + '%20OR%20'
           # 'Detailed Description'LIKE"%Windows Service%is not running on host%"'
           endpoint = endpoint + '%27Detailed%20Decription%27LIKE%22%25Windows%20Service%25is%20not%20running%20on%20host%25%22'
           # )
           endpoint = endpoint + '%20%29'
           
                  
           # define the API for getting only particular fields for incident
           endpoint = endpoint + '&fields=values(Entry ID,Company,Incident Number,Description,Detailed Decription,HPD_CI,Assigned Group,Status,Urgency,Impact,Priority)'
           
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
           
           self.check_incidents(value["entries"])

    def check_incidents(self, sn_incidents):
        ''' Create a trigger to run cleanup on any open incidents that are not being processed
        '''
        inc_st2_key = 'helix.incidents_processing'
        processing_incs = self.st2_client.keys.get_by_name(inc_st2_key)
        processing_incs = [] if processing_incs is None else ast.literal_eval(processing_incs.value)

        for inc in sn_incidents:
            # skip any incidents that are currently being processed
            if inc["values"]["Incident Number"] in processing_incs:
                # self._logger.info('Already processing INC: ' + inc['number'])
                continue
            else:
                insert_output = self.check_description(inc)
                if insert_output == "true":
                    processing_incs.append(inc["values"]["Incident Number"])
                    incs_str = str(processing_incs)
                    kvp = KeyValuePair(name=inc_st2_key, value=incs_str)
                    self.st2_client.keys.update(kvp)
                    self._logger.info('Helix Processing INC: ' + inc["values"]["Incident Number"])
                else:
                    continue
                
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
        insertto_datastore = 'false'
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
         
        if ('is not responding to ping' in desc or 'system up time' in desc ):
            insertto_datastore = 'true'
            if assign_group == '':
                check_uptime = False
                os_type = ''
            else:
                check_uptime = True
                os_type = 'windows' if 'intel' in assign_group.lower() else 'linux'
            
            if ('TrueSIght' in desc_org):
               ci_address_end = self.afterString(desc_org,"TrueSIght")  
               ci_address = ci_address_end.split(' ')[1]               
            else:
               ci_address = desc.split(' ')[0]               
            
            ci_address = ci_address.strip()
            payload = {
                'assignment_group': assign_group,
                'check_uptime': check_uptime,
                'ci_address': ci_address,
                'customer_name': company,
                'detailed_desc': desc_org,
                'inc_number': inc["values"]['Incident Number'],
                'inc_sys_id': inc["values"]['Entry ID'],
                'os_type': os_type,
                'short_desc': short_desc
            }
            self._sensor_service.dispatch(trigger='ntt_itsm.unreachable_ping', payload=payload)
            
        elif (('cpu utilization on' in desc) and ('intel' in assign_group.lower() or 'wintel' in assign_group.lower())):
            #assign_group, company = self.get_company_and_ag(inc)
            insertto_datastore = 'true'
            ci_address_begin = desc_org.split('cpu utilization on ')[-1]
            ci_address = ci_address_begin.split(' ')[0]
            if ', th is' in desc:
                threshold_begin = desc.split(', th is ')[-1]
                threshold = threshold_begin.split('%')[0]
            else:
                threshold = None

            payload = {
                'assignment_group': assign_group,
                'ci_address': ci_address,
                'cpu_name': '_total',
                'cpu_type': 'ProcessorTotalProcessorTime',
                'customer_name': company,
                'detailed_desc': desc_org,
                'inc_number': inc["values"]['Incident Number'],
                'inc_sys_id': inc["values"]['Entry ID'],
                'os_type': 'windows',
                'short_desc': short_desc,
                'threshold_percent': threshold
            }
            self._sensor_service.dispatch(trigger='ntt_itsm.high_cpu', payload=payload)
        elif (('memory usage on' in desc or 'memory used on' in desc) and ('linux' in assign_group.lower() or 'unix' in assign_group.lower())):
            #assign_group, company = self.get_company_and_ag(inc)
            insertto_datastore = 'true'
            if 'memory usage on' in desc:
                ci_address_begin = desc.split('memory usage on ')[-1]
            else:
                ci_address_begin = desc.split('memory used on ')[-1]
            ci_address = ci_address_begin.split(' ')[0]
            if ', th is' in desc:
                threshold_begin = desc.split(', th is ')[-1]
                threshold = threshold_begin.split('%')[0]
            else:
                threshold = None
            payload = {
                'assignment_group': assign_group,
                'ci_address': ci_address,
                'customer_name': company,
                'detailed_desc': desc_org,
                'inc_number': inc["values"]['Incident Number'],
                'inc_sys_id': inc["values"]['Entry ID'],
                'memory_threshold': threshold,
                'os_type': 'linux',
                'short_desc': short_desc
            }
            self._sensor_service.dispatch(trigger='ntt_itsm.high_memory', payload=payload)
        elif 'logical disk free space on' in desc:
            #assign_group, company = self.get_company_and_ag(inc)
            insertto_datastore = 'true'
            ci_address_begin = desc.split('logical disk free space on ')[-1]
            ci_address = ci_address_begin.split(' ')[0]
            disk_name_end = inc["values"]["Detailed Decription"].split(':')[0]
            disk_name = disk_name_end.split(' ')[-1]
            if ', th is' in desc:
                threshold_begin = desc.split(', th is ')[-1]
                threshold = threshold_begin.split('%')[0]
            else:
                threshold = None
            payload = {
                'assignment_group': assign_group,
                'ci_address': ci_address,
                'customer_name': company,
                'detailed_desc': desc_org,
                'disk_name': disk_name,
                'inc_number': inc["values"]['Incident Number'],
                'inc_sys_id': inc["values"]['Entry ID'],
                'os_type': 'windows',
                'short_desc': short_desc,
                'threshold_percent': threshold
            }
            self._sensor_service.dispatch(trigger='ntt_itsm.high_disk', payload=payload)
        elif (('memory usage on' in desc or 'memory used on' in desc) and ('intel' in assign_group.lower() or 'wintel' in assign_group.lower())):
            insertto_datastore = 'true'
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
            
        elif (('Windows Service' in short_desc and 'is not running' in short_desc) or ('Service Alert:' in short_desc and 'has changed to Stopped state' in short_desc)):
            insertto_datastore = 'true'
            ci_address = ''
            rec_short_desc = ''
            rec_detailed_desc = ''
            service_name = ''
            
            if ('TrueSight' in short_desc and 'Windows Service' in short_desc and 'is not running on host'in short_desc ):
               ci_address_begin = short_desc.split('TrueSight ')[-1]  
               ci_address = ci_address_begin.split(' ')[0] 
               
               Find_After = self.afterString(short_desc, "Windows Service")
               Find_After = Find_After.strip()
               Find_Before = self.beforeString(Find_After,'is not running on host')
               Find_Before =Find_Before.strip()
               rec_short_desc = 'Windows%20Service'
               rec_detailed_desc = Find_Before
               service_name  = Find_Before               
            elif ('Windows Service' in short_desc and 'is not running on host'in short_desc ):
               ci_address = short_desc.split(' ')[0]               
               Find_After = self.afterString(short_desc, "Windows Service")
               Find_After = Find_After.strip()
               Find_Before = self.beforeString(Find_After,'is not running on host')
               Find_Before =Find_Before.strip()
               rec_short_desc = 'Windows%20Service'
               rec_detailed_desc = service_name 
               service_name  = Find_Before
            elif ('Windows Service' in short_desc and 'on host' in short_desc and 'is not running'in short_desc ):
               ci_address = short_desc.split(' ')[0]
               Find_After = self.afterString(short_desc, "Windows Service")
               Find_After = Find_After.strip()
               Find_Before = self.beforeString(Find_After,'on host') 
               Find_Before =Find_Before.strip()               
               service_name  = Find_Before 
               rec_short_desc = 'Windows%20Service'
               rec_detailed_desc = Find_Before
            elif ('Service Alert:' in short_desc and 'has changed to Stopped state' in short_desc  ):
               ci_address = short_desc.split(':')[0]
               Find_After = self.afterString(short_desc, "Service Alert:")
               Find_After = Find_After.strip()
               Find_Before = self.beforeString(Find_After,'has changed to Stopped state')
               Find_Before =Find_Before.strip()               
               service_name = short_desc.split(' ')[2]
               rec_short_desc = 'Service%20Alert%3A'
               rec_detailed_desc = service_name
            
            
            payload = {
                'assignment_group': assign_group,
                'ci_address': ci_address,
                'customer_name': company,
                'detailed_desc': desc_org,
                'inc_number': inc["values"]['Incident Number'],
                'inc_sys_id': inc["values"]['Entry ID'],                
                'short_desc': short_desc,
                'incident_state': incident_state,
                'service_name': service_name,
                'rec_short_desc': rec_short_desc,
                'rec_detailed_desc': rec_detailed_desc,
                'configuration_item_name': configuration_item_name 
            }
            self._sensor_service.dispatch(trigger='ntt_itsm.win_service_check', payload=payload)  
        return insertto_datastore
                 
    def cleanup(self):
        pass

    def add_trigger(self, trigger):
        pass

    def update_trigger(self, trigger):
        pass

    def remove_trigger(self, trigger):
        pass

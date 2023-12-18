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
from st2reactor.sensor.base import PollingSensor
from st2client.models.keyvalue import KeyValuePair  # pylint: disable=no-name-in-module
import requests
import ast
import socket
import os
from st2client.client import Client
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../actions/lib')
import base_action

__all__ = [
    'servicenowpendingtasksensor'
]


class servicenowpendingtasksensor(PollingSensor):
    def __init__(self, sensor_service, config=None, poll_interval=None):
        super(servicenowpendingtasksensor, self).__init__(sensor_service=sensor_service,
                                                       config=config,
                                                       poll_interval=poll_interval)
        self._logger = self._sensor_service.get_logger(__name__)
        self.base_action = base_action.BaseAction(config)

    def setup(self):
        self.sn_username = self._config['servicenow']['username']
        self.sn_password = self._config['servicenow']['password']
        self.sn_url = self._config['servicenow']['url']
        self.servicenow_headers = {'Content-type': 'application/json',
                                   'Accept': 'application/json'}
        self.st2_fqdn = socket.getfqdn()
        st2_url = "https://{}/".format(self.st2_fqdn)
        self.st2_client = Client(base_url=st2_url)

    def poll(self):
               
        sn_task_endpoint = '/api/now/table/sc_task?sysparm_query=active=true^assigned_to.name=Automation Service^state=-5' \
            '^u_pending_end_date_time<javascript:gs.minutesAgoStart(-15)' \
            '^u_state_reason=106' \
            '^ORu_state_reason=100' \
            '^ORshort_descriptionENDSWITHAUTO' \
            '^ORshort_descriptionSTARTSWITHRemove%20Decommissioned%20Server' \
            '^ORshort_descriptionLIKESOM%20-%20Disable%20Linux%20Account' \
            '^ORshort_descriptionSTARTSWITHValidate%20CMA%20Console' \
            '^ORrequest_item.cat_item.nameINMessaging,Global%20Enterprise%20Server%20Provisioning,InfoSec%20-%20Termination,Bulk%20Add%20/%20Change%20/%20Terminate%20User,Enterprise%20Server%20Provisioning%20-%20Leveraged,Enterprise%20Server%20Decommissioning%20-%20Leveraged,Server%20Decommissioning,Virtual%20Server%20Provisioning' \
            '^ORrequest_item.cat_item.nameENDSWITHWFAUTO' \
            '^ORdescriptionINDatabase%20Security%20Request,Term-Remove%20Palo%20Alto%20Account'             
        
        sn_task_url = "https://{0}{1}".format(self.sn_url,
                                             sn_task_endpoint)

        sn_result = requests.request('GET',
                                     sn_task_url,
                                     auth=(self.sn_username, self.sn_password),
                                     headers=self.servicenow_headers)

        sn_result.raise_for_status()
        sn_taks = sn_result.json()['result']
        self.check_tasks(sn_taks)

    def check_tasks(self, sn_taks):
        ''' Create a trigger to run cleanup on any open incidents that are not being processed
        '''
        inc_st2_key = 'servicenow.Pending_tasks_processing'
        processing_tsks = self.st2_client.keys.get_by_name(inc_st2_key)

        processing_tsks = [] if processing_tsks is None else ast.literal_eval(processing_tsks.value)

        for tsk in sn_taks:
            # skip any taks that are currently being processed
            if tsk['number'] in processing_tsks:
                # self._logger.info('Already processing taks: ' + tsk['number'])
                continue
            else:
                self._logger.info('Processing pending tasks: ' + tsk['number'])
                processing_tsks.append(tsk['number'])
                incs_str = str(processing_tsks)
                kvp = KeyValuePair(name=inc_st2_key, value=incs_str)
                self.st2_client.keys.update(kvp)                
                self.check_description(tsk)

    def get_description(self, tsk):
        
        if tsk['assignment_group'] and tsk['assignment_group']['link']:
            response = self.base_action.sn_api_call(method='GET',
                                                    url=tsk['assignment_group']['link'])
            assign_group_name = response['name']
        else:
            self._logger.info('Assignment Group not found for task: ' + tsk['number'])
            assign_group_name = ''
        
        if tsk['company'] and tsk['company']['link']:
            response = self.base_action.sn_api_call(method='GET',
                                                    url=tsk['company']['link'])
            company_name = response['name']
        else:
            self._logger.info('Assignment Group not found for task: ' + tsk['number'])
            company_name = ''        
        
        if tsk['location'] and tsk['location']['link']:
            response = self.base_action.sn_api_call(method='GET',
                                                    url=tsk['location']['link'])
            location_name = response['name']
        else:
            self._logger.info('Assignment Group not found for task: ' + tsk['number'])
            location_name = ''
            
        if tsk['request'] and tsk['request']['link']:
            response = self.base_action.sn_api_call(method='GET',
                                                    url=tsk['request']['link'])
            request_number = response['number']
        else:
            self._logger.info('Assignment Group not found for task: ' + tsk['number'])
            request_number = ''

        if tsk['request_item'] and tsk['request_item']['link']:
            response = self.base_action.sn_api_call(method='GET',
                                                    url=tsk['request_item']['link'])
            request_item_number = response['number']
        else:
            self._logger.info('Assignment Group not found for task: ' + tsk['number'])
            request_item_number = ''
            
        return assign_group_name, company_name, location_name, request_number, request_item_number
          
        
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
            
    def check_description(self, tsk):
    
        desc = tsk['description']      
        
        # getting the description and numbers
        assign_group_name, company_name,location_name,request_number,request_item_number = self.get_description(tsk)         
               
        #if 'Term-Remove Palo Alto Account' in desc:
            
            # refer the sample trigger dispatch
            #payload = {
            #    'assign_group_name': assign_group_name,             
            #    'company_name': company_name,
            #    'detailed_desc': inc['description'],
            #    'inc_number': tsk['number'],
            #    'inc_sys_id': tsk['sys_id']            
            #}
            #self._sensor_service.dispatch(trigger='ntt_itsm.unreachable_ping', payload=payload)
       
    def cleanup(self):
        pass

    def add_trigger(self, trigger):
        pass

    def update_trigger(self, trigger):
        pass

    def remove_trigger(self, trigger):
        pass

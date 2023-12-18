#!/usr/bin/env python
# Copyright 2021 Encore Technologies
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
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../actions/lib')
import base_action

__all__ = [
    'ServiceNowIncidentSensor'
]


class ServiceNowIncidentSensor(PollingSensor):
    def __init__(self, sensor_service, config=None, poll_interval=None):
        super(ServiceNowIncidentSensor, self).__init__(sensor_service=sensor_service,
                                                       config=config,
                                                       poll_interval=poll_interval)
        self._logger = self._sensor_service.get_logger(__name__)
        self.base_action = base_action.BaseAction(config)

    def setup(self):
        self.sn_username = self._config['servicenow']['username']
        self.sn_password = self._config['servicenow']['password']
        self.sn_url = self._config['servicenow']['url']
        self.som_company_sys_id =  self.config['servicenow']['company_sys_id']
        self.servicenow_headers = {'Content-type': 'application/json',
                                   'Accept': 'application/json'}
        self.st2_fqdn = socket.getfqdn()
        st2_url = "https://{}/".format(self.st2_fqdn)
        self.st2_client = Client(base_url=st2_url)

    def poll(self):
        # Query for all active and open incidents               
        sn_inc_endpoint = '/api/now/table/incident?sysparm_query=active=true^incident_state=2'
        sn_inc_endpoint = sn_inc_endpoint + '^company.sys_id='+self.som_company_sys_id
        sn_inc_endpoint = sn_inc_endpoint + '^priority=3^ORpriority=4'
        sn_inc_endpoint = sn_inc_endpoint + '^sys_created_on>=javascript:gs.beginningOfYesterday()'
        # Host down
        sn_inc_endpoint = sn_inc_endpoint + '^descriptionLIKEnot%20responding%20to%20Ping'
        # Windows CPU Utilization
        sn_inc_endpoint = sn_inc_endpoint + '^ORdescriptionLIKEcpu%20utilization%20on'
        # Memory Utilization
        sn_inc_endpoint = sn_inc_endpoint + '^ORdescriptionLIKEmemory%20usage%20on'        
        sn_inc_endpoint = sn_inc_endpoint + '^ORdescriptionLIKEmemory%20used%20on'
        # Windows Disk usage
        sn_inc_endpoint = sn_inc_endpoint + '^ORdescriptionLIKElogical%20disk%20free%20space%20on'
        sn_inc_endpoint = sn_inc_endpoint + '^ORdescriptionLIKE%20MONITORING%20%20Disk'
        # Windows CPU Performance Queue length
        sn_inc_endpoint = sn_inc_endpoint + '^ORdescriptionLIKESystem%20Performance%20Processor%20Queue%20Length'
        # Linux Process
        sn_inc_endpoint = sn_inc_endpoint + '^ORdescriptionLIKELinux%20process'
        # Windows Hearbeat
        sn_inc_endpoint = sn_inc_endpoint + '^ORdescriptionLIKEOpsRamp%20Agent%20service%20is%20offline'       
        # Windows Service alert
        sn_inc_endpoint = sn_inc_endpoint + '^ORshort_descriptionLIKEWindows%20Service'
        sn_inc_endpoint = sn_inc_endpoint + '^ORshort_descriptionLIKEService%20Alert:'
        # Network Unreachable to ping
        sn_inc_endpoint = sn_inc_endpoint + '^ORdescriptionLIKENetwork%20Outage'
        sn_inc_endpoint = sn_inc_endpoint + '^ORdescriptionLIKEDevice%20Reboot%20Detected'
        # SNMP Agent Not Responding
        sn_inc_endpoint = sn_inc_endpoint + '^ORdescriptionLIKESNMP%20Agent%20Not%20Responding'
        #Wireless accesspoint alarm
        sn_inc_endpoint = sn_inc_endpoint + '^ORdescriptionLIKEAP%20Antenna%20Offline'
        
        # define the which fiels needs to return from SOM API
        sn_inc_endpoint = sn_inc_endpoint + '&sysparm_fields=number,assignment_group,company,cmdb_ci,description,short_description,sys_id,priority,incident_state,opened_at'
        
        sn_inc_url = "https://{0}{1}".format(self.sn_url,
                                             sn_inc_endpoint)

        sn_result = requests.request('GET',
                                     sn_inc_url,
                                     auth=(self.sn_username, self.sn_password),
                                     headers=self.servicenow_headers)

        sn_result.raise_for_status()
        sn_incidents = sn_result.json()['result']
        self.check_incidents(sn_incidents)

    def check_incidents(self, sn_incidents):
        ''' Create a trigger to run cleanup on any open incidents that are not being processed
        '''
        inc_st2_key = 'servicenow.incidents_processing'
        processing_incs = self.st2_client.keys.get_by_name(inc_st2_key)

        processing_incs = [] if processing_incs is None else ast.literal_eval(processing_incs.value)

        for inc in sn_incidents:
            # skip any incidents that are currently being processed
            if inc['number'] in processing_incs:
                # self._logger.info('Already processing INC: ' + inc['number'])
                continue
            else:
                insert_output = self.check_description(inc)
                if insert_output == "true":
                    self._logger.info('Processing INC: ' + inc['number'])
                    processing_incs.append(inc['number'])
                    incs_str = str(processing_incs)
                    kvp = KeyValuePair(name=inc_st2_key, value=incs_str)
                    self.st2_client.keys.update(kvp)
                else:
                    continue

    def get_company_and_ag_and_ciname(self, inc):
        configuration_item_env = ''
        if inc['assignment_group'] and inc['assignment_group']['link']:
            response = self.base_action.sn_api_call(method='GET',
                                                    url=inc['assignment_group']['link'])
            assign_group = response['name']
        else:
            self._logger.info('Assignment Group not found for INC: ' + inc['number'])
            assign_group = ''

        if inc['company'] and inc['company']['link']:
            response = self.base_action.sn_api_call(method='GET',
                                                   url=inc['company']['link'])
            company = response['name']
        else:
            self._logger.info('Company not found for INC: ' + inc['number'])
            company = ''
        
        if inc['cmdb_ci'] and inc['cmdb_ci']['link']:
            response = self.base_action.sn_api_call(method='GET',
                                                   url=inc['cmdb_ci']['link'])
            configuration_item_name = response['name']
            configuration_item_env = response['u_environment'].lower()
        else:
            self._logger.info('Company not found for INC: ' + inc['number'])
            configuration_item_name = ''

        return assign_group, company,configuration_item_name,configuration_item_env
    
        
        
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
        desc = inc['description'].lower()
        short_desc = inc['short_description']
        
        
        
        assign_group, company, configuration_item_name,configuration_item_env = self.get_company_and_ag_and_ciname(inc)
         
        if 'is not responding to ping' in desc:
            #assign_group, company = self.get_company_and_ag_and_ciname(inc)
            insertto_datastore = "true"
            if assign_group == '':
                check_uptime = False
                os_type = ''
            else:
                check_uptime = True
                os_type = 'windows' if 'intel' in assign_group.lower() else 'linux'

            ci_address_end = desc.split(' is not responding to ping')[0]
            ci_address = ci_address_end.split(' ')[-1]
            payload = {
                'assignment_group': assign_group,
                'check_uptime': check_uptime,
                'ci_address': ci_address,
                'customer_name': company,
                'detailed_desc': inc['description'],
                'inc_number': inc['number'],
                'inc_sys_id': inc['sys_id'],
                'os_type': os_type,
                'short_desc': inc['short_description']
            }
            self._sensor_service.dispatch(trigger='ntt_itsm.unreachable_ping', payload=payload)
        elif (('cpu utilization on' in desc) and ('intel' in assign_group.lower() or 'wintel' in assign_group.lower())):
            #assign_group, company = self.get_company_and_ag(inc)
            insertto_datastore = "true"
            ci_address_begin = desc.split('cpu utilization on ')[-1]
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
                'detailed_desc': inc['description'],
                'inc_number': inc['number'],
                'inc_sys_id': inc['sys_id'],
                'os_type': 'windows',
                'short_desc': inc['short_description'],
                'threshold_percent': threshold
            }
            self._sensor_service.dispatch(trigger='ntt_itsm.high_cpu', payload=payload)
        #elif 'memory usage on' in desc or 'memory used on' in desc:
        elif (('memory usage on' in desc or 'memory used on' in desc) and ('linux' in assign_group.lower() or 'unix' in assign_group.lower())):
            #assign_group, company = self.get_company_and_ag(inc)
            insertto_datastore = "true"
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
                'detailed_desc': inc['description'],
                'inc_number': inc['number'],
                'inc_sys_id': inc['sys_id'],
                'memory_threshold': threshold,
                'os_type': 'linux',
                'short_desc': inc['short_description']
            }
            self._sensor_service.dispatch(trigger='ntt_itsm.high_memory', payload=payload)
        elif 'logical disk free space on' in desc:
            #assign_group, company = self.get_company_and_ag(inc)
            insertto_datastore = "true"
            ci_address_begin = desc.split('logical disk free space on ')[-1]
            ci_address = ci_address_begin.split(' ')[0]
            disk_name_end = inc['description'].split(':')[0]
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
                'detailed_desc': inc['description'],
                'disk_name': disk_name,
                'inc_number': inc['number'],
                'inc_sys_id': inc['sys_id'],
                'os_type': 'windows',
                'short_desc': inc['short_description'],
                'threshold_percent': threshold
            }
            self._sensor_service.dispatch(trigger='ntt_itsm.high_disk', payload=payload)
        elif (('memory usage on' in desc or 'memory used on' in desc) and ('intel' in assign_group.lower() or 'wintel' in assign_group.lower())):
            insertto_datastore = "true"           
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
                rec_short_desc = 'memory usage on'
                rec_detailed_desc = 'memory usage on'
                ci_address_begin = desc.split('memory usage on ')[-1]
                ci_address = ci_address_begin.split(' ')[0]                
            elif 'memory used on' in desc: 
                rec_short_desc = 'memory used on'
                rec_detailed_desc = 'memory used on'
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
                'detailed_desc': inc['description'],
                'inc_number': inc['number'],
                'inc_sys_id': inc['sys_id'],
                'os_type': 'windows',
                'short_desc': inc['short_description'],
                'threshold_percent': threshold,
                'incident_state': inc['incident_state'],
                'rec_short_desc': rec_short_desc,
                'rec_detailed_desc': rec_detailed_desc,
                'configuration_item_name': configuration_item_name,
                'memory_type':memory_type
            }
            self._sensor_service.dispatch(trigger='ntt_itsm.win_memory_high', payload=payload)
            
        elif (('Windows Service' in short_desc and 'is not running' in short_desc) or ('Service Alert:' in short_desc and 'has changed to Stopped state' in short_desc)):
            insertto_datastore = "true"    
            ci_address = ''
            rec_short_desc = ''
            rec_detailed_desc = ''
            
            if ('TrueSight' in short_desc and 'Windows Service' in short_desc and 'is not running on host'in short_desc ):
               ci_address_begin = short_desc.split('TrueSight ')[-1]  
               ci_address = ci_address_begin.split(' ')[0] 
               
               Find_After = self.afterString(short_desc, "Windows Service")
               Find_After = Find_After.strip()
               Find_Before = self.beforeString(Find_After,'is not running on host')
               Find_Before =Find_Before.strip()
               rec_short_desc = 'Windows Service'
               rec_detailed_desc = Find_Before
               service_name  = Find_Before               
            elif ('Windows Service' in short_desc and 'is not running on host'in short_desc ):
               ci_address = short_desc.split(' ')[0]               
               Find_After = self.afterString(short_desc, "Windows Service")
               Find_After = Find_After.strip()
               Find_Before = self.beforeString(Find_After,'is not running on host')
               Find_Before =Find_Before.strip()
               rec_short_desc = 'Windows Service'
               rec_detailed_desc = service_name 
               service_name  = Find_Before
            elif ('Windows Service' in short_desc and 'on host' in short_desc and 'is not running'in short_desc ):
               ci_address = short_desc.split(' ')[0]
               Find_After = self.afterString(short_desc, "Windows Service")
               Find_After = Find_After.strip()
               Find_Before = self.beforeString(Find_After,'on host') 
               Find_Before =Find_Before.strip()               
               service_name  = Find_Before 
               rec_short_desc = 'Windows Service'
               rec_detailed_desc = Find_Before
            elif ('Service Alert:' in short_desc and 'has changed to Stopped state' in short_desc  ):
               ci_address = short_desc.split(':')[0]
               Find_After = self.afterString(short_desc, "Service Alert:")
               Find_After = Find_After.strip()
               Find_Before = self.beforeString(Find_After,'has changed to Stopped state')
               Find_Before =Find_Before.strip()               
               service_name = short_desc.split(' ')[2]
               rec_short_desc = 'Service Alert:'
               rec_detailed_desc = service_name
            
            
            payload = {
                'assignment_group': assign_group,
                'ci_address': ci_address,
                'customer_name': company,
                'detailed_desc': inc['description'],
                'inc_number': inc['number'],
                'inc_sys_id': inc['sys_id'],                
                'short_desc': inc['short_description'],
                'incident_state': inc['incident_state'],
                'service_name': service_name,
                'rec_short_desc': rec_short_desc,
                'rec_detailed_desc': rec_detailed_desc,
                'configuration_item_name': configuration_item_name 
            }
            self._sensor_service.dispatch(trigger='ntt_itsm.win_service_check', payload=payload)
        elif (('cpu utilization on' in desc) and ('linux' in assign_group.lower())):                 
            insertto_datastore = "true"
            ci_address = ''
            
            # ci_address_begin = desc.split('cpu utilization on ')[-1]
            # ci_address = ci_address_begin.split(' ')[0]
            
            Find_Before = self.beforeString(short_desc,'Total CPU Utilization on') 
            Find_Before =Find_Before.strip()
            ci_address = Find_Before
            Find_After = self.afterString(ci_address, "TrueSight ")
            Find_After = Find_After.strip()
            ci_address = Find_After
            rec_short_desc = 'Total CPU Utilization on'
            rec_detailed_desc = 'Total CPU Utilization on'
            
            if ', th is' in desc:
               # threshold_begin = desc.split(', th is ')[-1]
               # threshold = threshold_begin.split('%')[0]
               Find_After = self.afterString(desc, "th is")
               Find_After = Find_After.strip()
               threshold = Find_After

               Find_Before = self.beforeString(threshold,'%') 
               Find_Before =Find_Before.strip()
               threshold = Find_Before
               threshold = self.beforeString(threshold,'.')               
            else:
               threshold = 85
            
            payload = {
                'assignment_group': assign_group,
                'ci_address': ci_address,
                'cpu_name': '_total',
                'cpu_type': 'ProcessorTotalProcessorTime',
                'customer_name': company,
                'detailed_desc': inc['description'],
                'inc_number': inc['number'],
                'inc_sys_id': inc['sys_id'],
                'os_type': 'linux',
                'short_desc': inc['short_description'],
                'threshold_percent': threshold,
                'incident_state': inc['incident_state'],
                'rec_short_desc': rec_short_desc,
                'rec_detailed_desc': rec_detailed_desc                
            }
            self._logger.info('Processing INC: ' + inc['number'] + '' + str(payload))
            self._sensor_service.dispatch(trigger='ntt_itsm.linux_cpu_high', payload=payload)              
        elif (('disk' in desc and 'is critical' in desc) and (('linux' in assign_group.lower()) or ('unix' in assign_group.lower()))):
            insertto_datastore = "true"
            ci_address = ''
            threshold = '85'
            Find_Before = self.beforeString(short_desc,'Disk') 
            Find_Before =Find_Before.strip()
            ci_address = Find_Before
            Find_After = self.afterString(short_desc, "Threshold is")
            Find_After = Find_After.strip()
            threshold = Find_After
            disk_name_before = self.beforeString(short_desc,'Critical.Used') 
            disk_name_before =disk_name_before.strip()
            disk_name = disk_name_before
            disk_name_after = self.afterString(disk_name_before, "Disk")
            disk_name_after = disk_name_after.strip()
            disk_name = disk_name_after
            rec_short_desc = 'Disk Capacity'
            rec_detailed_desc = disk_name             
            payload = {
                'assignment_group': assign_group,
                'ci_address': ci_address,
                'customer_name': company,
                'detailed_desc': inc['description'],
                'inc_number': inc['number'],
                'inc_sys_id': inc['sys_id'],                
                'short_desc': inc['short_description'],
                'incident_state': inc['incident_state'],
                'disk_name': disk_name,
                'os_type': 'linux',
                'disk_threshold': threshold,
                'rec_short_desc': rec_short_desc,
                'rec_detailed_desc': rec_detailed_desc,
                'configuration_item_name': configuration_item_name 
            }
            self._sensor_service.dispatch(trigger='ntt_itsm.disk_usage_check_linux', payload=payload)
        elif (('system performance processor queue length' in desc ) and ('intel' in assign_group.lower() or 'wintel' in assign_group.lower())):
            insertto_datastore = "true"
            ci_address = ''
            rec_short_desc = ''
            rec_detailed_desc = ''
            desc_org = inc['description']
            
            Find_Before = self.beforeString(desc_org,'System Performance')
            ci_address =Find_Before.strip()
            
            Find_After = self.afterString(desc_org, ">")
            Find_After = Find_After.strip()
            Find_Before = self.beforeString(Find_After,'Number')
            threshold_queue =Find_Before.strip()
            
            rec_short_desc = 'System Performance Processor Queue Length'
            rec_detailed_desc = 'System Performance Processor Queue Length'
            
            payload = {
                'assignment_group': assign_group,
                'ci_address': ci_address,
                'customer_name': company,
                'detailed_desc': inc['description'],
                'inc_number': inc['number'],
                'inc_sys_id': inc['sys_id'],
                'os_type': 'windows',
                'short_desc': inc['short_description'],
                'threshold_queue': threshold_queue,
                'incident_state': inc['incident_state'],
                'rec_short_desc': rec_short_desc,
                'rec_detailed_desc': rec_detailed_desc,
                'configuration_item_name': configuration_item_name,
                'cpu_type':'ProcessorQueueLength'                
            }
            self._sensor_service.dispatch(trigger='ntt_itsm.win_cpu_queue_length', payload=payload)
            
        elif (('is not running on host' in desc) and ('linux' in desc)):
            insertto_datastore = "true"
            #service            
            service_begin = desc.split('is not running on host')[0]
            service = service_begin.split('Linux process')[-1]
            service = service.strip()
            #CI Name
            ci_name_begin = desc.split('is not running on host')[-1]
            ci_name = ci_name_begin.strip()
         
            payload = {
                'assignment_group': assign_group,
                'ci_address': ci_address,
                'customer_name': company,
                'detailed_desc': inc['description'],
                'inc_number': inc['number'],
                'inc_sys_id': inc['sys_id'],
                'os_type': 'linux',
                'short_desc': inc['short_description'],
                'service': service,
                'incident_state': inc['incident_state'],
                'configuration_item_name': ci_name
            }
            self._sensor_service.dispatch(trigger='ntt_itsm.unix_process_alert', payload=payload)
            
        elif (('opsramp agent service is offline' in desc ) and ('intel' in assign_group.lower() or 'wintel' in assign_group.lower())):
            insertto_datastore = "true"
            ci_address = ''
            rec_short_desc = ''
            rec_detailed_desc = ''
            desc_org = inc['description']
            Find_Before = self.beforeString(desc_org,'OpsRamp Agent service is offline')
            ci_address =Find_Before.strip()
            
            rec_short_desc = 'OpsRamp agent is offline '
            rec_detailed_desc = 'OpsRamp Agent service is offline'            
            # self._logger.info('Already processing INC: ' + inc['number'] +'incident_open_at' + inc['opened_at'] )
            payload = {
                'assignment_group': assign_group,
                'ci_address': ci_address,
                'customer_name': company,
                'detailed_desc': inc['description'],
                'inc_number': inc['number'],
                'inc_sys_id': inc['sys_id'],
                'incident_open_at': inc['opened_at'], 
                'os_type': 'windows',
                'short_desc': inc['short_description'],
                'incident_state': inc['incident_state'],                
                'rec_short_desc': rec_short_desc,
                'rec_detailed_desc': rec_detailed_desc,
                'configuration_item_name': configuration_item_name,
                'configuration_item_env': configuration_item_env                
            }
            self._sensor_service.dispatch(trigger='ntt_itsm.win_monitoring_heartbeat_failure', payload=payload)
            
        elif (('network outage' in desc ) or ('device reboot detected' in desc )):
            insertto_datastore = "true"
            desc_org = inc['description']
            if (( 'NMSENVPOLL' in desc_org ) and ( 'Network Outage' in desc_org)):                 
                Find_Before = self.beforeString(desc_org,': Network Outage')
                Find_Before = Find_Before.strip()
                Find_Between = self.betweenString(Find_Before,":",":")
                ci_address = Find_Between.strip()
            elif (( 'NMSENVPOLL' in desc_org ) and ( 'Device Reboot Detected' in desc_org)):
                Find_Before = self.beforeString(desc_org,': Device Reboot Detected')
                Find_Before = Find_Before.strip()
                Find_Between = self.betweenString(Find_Before,":",":")
                ci_address = Find_Between.strip()
            else:
                Find_Before = self.beforeString(desc_org,':Network Outage')
                Find_Before = Find_Before.strip()
                Find_Between = self.betweenString(Find_Before,":",":")
                Find_Between = Find_Between.strip()
                Find_After = self.afterString(Find_Between, ":")
                ci_address = Find_After.strip()
            
            if 'Network Outage' in desc_org:
                rec_short_desc = 'Network Outage'
                rec_detailed_desc = 'Network Outage'
            elif 'Device Reboot Detected' in desc_org:
                rec_short_desc = 'Device Reboot Detected'
                rec_detailed_desc = 'Device Reboot Detected'
            
            payload = {
                'inc_number': inc['number'],
                'inc_sys_id': inc['sys_id'],
                'ci_address': ci_address,
                'assignment_group': assign_group,                
                'customer_name': company,
                'short_desc': inc['short_description'],
                'detailed_desc': inc['description'],
                'incident_state': inc['incident_state'],
                'incident_open_at': inc['opened_at'],    
                'rec_short_desc': rec_short_desc,
                'rec_detailed_desc': rec_detailed_desc,
                'configuration_item_name': configuration_item_name              
            }
            self._sensor_service.dispatch(trigger='ntt_itsm.nw_unreachable_to_ping', payload=payload)
        elif (('snmp agent not responding' in desc )): 
            insertto_datastore = "true"
            desc_org = inc['description']
            ci_address = ''
            if (( 'NMSENVPOLL' in desc_org )):                 
                Find_After = self.afterString(desc_org,'nttdataservices.com :')
                Find_Before = self.beforeString(Find_After,':')
                ci_address = Find_Before.strip()
             
                      
            rec_short_desc = 'SNMP Agent Not Responding'
            rec_detailed_desc = 'SNMP Agent Not Responding'
            
            payload = {
                'inc_number': inc['number'],
                'inc_sys_id': inc['sys_id'],
                'ci_address': ci_address,
                'assignment_group': assign_group,                
                'customer_name': company,
                'short_desc': inc['short_description'],
                'detailed_desc': inc['description'],
                'incident_state': inc['incident_state'],
                'incident_open_at': inc['opened_at'],    
                'rec_short_desc': rec_short_desc,
                'rec_detailed_desc': rec_detailed_desc,
                'configuration_item_name': configuration_item_name              
            }
            self._sensor_service.dispatch(trigger='ntt_itsm.nw_snmp_not_responding', payload=payload)    
        elif('ap antenna offline:' in desc):
            insertto_datastore = "true"
            desc = inc['description'].lower()
            short_desc = inc['short_description']
            if assign_group == '':
                chekc_uptime = False
                os_type = ''
            else:
                check_uptime = True
                os_type = 'windows' if 'intel' in assign_group.lower() else 'linux'
            ci_address = desc.split(':AP Antenna Offline:')[0].split(':')[2]
            payload = {
                    'assignment_group': assign_group,
                    'ci_address': ci_address,
                    'customer_name': company,
                    'detailed_desc': inc['description'],
                    'inc_number': inc['number'],
                    'inc_sys_id': inc['sys_id'],
                    'short_desc': inc['short_description']
            }
            print("Dispatching the trigger")
            self._sensor_service.dispatch(trigger='ntt_itsm.wireless_accesspoint_antenna_offline_alarm', payload=payload)
            
        return insertto_datastore
        
    def cleanup(self):
        pass

    def add_trigger(self, trigger):
        pass

    def update_trigger(self, trigger):
        pass

    def remove_trigger(self, trigger):
        pass

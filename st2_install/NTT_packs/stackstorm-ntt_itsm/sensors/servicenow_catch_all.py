#!/usr/bin/env python
# Copyright 2021 NTTData 
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
import time

__all__ = [
    'servicenowcatchall'
]


class servicenowcatchall(PollingSensor):
    def __init__(self, sensor_service, config=None, poll_interval=None):
        super(servicenowcatchall, self).__init__(sensor_service=sensor_service,
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
        # Query for all active and open incidents        
        sn_inc_endpoint = '/api/now/table/incident?sysparm_query=stateIN2,-3,-5^' \
            'assigned_to.name=Automation Service^sys_updated_on<javascript:gs.hoursAgoStart(1)' \
            '&sysparm_fields=incident_state%2Csys_id%2Cnumber'
        
        sn_inc_url = "https://{0}{1}".format(self.sn_url,
                                             sn_inc_endpoint)

        sn_result = requests.request('GET',
                                     sn_inc_url,
                                     auth=(self.sn_username, self.sn_password),
                                     headers=self.servicenow_headers)

        sn_result.raise_for_status()
        sn_incidents = sn_result.json()['result']
        self._logger.info('servicenow catchall sensor : ' + str(sn_incidents))
        self.check_incidents(sn_incidents)

    def check_incidents(self, sn_incidents):
        ''' Create a trigger to run cleanup on any open incidents that are not being processed
        '''
        
        for inc in sn_incidents:
            inc_st2_key = 'servicenow.incidents_processing'
            processing_incs = self.st2_client.keys.get_by_name(inc_st2_key)
            processing_incs = [] if processing_incs is None else ast.literal_eval(processing_incs.value)           

            if inc['number'] not in processing_incs:              
               processing_incs.append(inc['number'])
               incs_str = str(processing_incs)
               kvp = KeyValuePair(name=inc_st2_key, value=incs_str)
               self.st2_client.keys.update(kvp)
               self._logger.info('Servicenow Incident catch all processing INC: ' + inc['number'])
               
            payload = {
                'escalate': bool("true"),                
                'inc_id': inc['sys_id'],                 
                'notes': 'Automation is escalating this Incident as there has been no progress for at least 1 hour.'
            }
            self._sensor_service.dispatch(trigger='ntt_itsm.servicenow_incident_catchall', payload=payload)
            
    def cleanup(self):
        pass

    def add_trigger(self, trigger):
        pass

    def update_trigger(self, trigger):
        pass

    def remove_trigger(self, trigger):
        pass

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
from lib.base_action import BaseAction


class ServiceNowIncidentUpdate(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(ServiceNowIncidentUpdate, self).__init__(config)

    def run(self, close, escalate, inc_sys_id, notes, work_in_progress):
        endpoint = '/api/now/table/incident/' + inc_sys_id

        if work_in_progress:
            payload = {
                'assigned_to': 'Automation Service',
                'incident_state': '-3',
                'state': '-3'
            }
            if notes:
                payload['work_notes'] = notes
        elif close:
            payload = {
                'incident_state': '7',
                'state': '7',
                'close_code': 'Solved Remotely (Permanently)'
            }
            if notes:
                payload['close_notes'] = notes
            else:
                raise "notes is a required field when closing an incident!"
        elif escalate:
            payload = {
                'assigned_to': '',
                'incident_state': '2',
                'state': '2'
            }
            if notes:
                payload['work_notes'] = notes
        else:
            raise "One of close, escalate, or work_in_progress must be set to True!"

        inc = self.sn_api_call('PATCH', endpoint, payload=payload)

        return inc

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
from ntt_base_action_test_case import NTTBaseActionTestCase
from itsm_incident_update import ITSMIncidentUpdate
from st2common.runners.base_action import Action
from lib.base_action import BaseAction
import mock

__all__ = [
    'ITSMIncidentUpdateTestCase'
]


class ITSMIncidentUpdateTestCase(NTTBaseActionTestCase):
    __test__ = True
    action_cls = ITSMIncidentUpdate

    def test_init(self):
        action = self.get_action_instance(self.config_good)
        self.assertIsInstance(action, ITSMIncidentUpdate)
        self.assertIsInstance(action, BaseAction)
        self.assertIsInstance(action, Action)

    @mock.patch("lib.base_action.BaseAction.sn_api_call")
    def test_run_wip(self, mock_api_call):
        action = self.get_action_instance(self.config_good)

        test_sys_id = '1234'
        test_endpoint = '/api/now/table/incident/' + test_sys_id
        test_close = False
        test_escalate = False
        test_wip = True
        test_notes = 'Hello World'
        test_payload = {
            'assigned_to': 'Automation Service',
            'incident_state': '-3',
            'state': '-3',
            'work_notes': test_notes
        }

        expected_result = 'result'

        mock_api_call.return_value = expected_result

        result = action.run(test_close, test_escalate, test_sys_id, test_notes, test_wip)
        self.assertEqual(result, expected_result)
        mock_api_call.assert_called_with('PATCH', test_endpoint,
                                         payload=test_payload)

    @mock.patch("lib.base_action.BaseAction.sn_api_call")
    def test_run_close(self, mock_api_call):
        action = self.get_action_instance(self.config_good)

        test_sys_id = '1234'
        test_endpoint = '/api/now/table/incident/' + test_sys_id
        test_close = True
        test_escalate = False
        test_wip = False
        test_notes = 'Hello World'
        test_payload = {
            'incident_state': '7',
            'state': '7',
            'close_code': 'Solved Remotely (Permanently)',
            'close_notes': test_notes
        }

        expected_result = 'result'

        mock_api_call.return_value = expected_result

        result = action.run(test_close, test_escalate, test_sys_id, test_notes, test_wip)
        self.assertEqual(result, expected_result)
        mock_api_call.assert_called_with('PATCH', test_endpoint,
                                         payload=test_payload)

    @mock.patch("lib.base_action.BaseAction.sn_api_call")
    def test_run_escalate(self, mock_api_call):
        action = self.get_action_instance(self.config_good)

        test_sys_id = '1234'
        test_endpoint = '/api/now/table/incident/' + test_sys_id
        test_close = False
        test_escalate = True
        test_wip = False
        test_notes = None
        test_payload = {
            'assigned_to': '',
            'incident_state': '2',
            'state': '2'
        }

        expected_result = 'result'

        mock_api_call.return_value = expected_result

        result = action.run(test_close, test_escalate, test_sys_id, test_notes, test_wip)
        self.assertEqual(result, expected_result)
        mock_api_call.assert_called_with('PATCH', test_endpoint,
                                         payload=test_payload)

    def test_run_error(self):
        action = self.get_action_instance(self.config_good)

        test_sys_id = '1234'
        test_close = False
        test_escalate = False
        test_wip = False
        test_notes = None

        with self.assertRaises(Exception):
            action.run(test_close, test_escalate, test_sys_id, test_notes, test_wip)

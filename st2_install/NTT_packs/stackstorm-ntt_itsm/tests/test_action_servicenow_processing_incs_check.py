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
from servicenow_processing_incs_check import ServicenowProcessingIncsCheck
from st2common.runners.base_action import Action
import mock

__all__ = [
    'ServicenowProcessingIncsCheckTestCase'
]


class ServicenowProcessingIncsCheckTestCase(NTTBaseActionTestCase):
    __test__ = True
    action_cls = ServicenowProcessingIncsCheck

    def test_init(self):
        action = self.get_action_instance(self.config_good)
        self.assertIsInstance(action, ServicenowProcessingIncsCheck)
        self.assertIsInstance(action, Action)

    @mock.patch("servicenow_processing_incs_check.KeyValuePair")
    @mock.patch("lib.base_action.BaseAction.sn_api_call")
    @mock.patch("lib.base_action.BaseAction.st2_client_get")
    def test_run(self, mock_client, mock_api_call, mock_KeyValuePair):
        action = self.get_action_instance(self.config_good)

        test_inc_st2_key = 'st2.key'
        # Each API call is expected to return an array with a single element
        test_incs = [
            [{
                'number': 'INC0001',
                'state': '1'
            }],
            [{
                'number': 'INC0002',
                'state': '6'
            }],
            [{
                'number': 'INC0003',
                'state': '1'
            }],
            [{
                'number': 'INC0004',
                'state': '8'
            }]
        ]

        mock_KeyValuePair.return_value = 'keys_return'
        mock_keys = mock.Mock(value="['INC0001', 'INC0002', 'INC0003', 'INC0004']")
        mock_st2_client = mock.MagicMock()
        mock_st2_client.keys.get_by_name.return_value = mock_keys
        mock_st2_client.keys.update.return_value = 'update complete'
        mock_client.return_value = mock_st2_client

        mock_api_call.side_effect = test_incs

        expected_result = ['INC0001', 'INC0003']

        result = action.run(test_inc_st2_key)

        self.assertEqual(result, expected_result)
        mock_st2_client.keys.get_by_name.assert_called_with(test_inc_st2_key)
        mock_api_call.assert_has_calls = [
            mock.call('GET', '/api/now/table/incident?sysparm_query=number=INC0001'),
            mock.call('GET', '/api/now/table/incident?sysparm_query=number=INC0002'),
            mock.call('GET', '/api/now/table/incident?sysparm_query=number=INC0003'),
            mock.call('GET', '/api/now/table/incident?sysparm_query=number=INC0004')
        ]
        mock_KeyValuePair.assert_called_with(name=test_inc_st2_key, value=str(expected_result))

    @mock.patch("servicenow_processing_incs_check.KeyValuePair")
    @mock.patch("lib.base_action.BaseAction.sn_api_call")
    @mock.patch("lib.base_action.BaseAction.st2_client_get")
    def test_run_none(self, mock_client, mock_api_call, mock_KeyValuePair):
        action = self.get_action_instance(self.config_good)

        test_inc_st2_key = 'st2.key'
        # Each API call is expected to return an array with a single element
        # The last INC here mocks an example of one that wasn't found
        test_incs = [
            [{
                'number': 'INC0001',
                'state': '1'
            }],
            [{
                'number': 'INC0002',
                'state': '7'
            }],
            []
        ]

        mock_KeyValuePair.return_value = 'keys_return'
        mock_keys = mock.Mock(value="['INC0001', 'INC0002', 'INC0003']")
        mock_st2_client = mock.MagicMock()
        mock_st2_client.keys.get_by_name.return_value = mock_keys
        mock_st2_client.keys.update.return_value = 'update complete'
        mock_client.return_value = mock_st2_client

        mock_api_call.side_effect = test_incs

        expected_result = ['INC0001']

        result = action.run(test_inc_st2_key)

        self.assertEqual(result, expected_result)
        mock_st2_client.keys.get_by_name.assert_called_with(test_inc_st2_key)
        mock_api_call.assert_has_calls = [
            mock.call('GET', '/api/now/table/incident?sysparm_query=number=INC0001'),
            mock.call('GET', '/api/now/table/incident?sysparm_query=number=INC0002'),
            mock.call('GET', '/api/now/table/incident?sysparm_query=number=INC0003')
        ]
        mock_KeyValuePair.assert_called_with(name=test_inc_st2_key, value=str(expected_result))

    @mock.patch("lib.base_action.BaseAction.sn_api_call")
    @mock.patch("lib.base_action.BaseAction.st2_client_get")
    def test_run_multiple_error(self, mock_client, mock_api_call):
        action = self.get_action_instance(self.config_good)

        test_inc_st2_key = 'st2.key'
        test_incs = [
            [
                {
                    'number': 'INC0001',
                    'state': '1'
                },
                {
                    'number': 'INC0001',
                    'state': '6'
                }
            ]
        ]

        mock_keys = mock.Mock(value="['INC0001']")
        mock_st2_client = mock.MagicMock()
        mock_st2_client.keys.get_by_name.return_value = mock_keys
        mock_client.return_value = mock_st2_client

        mock_api_call.side_effect = test_incs

        with self.assertRaises(Exception):
            action.run(test_inc_st2_key)

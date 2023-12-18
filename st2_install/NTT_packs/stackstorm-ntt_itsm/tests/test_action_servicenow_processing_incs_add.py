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
from servicenow_processing_incs_add import ServicenowProcessingIncsAdd
from st2common.runners.base_action import Action
import mock

__all__ = [
    'ServicenowProcessingIncsAddTestCase'
]


class ServicenowProcessingIncsAddTestCase(NTTBaseActionTestCase):
    __test__ = True
    action_cls = ServicenowProcessingIncsAdd

    def test_init(self):
        action = self.get_action_instance(self.config_good)
        self.assertIsInstance(action, ServicenowProcessingIncsAdd)
        self.assertIsInstance(action, Action)

    @mock.patch("lib.base_action.BaseAction.st2_client_get")
    def test_run_processed(self, mock_client):
        action = self.get_action_instance(self.config_good)

        test_inc_id = 'INC1234'
        test_inc_st2_key = 'st2.key'

        mock_keys = mock.Mock(value="['INC9876', 'INC1234']")
        mock_st2_client = mock.MagicMock()
        mock_st2_client.keys.get_by_name.return_value = mock_keys
        mock_client.return_value = mock_st2_client

        result = action.run(test_inc_id, test_inc_st2_key)

        self.assertEqual(result, "The given incident ID is already being processed")

    @mock.patch("servicenow_processing_incs_add.KeyValuePair")
    @mock.patch("lib.base_action.BaseAction.st2_client_get")
    def test_run(self, mock_client, mock_KeyValuePair):
        action = self.get_action_instance(self.config_good)

        test_inc_id = '1'
        test_inc_st2_key = 'st2.key'

        mock_KeyValuePair.return_value = 'keys_return'
        mock_keys = mock.Mock(value="['INC9876', 'INC1234']")
        mock_st2_client = mock.MagicMock()
        mock_st2_client.keys.get_by_name.return_value = mock_keys
        mock_st2_client.keys.update.return_value = 'update complete'
        mock_client.return_value = mock_st2_client

        expected_result = {
            'key': test_inc_st2_key,
            'value': "['INC9876', 'INC1234', '1']"
        }

        result = action.run(test_inc_id, test_inc_st2_key)

        self.assertEqual(result, expected_result)

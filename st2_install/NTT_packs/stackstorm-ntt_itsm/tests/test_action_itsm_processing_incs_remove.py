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
from itsm_processing_incs_remove import ITSMProcessingIncsRemove
from st2common.runners.base_action import Action
from lib.base_action import BaseAction
import mock

__all__ = [
    'ITSMProcessingIncsRemoveTestCase'
]


class ITSMProcessingIncsRemoveTestCase(NTTBaseActionTestCase):
    __test__ = True
    action_cls = ITSMProcessingIncsRemove

    def test_init(self):
        action = self.get_action_instance(self.config_good)
        self.assertIsInstance(action, ITSMProcessingIncsRemove)
        self.assertIsInstance(action, BaseAction)
        self.assertIsInstance(action, Action)

    @mock.patch("lib.base_action.BaseAction.st2_client_get")
    def test_run_processed(self, mock_client):
        action = self.get_action_instance(self.config_good)

        test_inc_id = 'INC1234'

        mock_keys = mock.Mock(value="['INC9876']")
        mock_st2_client = mock.MagicMock()
        mock_st2_client.keys.get_by_name.return_value = mock_keys
        mock_client.return_value = mock_st2_client

        result = action.run(test_inc_id)

        self.assertEqual(result, "The given incident ID was not found in the list")

    @mock.patch("servicenow_processing_incs_remove.KeyValuePair")
    @mock.patch("lib.base_action.BaseAction.st2_client_get")
    def test_run(self, mock_client, mock_KeyValuePair):
        action = self.get_action_instance(self.config_good)

        test_inc_id = 'INC0001'

        mock_KeyValuePair.return_value = 'keys_return'
        mock_keys = mock.Mock(value="['INC9876', 'INC1234', 'INC0001']")
        mock_st2_client = mock.MagicMock()
        mock_st2_client.keys.get_by_name.return_value = mock_keys
        mock_st2_client.keys.update.return_value = 'update complete'
        mock_client.return_value = mock_st2_client

        expected_result = {
            'key': 'servicenow.incidents_processing',
            'value': "['INC9876', 'INC1234']"
        }

        result = action.run(test_inc_id)

        self.assertEqual(result, expected_result)

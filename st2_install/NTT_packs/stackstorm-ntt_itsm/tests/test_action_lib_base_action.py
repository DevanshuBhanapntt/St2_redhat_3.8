#!/usr/bin/env python
# Copyright 2019 Encore Technologies
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
import mock
from lib.base_action import BaseAction
from config_vars_get import ConfigVarsGet

__all__ = [
    'BaseActionTestCase'
]


class BaseActionTestCase(NTTBaseActionTestCase):
    __test__ = True
    action_cls = ConfigVarsGet

    def test_init_config_good(self):
        action = self.get_action_instance(self.config_good)
        self.assertIsInstance(action, BaseAction)

    def test_init_config_blank(self):
        with self.assertRaises(ValueError):
            action = self.get_action_instance(self.config_blank)
            self.assertIsInstance(action, BaseAction)

    def test_init_config_no_tool(self):
        with self.assertRaises(ValueError):
            action = self.get_action_instance(self.config_no_tool)
            self.assertIsInstance(action, BaseAction)

    def test_init_config_no_creds(self):
        with self.assertRaises(ValueError):
            action = self.get_action_instance(self.config_no_creds)
            self.assertIsInstance(action, BaseAction)

    def test_init_config_none(self):
        with self.assertRaises(ValueError):
            action = self.get_action_instance({})
            self.assertIsInstance(action, BaseAction)

    @mock.patch("lib.base_action.socket")
    @mock.patch("lib.base_action.Client")
    def test_st2_client_get(self, mock_client, mock_socket):
        action = self.get_action_instance(self.config_good)

        mock_socket.getfqdn.return_value = "st2.com"
        test_st2_fqdn = 'https://st2.com/'

        expected_result = 'result'
        mock_client.return_value = expected_result

        result = action.st2_client_get()

        self.assertEqual(result, expected_result)
        mock_client.assert_called_with(base_url=test_st2_fqdn)
        self.assertTrue(mock_socket.getfqdn.called)

    @mock.patch("lib.base_action.requests.request")
    def test_sn_api_call(self, mock_request):
        action = self.get_action_instance(self.config_good)

        method = "POST"
        test_endpoint = "/api/ent/v1/endpoint"
        test_payload = {"test": "test"}
        test_params = {"force": "yes"}
        test_headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

        test_server = self.config_good['servicenow']['url']
        test_user = self.config_good['servicenow']['username']
        test_pass = self.config_good['servicenow']['password']

        test_url = "https://{0}{1}".format(test_server, test_endpoint)

        expected_result = {"result": "expected result"}
        # mock
        mock_request.return_value = mock.MagicMock()
        mock_request.return_value.raise_for_status.return_value = None
        mock_request.return_value.json.return_value = {"result": expected_result}

        # execute
        result = action.sn_api_call(method, test_endpoint, payload=test_payload,
                                    params=test_params)

        # assert
        self.assertEqual(result, expected_result)
        # Check that requests.post is called with the correct parameters
        mock_request.assert_called_with(
            method,
            test_url,
            auth=(test_user, test_pass),
            json=test_payload,
            headers=test_headers,
            params=test_params
        )

    @mock.patch("lib.base_action.requests.request")
    def test_sn_api_call_unauthorized(self, mock_request):
        action = self.get_action_instance(self.config_good)

        method = "POST"
        test_endpoint = "/api/ent/v1/endpoint"
        test_payload = {"test": "test"}
        test_params = {"force": "yes"}

        mock_result = mock.MagicMock()
        mock_result.raise_for_status.side_effect = RuntimeError('test exception')
        mock_request.return_value = mock_result

        # Check that the function returns an error
        with self.assertRaises(RuntimeError):
            action.sn_api_call(method, test_endpoint, payload=test_payload,
                               params=test_params)

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

from config_vars_get import ConfigVarsGet
from st2common.runners.base_action import Action

__all__ = [
    'ConfigVarsGetTestCase'
]


class ConfigVarsGetTestCase(NTTBaseActionTestCase):
    __test__ = True
    action_cls = ConfigVarsGet

    def test_init(self):
        action = self.get_action_instance(self.config_good)
        self.assertIsInstance(action, ConfigVarsGet)
        self.assertIsInstance(action, Action)

    def test_check_overrides(self):
        action = self.get_action_instance(self.config_good)

        test_config_dict = {
            'connections': {
                'ssh_username': "root",
                'ssh_password': "passwd",
                'winrm_username': "administrator",
                'winrm_password': "password",
                'winrm_port': "5986",
                'winrm_scheme': "https",
                'winrm_verify_ssl': "false"
            },
            'test_var1': "test1",
            'test_var2': "test2",
            'test_var3': "test3"
        }

        test_workflow_dict = {
            'connections': {
                'ssh_username': "root",
                'ssh_password': "passwd",
                'winrm_username': "administrator",
                'winrm_password': "password",
                'winrm_port': "5986",
                'winrm_scheme': "https",
                'winrm_verify_ssl': "false"
            },
            'test_var1': "test1",
            'test_var2': "test2",
            'test_var3': "test3"
        }

        expected_result = {
            'connections': {
                'ssh_username': "root",
                'ssh_password': "passwd",
                'winrm_username': "administrator",
                'winrm_password': "password",
                'winrm_port': "5986",
                'winrm_scheme': "https",
                'winrm_verify_ssl': "false"
            },
            'test_var1': "test1",
            'test_var2': "test2",
            'test_var3': "test3"
        }

        result = action.check_overrides(test_workflow_dict, test_config_dict)
        self.assertEqual(result, expected_result)

    def test_check_overrides_2(self):
        action = self.get_action_instance(self.config_good)

        test_config_dict = {
            'connections': {
                'ssh_username': "root",
                'ssh_password': "passwd",
                'winrm_username': "administrator",
                'winrm_password': "password",
                'winrm_port': "5986",
                'winrm_scheme': "https",
                'winrm_verify_ssl': "false"
            },
            'test_var1': "test1",
            'test_var2': "test2",
            'test_var3': "test3"
        }

        test_workflow_dict = {
            'connections': {
                'ssh_username': "root",
                'ssh_password': "passwd",
                'winrm_username': "administrator",
                'winrm_password': "password",
                'winrm_port': "5986",
                'winrm_scheme': "https",
                'winrm_verify_ssl': "false"
            }
        }

        expected_result = {
            'connections': {
                'ssh_username': "root",
                'ssh_password': "passwd",
                'winrm_username': "administrator",
                'winrm_password': "password",
                'winrm_port': "5986",
                'winrm_scheme': "https",
                'winrm_verify_ssl': "false"
            },
            'test_var1': "test1",
            'test_var2': "test2",
            'test_var3': "test3"
        }

        result = action.check_overrides(test_workflow_dict, test_config_dict)
        self.assertEqual(result, expected_result)

    def test_check_overrides_3(self):
        action = self.get_action_instance(self.config_good)

        test_config_dict = {
            'connections': {
                'ssh_username': "root",
                'ssh_password': "passwd",
                'winrm_username': "administrator",
                'winrm_password': "this will be changed",
                'winrm_port': "5986",
                'winrm_scheme': "https",
                'winrm_verify_ssl': "false"
            },
            'test_var1': "this is not the real value",
            'test_var2': "test2",
            'test_var3': "test3"
        }

        test_workflow_dict = {
            'connections': {
                'ssh_username': "root",
                'ssh_password': "passwd",
                'winrm_username': "administrator",
                'winrm_password': "password",
                'winrm_port': "5986",
                'winrm_scheme': "https",
                'winrm_verify_ssl': "false"
            },
            'test_var1': "test1",
            'test_var2': "test2",
            'test_var3': "test3"
        }

        expected_result = {
            'connections': {
                'ssh_username': "root",
                'ssh_password': "passwd",
                'winrm_username': "administrator",
                'winrm_password': "password",
                'winrm_port': "5986",
                'winrm_scheme': "https",
                'winrm_verify_ssl': "false"
            },
            'test_var1': "test1",
            'test_var2': "test2",
            'test_var3': "test3"
        }

        result = action.check_overrides(test_workflow_dict, test_config_dict)
        self.assertEqual(result, expected_result)

    def test_run(self):
        action = self.get_action_instance(self.config_good)

        test_cust = "cus"

        expected_result = {
            'connections': {
                'ssh_username': "root",
                'ssh_password': "passwd",
                'winrm_username': "administrator",
                'winrm_password': "password",
                'winrm_port': "5986",
                'winrm_scheme': "https",
                'winrm_verify_ssl': "false"
            },
            'test_var1': "test1",
            'test_var2': "test2",
            'test_var3': "test3"
        }

        result = action.run(test_cust, {})
        self.assertEqual(result, expected_result)

    def test_run_with_overrides(self):
        action = self.get_action_instance(self.config_good)

        test_cust = "cus"

        test_workflow_dict = {
            'test_var1': "test4",
            'test_var2': "test5",
            'test_var3': "test6"
        }

        expected_result = {
            'connections': {
                'ssh_username': "root",
                'ssh_password': "passwd",
                'winrm_username': "administrator",
                'winrm_password': "password",
                'winrm_port': "5986",
                'winrm_scheme': "https",
                'winrm_verify_ssl': "false"
            },
            'test_var1': "test4",
            'test_var2': "test5",
            'test_var3': "test6"
        }

        result = action.run(test_cust, test_workflow_dict)
        self.assertEqual(result, expected_result)

    # Verify that only variables from the given customer are returned
    def test_run_config_no_default(self):
        action = self.get_action_instance(self.config_no_default)

        test_cust = "cus"

        expected_result = {
            'connections': {
                'ssh_username': "root",
                'ssh_password': "passwd",
                'winrm_username': "administrator",
                'winrm_password': "password"
            },
            'test_var1': "test1"
        }

        result = action.run(test_cust, {})
        self.assertEqual(result, expected_result)

    # This is expected to fail because it is using a config with no default customer
    # and it is expecting customer "cus"
    def test_run_config_no_default_error(self):
        action = self.get_action_instance(self.config_no_default)

        test_cust = "fail"

        with self.assertRaises(Exception):
            action.run(test_cust, {})

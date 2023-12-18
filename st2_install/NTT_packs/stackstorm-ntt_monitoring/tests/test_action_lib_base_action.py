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

from lib.base_action import BaseAction

__all__ = [
    'BaseActionTestCase'
]


class BaseActionTestCase(NTTBaseActionTestCase):
    __test__ = True
    action_cls = BaseAction

    def test_init_config_good(self):
        action = self.get_action_instance(self.config_good)
        self.assertIsInstance(action, BaseAction)

    def test_init_config_blank(self):
        with self.assertRaises(ValueError):
            action = self.get_action_instance(self.config_blank)
            self.assertIsInstance(action, BaseAction)

    def test_init_config_none(self):
        with self.assertRaises(ValueError):
            action = self.get_action_instance({})
            self.assertIsInstance(action, BaseAction)

    def test_get_del_arg_present(self):
        action = self.get_action_instance(self.config_good)
        test_dict = {"key1": "value1",
                     "key2": "value2"}
        test_key = "key1"
        expected_value = test_dict["key1"]
        result_value = action.get_del_arg(test_key, test_dict)
        self.assertEqual(result_value, expected_value)

    def test_get_del_arg_missing(self):
        action = self.get_action_instance(self.config_good)
        test_dict = {"key1": "value1",
                     "key2": "value2"}
        test_key = "key3"
        expected_value = None
        result_value = action.get_del_arg(test_key, test_dict)
        self.assertEqual(result_value, expected_value)

    def test_get_del_arg_delete_present(self):
        action = self.get_action_instance(self.config_good)
        test_dict = {"key1": "value1",
                     "key2": "value2"}
        test_key = "key1"
        expected_dict = {"key2": "value2"}
        expected_value = test_dict["key1"]
        result_value = action.get_del_arg(test_key, test_dict, True)
        self.assertEqual(result_value, expected_value)
        self.assertEqual(test_dict, expected_dict)

    def test_get_del_arg_delete_missing(self):
        action = self.get_action_instance(self.config_good)
        test_dict = {"key1": "value1",
                     "key2": "value2"}
        test_key = "key3"
        expected_dict = test_dict
        expected_value = None
        result_value = action.get_del_arg(test_key, test_dict, True)
        self.assertEqual(result_value, expected_value)
        self.assertEqual(test_dict, expected_dict)

    def test_run(self):
        action = self.get_action_instance(self.config_good)

        with self.assertRaises(RuntimeError):
            action.run()

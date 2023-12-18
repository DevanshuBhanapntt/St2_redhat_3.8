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

from merge_dicts import MergeDicts
from st2common.runners.base_action import Action

__all__ = [
    'MergeDictsTestCase'
]


class MergeDictsTestCase(NTTBaseActionTestCase):
    __test__ = True
    action_cls = MergeDicts

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, MergeDicts)
        self.assertIsInstance(action, Action)

    def test_run(self):
        action = self.get_action_instance({})
        kwargs_dict = {"dicts": [{"key1": "value1",
                                  "key2": "value2"},
                                 {"key3": "value3"}]}
        result = action.run(**kwargs_dict)
        self.assertEqual(result, {"key1": "value1",
                                  "key2": "value2",
                                  "key3": "value3"})

    def test_run_overwrite(self):
        action = self.get_action_instance({})
        kwargs_dict = {"dicts": [{"key1": "value1",
                                  "key2": "value2"},
                                 {"key2": "overwrite value2"}]}
        result = action.run(**kwargs_dict)
        self.assertEqual(result, {"key1": "value1",
                                  "key2": "overwrite value2"})

    def test_run_dict_none(self):
        action = self.get_action_instance({})
        kwargs_dict = {"dicts": [{"key1": "value1",
                                  "key2": "value2"},
                                 None]}
        result = action.run(**kwargs_dict)
        self.assertEqual(result, {"key1": "value1",
                                  "key2": "value2"})

    def test_run_single(self):
        action = self.get_action_instance({})
        kwargs_dict = {"dicts": [{"key1": "value1",
                                  "key2": "value2"}]}
        result = action.run(**kwargs_dict)
        self.assertEqual(result, {"key1": "value1",
                                  "key2": "value2"})

    def test_run_empty(self):
        action = self.get_action_instance({})
        kwargs_dict = {"dicts": []}
        result = action.run(**kwargs_dict)
        self.assertEqual(result, {})

    def test_run_single_none(self):
        action = self.get_action_instance({})
        kwargs_dict = {"dicts": [None]}
        result = action.run(**kwargs_dict)
        self.assertEqual(result, {})

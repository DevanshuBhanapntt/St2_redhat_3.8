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

    def test_run(self):
        action = self.get_action_instance(self.config_good)

        expected_result = {
            'itsm_tool': 'servicenow',
            'servicenow': {
                'url': 'test.service-now.com',
                'username': 'snuser',
                'password': 'snpass'
            },
            'helix': {
                'url': 'helix.com',
                'username': 'huser',
                'password': 'hpass'
            }
        }

        result = action.run()
        self.assertEqual(result, expected_result)

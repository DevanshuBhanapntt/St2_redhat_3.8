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
import datetime

from convert_timestamp import ConvertTimestamp
from st2common.runners.base_action import Action

__all__ = [
    'ConvertTimestampTestCase'
]


class ConvertTimestampTestCase(NTTBaseActionTestCase):
    __test__ = True
    action_cls = ConvertTimestamp

    def test_init(self):
        action = self.get_action_instance(self.config_good)
        self.assertIsInstance(action, ConvertTimestamp)
        self.assertIsInstance(action, Action)

    def test_convert_timestamp(self):
        action = self.get_action_instance({})
        result = action.convert_timestamp('2021-06-16 20:08:24.586607+00:00')
        self.assertEqual(result, datetime.datetime(2021, 6, 16, 20, 8, 24, 586607))

    def test_run(self):
        action = self.get_action_instance(self.config_good)

        start_timestamp = "2021-06-16 20:08:24.586607+00:00"
        end_timestamp = "2021-06-16 20:11:39.089285+00:00"

        test_data_dict = {
            'test': 'value'
        }

        expected_result = {
            'test': 'value',
            'Start_Time': '2021-06-16T20:08:24.586',
            'Duration': 194.502678
        }

        result = action.run(test_data_dict, end_timestamp, start_timestamp)

        self.assertEqual(result, expected_result)

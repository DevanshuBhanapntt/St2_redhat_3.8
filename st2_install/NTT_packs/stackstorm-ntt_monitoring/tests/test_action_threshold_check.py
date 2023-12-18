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

from threshold_check import ThresholdCheck
from st2common.runners.base_action import Action
from lib.base_action import BaseAction

import mock

__all__ = [
    'ThresholdCheckTestCase'
]


class ThresholdCheckTestCase(NTTBaseActionTestCase):
    __test__ = True
    action_cls = ThresholdCheck

    def test_init(self):
        action = self.get_action_instance(self.config_good)
        self.assertIsInstance(action, ThresholdCheck)
        self.assertIsInstance(action, BaseAction)
        self.assertIsInstance(action, Action)

    def test_check_value_lower_fail(self):
        action = self.get_action_instance(self.config_good)
        action.threshold_passed = None
        test_fail_check_counter = 0
        threshold_type = 'lower'
        threshold = 100
        value = 99
        result = action.check_value(test_fail_check_counter, threshold_type, threshold, value)
        self.assertEqual(result, 1)
        self.assertEqual(action.threshold_passed, False)

    def test_check_value_lower_fail_2(self):
        action = self.get_action_instance(self.config_good)
        action.threshold_passed = None
        test_fail_check_counter = 4
        threshold_type = 'lower'
        threshold = 100
        value = 100
        result = action.check_value(test_fail_check_counter, threshold_type, threshold, value)
        self.assertEqual(result, 5)
        self.assertEqual(action.threshold_passed, False)

    def test_check_value_lower_seccess(self):
        action = self.get_action_instance(self.config_good)
        action.threshold_passed = None
        test_fail_check_counter = 2
        threshold_type = 'lower'
        threshold = 100
        value = 120
        result = action.check_value(test_fail_check_counter, threshold_type, threshold, value)
        self.assertEqual(result, 0)
        self.assertEqual(action.threshold_passed, True)

    def test_check_value_upper_fail(self):
        action = self.get_action_instance(self.config_good)
        action.threshold_passed = None
        test_fail_check_counter = 0
        threshold_type = 'upper'
        threshold = 100
        value = 110
        result = action.check_value(test_fail_check_counter, threshold_type, threshold, value)
        self.assertEqual(result, 1)
        self.assertEqual(action.threshold_passed, False)

    def test_check_value_upper_fail_2(self):
        action = self.get_action_instance(self.config_good)
        action.threshold_passed = None
        test_fail_check_counter = 4
        threshold_type = 'upper'
        threshold = 100
        value = 100
        result = action.check_value(test_fail_check_counter, threshold_type, threshold, value)
        self.assertEqual(result, 5)
        self.assertEqual(action.threshold_passed, False)

    def test_check_value_upper_success(self):
        action = self.get_action_instance(self.config_good)
        action.threshold_passed = None
        test_fail_check_counter = 4
        threshold_type = 'upper'
        threshold = 100
        value = 90
        result = action.check_value(test_fail_check_counter, threshold_type, threshold, value)
        self.assertEqual(result, 0)
        self.assertEqual(action.threshold_passed, True)

    @mock.patch('threshold_check.time')
    def test_run_1(self, mock_time):
        action = self.get_action_instance(self.config_good)
        test_dict = {
            'check_value': True,
            'max_failures': 2,
            'rerun_flag': False,
            'rerun_limit': 5,
            'rerun_total': 4,
            'fail_check_counter': 1,
            'sleep_interval': 30,
            'threshold': 100,
            'threshold_type': 'lower',
            'value': 100
        }

        mock_time.sleep.return_value = 'Sleepy sleepy'

        expected_result = {
            'rerun_action': False,
            'fail_check_counter': 2,
            'threshold_passed': False
        }

        result = action.run(**test_dict)
        self.assertEqual(result, expected_result)

    @mock.patch('threshold_check.time')
    def test_run_2(self, mock_time):
        action = self.get_action_instance(self.config_good)
        test_dict = {
            'check_value': False,
            'max_failures': 3,
            'rerun_flag': False,
            'rerun_limit': 5,
            'rerun_total': 6,
            'fail_check_counter': 3,
            'sleep_interval': 30,
            'threshold': 100,
            'threshold_type': 'lower',
            'value': 100
        }

        mock_time.sleep.return_value = 'Sleepy sleepy'

        expected_result = {
            'rerun_action': False,
            'fail_check_counter': 3,
            'threshold_passed': None
        }

        result = action.run(**test_dict)
        self.assertEqual(result, expected_result)

    @mock.patch('threshold_check.time')
    def test_run_3(self, mock_time):
        action = self.get_action_instance(self.config_good)
        test_dict = {
            'check_value': True,
            'max_failures': 3,
            'rerun_flag': True,
            'rerun_limit': 5,
            'rerun_total': 4,
            'fail_check_counter': 2,
            'sleep_interval': 30,
            'threshold': 100,
            'threshold_type': 'lower',
            'value': 110
        }

        mock_time.sleep.return_value = 'Sleepy sleepy'

        expected_result = {
            'rerun_action': True,
            'fail_check_counter': 0,
            'threshold_passed': True
        }

        result = action.run(**test_dict)
        self.assertEqual(result, expected_result)
        mock_time.sleep.assert_called_with(30)

    @mock.patch('threshold_check.time')
    def test_run_4(self, mock_time):
        action = self.get_action_instance(self.config_good)
        test_dict = {
            'check_value': True,
            'max_failures': 3,
            'rerun_flag': False,
            'rerun_limit': 5,
            'rerun_total': 4,
            'fail_check_counter': 2,
            'sleep_interval': 30,
            'threshold': 100,
            'threshold_type': 'lower',
            'value': 110
        }

        mock_time.sleep.return_value = 'Sleepy sleepy'

        expected_result = {
            'rerun_action': False,
            'fail_check_counter': 0,
            'threshold_passed': True
        }

        result = action.run(**test_dict)
        self.assertEqual(result, expected_result)

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
from lib.base_action import BaseAction
import time


class ThresholdCheck(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(ThresholdCheck, self).__init__(config)

    def check_value(self, fail_check_counter, threshold_type, threshold, value):
        if threshold_type == 'lower':
            if value <= threshold:
                fail_check_counter += 1
                self.threshold_passed = False
            elif value > threshold:
                fail_check_counter = 0
                self.threshold_passed = True
        elif threshold_type == 'upper':
            if value >= threshold:
                fail_check_counter += 1
                self.threshold_passed = False
            elif value < threshold:
                fail_check_counter = 0
                self.threshold_passed = True
        else:
            raise ValueError("threshold_type must be lower or upper")

        return fail_check_counter

    def run(self,
            check_value,
            max_failures,
            rerun_flag,
            rerun_limit,
            rerun_total,
            fail_check_counter,
            sleep_interval,
            threshold,
            threshold_type,
            value):

        self.threshold_passed = None
        rerun_action = None
        action_recheck = False

        if check_value:
            fail_check_counter = self.check_value(fail_check_counter,
                                                  threshold_type,
                                                  threshold,
                                                  value)

        if fail_check_counter == max_failures:
            rerun_action = False
        elif rerun_total >= rerun_limit:
            rerun_action = False
        elif rerun_flag and (rerun_total < rerun_limit) and (fail_check_counter < max_failures):
            rerun_action = True
            action_recheck = True
        elif not rerun_flag and (rerun_total < rerun_limit) and (fail_check_counter < max_failures):
            rerun_action = False

        if action_recheck:
            time.sleep(sleep_interval)

        return {'rerun_action': rerun_action,
                'fail_check_counter': fail_check_counter,
                'threshold_passed': self.threshold_passed}

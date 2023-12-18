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
from st2common.runners.base_action import Action
from datetime import datetime


class ConvertTimestamp(Action):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(ConvertTimestamp, self).__init__(config)

    def convert_timestamp(self, timestamp):
        # remove timezone overlap
        trim_timezone = timestamp.split("+")[0]
        datetime_object = datetime.strptime(trim_timezone, '%Y-%m-%d %H:%M:%S.%f')

        return datetime_object

    def run(self, data_dict, end_timestamp, start_timestamp):
        start = self.convert_timestamp(start_timestamp)
        end = self.convert_timestamp(end_timestamp)

        duration = (end - start).total_seconds()

        data_dict['Start_Time'] = start.isoformat()[:-3]
        data_dict['Duration'] = duration

        return data_dict

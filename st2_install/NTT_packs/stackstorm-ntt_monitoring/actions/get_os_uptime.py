#!/usr/bin/env python
# Copyright 2021 NTT Data
# Developed by Nalinikant11.Mohanty@nttdata.com
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
# from st2common.runners.base_action import Action
from lib.base_action import BaseAction
import datetime
import os
import re
from st2client.client import Client
import sys
from dateutil.parser import parse

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../actions/lib')


class GetOsUptime(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(GetOsUptime, self).__init__(config)

    def get_uptime_secs(self, uptime_val):
        uptime_lst = str(uptime_val).split(',')
        secs = 0
        for item in uptime_lst:
            if 'year' in str(item).strip().lower():
                year = int(str(item).strip().split(' ')[0])
                year_secs = year * 365 * 24 * 60 * 60
                secs += year_secs
            elif 'week' in str(item).strip().lower():
                week = int(str(item).strip().split(' ')[0])
                week_secs = week * 7 * 24 * 60 * 60
                secs += week_secs
            elif 'hour' in str(item).strip().lower():
                hour = int(str(item).strip().split(' ')[0])
                hour_secs = hour * 60 * 60
                secs += hour_secs
            elif 'minute' in str(item).strip().lower():
                minute = int(str(item).strip().split(' ')[0])
                minute_secs = minute * 60
                secs += minute_secs

        return secs

    def find_uptime(self, cmd_input):
        try:
            pat = '\s+uptime is (.*)'
            search_pattern = r'{}'.format(pat)
            pattern = re.compile(search_pattern)
            uptime = pattern.findall(str(cmd_input))
            if uptime:
                uptime_val = uptime[0]
            else:
                uptime_val = None
            time_secs = self.get_uptime_secs(uptime_val)

            if time_secs > 1800:
                uptime_note = "Uptime in seconds is {}.".format(str(time_secs))
                result = (True, {"uptime": uptime_note})
            else:
                uptime_note = "Uptime in seconds is {}. This is below 30 minutes. Can't proceed further".format(str(time_secs))
                result = (False, {"uptime": uptime_note})
        except Exception as e:
            print(e)
            result = (False, {"uptime": "Can not find Uptime for the Device. Can not proceed further"})
        return result

    def run(self, cmd_input):
        return_value = self.find_uptime(cmd_input)
        return return_value

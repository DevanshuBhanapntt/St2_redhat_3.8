#!/usr/bin/env python
# Copyright 2021 NTT Data
# Developed by Arulanantham
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
from st2client.models.keyvalue import KeyValuePair  # pylint: disable=no-name-in-module
import ast

KEY_DICT = {
    'servicenow': 'servicenow.Pending_tasks_processing',
    'helix': 'helix.Pending_tasks_processing'
}


class itsmprocessingpendingtasksremove(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(itsmprocessingpendingtasksremove, self).__init__(config)

    def run(self, task_number):
        itsm_tool = self.config['itsm_tool']
        inc_st2_key = KEY_DICT[itsm_tool]
        st2_client = self.st2_client_get()
        processing_pending_tasks = st2_client.keys.get_by_name(inc_st2_key)

        processing_pending_tasks = [] if processing_pending_tasks is None else ast.literal_eval(processing_pending_tasks.value)

        if task_number in processing_pending_tasks:
            processing_pending_tasks.remove(task_number)
            incs_str = str(processing_pending_tasks)
            kvp = KeyValuePair(name=inc_st2_key, value=incs_str)
            st2_client.keys.update(kvp)

            result = {
                'key': inc_st2_key,
                'value': incs_str
            }
        else:
            result = "The given tasks ID was not found in the list"

        return result

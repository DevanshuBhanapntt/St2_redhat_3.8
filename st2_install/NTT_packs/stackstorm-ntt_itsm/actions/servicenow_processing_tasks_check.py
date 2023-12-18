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


class servicenowprocessingtaskscheck(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(servicenowprocessingtaskscheck, self).__init__(config)

    def run(self, inc_st2_key):
        st2_client = self.st2_client_get()
        processing_tasks = st2_client.keys.get_by_name(inc_st2_key)

        processing_tasks = [] if processing_tasks is None else ast.literal_eval(processing_tasks.value)

        for tsk_number in processing_tasks[:]:
            endpoint = '/api/now/table/sc_task?sysparm_query=number=' + tsk_number
            tasks = self.sn_api_call('GET', endpoint)

            if len(tasks) == 0:
                print('No tasks found with ID: ' + tsk_number)
                processing_tasks.remove(tsk_number)
                continue
            elif len(tasks) > 1:
                raise Exception('Multiple tasks found with ID: ' + tsk_number)

            # tasks state 3  is closed, 4 is canceled, 5 is skipped and 7 is no longer needed
            # https://support.servicenow.com/kb?id=kb_article_view&sysparm_article=KB0564465
            if int(tasks[0]['state']) > 2:
                print('Removing tasks: ' + tsk_number + ' as it is no longer open')
                processing_tasks.remove(tsk_number)

        incs_str = str(processing_tasks)
        kvp = KeyValuePair(name=inc_st2_key, value=incs_str)
        st2_client.keys.update(kvp)

        return processing_tasks

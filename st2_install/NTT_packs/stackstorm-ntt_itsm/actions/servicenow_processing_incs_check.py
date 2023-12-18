#!/usr/bin/env python
# Copyright 2021 Encore Technologies
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


class ServicenowProcessingIncsCheck(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(ServicenowProcessingIncsCheck, self).__init__(config)

    def run(self, inc_st2_key):
        st2_client = self.st2_client_get()
        processing_incs = st2_client.keys.get_by_name(inc_st2_key)

        processing_incs = [] if processing_incs is None else ast.literal_eval(processing_incs.value)

        for inc_id in processing_incs[:]:
            endpoint = '/api/now/table/incident?sysparm_query=number=' + inc_id
            inc = self.sn_api_call('GET', endpoint)

            if len(inc) == 0:
                print('No incident found with ID: ' + inc_id)
                processing_incs.remove(inc_id)
                continue
            elif len(inc) > 1:
                raise Exception('Multiple incidents found with ID: ' + inc_id)

            # Incidents state 6 is resolved, 7 is closed, and 8 is canceled
            # https://support.servicenow.com/kb?id=kb_article_view&sysparm_article=KB0564465
            if int(inc[0]['state']) > 5:
                print('Removing incident: ' + inc_id + ' as it is no longer open')
                processing_incs.remove(inc_id)

        incs_str = str(processing_incs)
        kvp = KeyValuePair(name=inc_st2_key, value=incs_str)
        st2_client.keys.update(kvp)

        return processing_incs

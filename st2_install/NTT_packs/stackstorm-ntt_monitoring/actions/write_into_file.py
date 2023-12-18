#!/usr/bin/env python
# Copyright 2021 NTT Data
# Developed by Arulanantham.p@nttdata.com
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

import datetime
import os
import sys
import json

from st2client.client import Client
from lib.base_action import BaseAction

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../actions/lib')


class WriteIntoFile(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(WriteIntoFile, self).__init__(config)

    def write_into_file(self, inc_number, itsm_data, job_id):
        try:
            if str(inc_number) and str(itsm_data):
                itsm_lst_data = str(itsm_data).strip().split("|")
                itsm_dict_data = {}
                for pair in itsm_lst_data:
                    key = str(pair).split(":")[0]
                    val = str(pair).split(":")[1]
                    if str(key) == "Status":
                        if str(val).lower() == "false":
                            val = "Success"
                        elif str(val).lower() == "true":
                            val = "Failure"

                    itsm_dict_data[key] = val

                itsm_dict_data["Job ID"] = job_id

                if not os.path.isdir("/opt/stackstorm/execution_records"):
                    os.mkdir("/opt/stackstorm/execution_records")

                file_name = str(inc_number) + "_" + str(datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')) + ".json"
                file_path = "/opt/stackstorm/execution_records/" + str(file_name)

                with open(file_path, "w") as fo:
                    json.dump(itsm_dict_data, fo)

                result = (True, {"insert_to_file": True, "record_path": str(file_path)})
            else:
                result = (False, {"insert_to_file": False, "record_path": None})
        except Exception as e:
            print(e)
            result = (False, {"insert_to_file": False, "record_path": None})

        return result

    def run(self, inc_number, itsm_data, job_id):
        return_value = self.write_into_file(inc_number, itsm_data, job_id)
        return return_value

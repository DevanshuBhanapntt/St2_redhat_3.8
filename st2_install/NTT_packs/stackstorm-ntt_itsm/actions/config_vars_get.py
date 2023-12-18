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


class ConfigVarsGet(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(ConfigVarsGet, self).__init__(config)

    def run(self):
        # Config validation is handled in the base_action where it expects an
        # itsm_tool parameter as well as credentials fior the given tool
        if self.config:
            return self.config
        else:
            raise Exception("Could not get config for ntt_itsm pack!")

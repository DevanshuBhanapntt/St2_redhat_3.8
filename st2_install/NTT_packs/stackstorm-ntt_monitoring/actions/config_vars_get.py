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


class ConfigVarsGet(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(ConfigVarsGet, self).__init__(config)

    def check_overrides(self, workflow_overrides, config_dict):
        for key in workflow_overrides:
            value = workflow_overrides[key]
            if value:
                if 'winrm' in key or 'ssh' in key:
                    config_dict['connections'][key] = value
                else:
                    config_dict[key] = value

        return config_dict

    def run(self, customer_abbr, workflow_overrides):
        default = {}
        customer = {}
        # Get the default variables first
        if self.config['customers'].get('default'):
            default = self.config['customers'].get('default')

        # Check if there are any customer specfic variables
        if customer_abbr and self.config['customers'].get(customer_abbr):
            customer = self.config['customers'].get(customer_abbr)

        # Fail if no default or customer variables are found in the config
        if default == {} and customer == {}:
            raise Exception("No default or customer configurations found!")

        # Overwrite default variables with customer specific ones (if any)
        if 'connections' in customer and 'connections' in default:
            # Add any default connections that are missing from the customer section
            for key, value in default['connections'].items():
                if key not in customer['connections']:
                    customer['connections'][key] = value

        default.update(customer)
        return_dict = self.check_overrides(workflow_overrides, default)

        return return_dict

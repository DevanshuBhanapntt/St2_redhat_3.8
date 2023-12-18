#!/usr/bin/env python
# Copyright 2019 Ntt Data
# Developed by Arulanantham.p@nttdata.com
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
from st2client.client import Client
import ast
from st2client.models.keyvalue import KeyValuePair
import socket
import os
import sys
import json


class update_kv_dict(Action):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(update_kv_dict, self).__init__(config)

    def run(self, st2_key_name,Find_key_field,update_key_value,update_key_value_oper):
        self.st2_fqdn = socket.getfqdn()
        st2_url = "https://{}/".format(self.st2_fqdn)
        self.st2_client = Client(base_url=st2_url)  
        result = "0"
        # reading the values from Stackstorm Keystore
        res_key_store_value = self.st2_client.keys.get_by_name(st2_key_name)        
        # Check if the variable have the value or empty
        if res_key_store_value:
            # reading the value from value part        
            res_key_store_value =res_key_store_value.value           
            # Replace the single quotes to double quotes
            res_key_store_value = res_key_store_value.replace("'","\"")
            # convert string to dict
            convertedDict = json.loads(res_key_store_value) 
            Find_key_field_value = convertedDict.get(Find_key_field, 0)
            # convert the num into string
            #Find_key_field_valuestr = str(Find_key_field_value)
            #print(Find_key_field_valuestr)   
            #print(len(Find_key_field_valuestr))            
            if 'add' in update_key_value_oper:
                #Adding the values
                convertedDict[Find_key_field] = convertedDict.get(Find_key_field, 0) + update_key_value
            elif 'subtract' in update_key_value_oper:
                # Subtract the values
                convertedDict[Find_key_field] = convertedDict.get(Find_key_field, 0) - update_key_value
            elif (('remove' in update_key_value_oper) and (Find_key_field_value > 0)):
                # remove the value from key store
                del convertedDict[Find_key_field]
            
            if ('add' in update_key_value_oper or 'subtract' in update_key_value_oper or 'remove' in update_key_value_oper):
               # Convert string to Dictionary 
               result = json.dumps(convertedDict)
               # making the kayvalue pair
               kvp = KeyValuePair(name=st2_key_name, value=result)
               # updating the Stackstorm keystore
               self.st2_client.keys.update(kvp)
            else:
                return convertedDict.get(Find_key_field, 0)
                      
        elif 'add' in update_key_value_oper:
            # Prepare the dictionary
            Dict = {Find_key_field: update_key_value}
            # Convert string to Dictionary 
            result = json.dumps(Dict)
            # making the kayvalue pair
            kvp = KeyValuePair(name=st2_key_name, value=result)
            # updating the Stackstorm keystore
            self.st2_client.keys.update(kvp)
                       
                        
        return result

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
#from st2common.runners.base_action import Action
from lib.base_action import BaseAction
from st2client.models.keyvalue import KeyValuePair  # pylint: disable=no-name-in-module
import requests
import ast
import socket
import os
from st2client.client import Client
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../actions/lib')
import base_action
import json
import datetime as dt
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

__all__ = [
    'ServiceNowIncidentSensor'
]

class ITSMIncidentRecurrence(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(ITSMIncidentRecurrence, self).__init__(config)
          

    def servicenow_recurrence_check(self, sn_username, sn_password, sn_url, inc_id, rec_ds_key_name, company_name, ci_name, short_desc, long_desc):
        
        self.st2_fqdn = socket.getfqdn()
        st2_url = "https://{}/".format(self.st2_fqdn)
        self.st2_client = Client(base_url=st2_url)  
        # reading the values from Stackstorm Keystore
        res_key_store_value = self.st2_client.keys.get_by_name(rec_ds_key_name)
        # reading the value from value part        
        res_key_store_value =res_key_store_value.value           
        # Replace the single quotes to double quotes
        res_key_store_value = res_key_store_value.replace("'","\"")
        # convert string to dict
        convertedDict = json.loads(res_key_store_value)         
        #print(str(convertedDict))
        
        Found_Recurrence = False
        #Header details
        servicenow_headers = {'Content-type': 'application/json','Accept': 'application/json'}
        
        # define the conditions
        endpoint = '/api/now/table/incident?sysparm_query=number!='+inc_id        
        if company_name:
           endpoint = endpoint+'^company.nameIN'+company_name
        if ci_name:
            endpoint = endpoint+'^cmdb_ci.name='+ci_name
        if short_desc:
            endpoint = endpoint+'^short_descriptionLIKE'+short_desc
        if long_desc:
            endpoint = endpoint+'^descriptionLIKE'+long_desc
            
        for key in convertedDict:
            endpointdays = ''
            # define the aging conditions
            endpointdays = '^opened_atBETWEENjavascript:gs.daysAgoStart('+str(key)+')@javascript:gs.daysAgoEnd(0)'
            endpointdays = endpoint + endpointdays
            # adding the Fields details
            endpointdays = endpointdays + '&sysparm_fields=number'  
            # define the url & end point details            
            sn_inc_url = "https://{0}{1}".format(sn_url,endpointdays)   
            # connect the servicenow            
            sn_result = requests.request('GET',
                                     sn_inc_url,
                                     auth=(sn_username, sn_password),
                                     headers=servicenow_headers,verify=False)
            # getting the result
            sn_incidents = sn_result.json()['result']
            rec_threshold = convertedDict[key]
            if len(sn_incidents) > rec_threshold :
                incidnet_det = ''
                Found_Recurrence = True
                # Prepaing the Recurrence incident number details 
                for inc in sn_incidents:
                     if (len(str(incidnet_det)) > 0):
                        incidnet_det = incidnet_det + ','+ str(inc['number'])
                     else:
                        incidnet_det = str(inc['number'])
                # preparing the result format
                result = {
                'Found_Recurrence': Found_Recurrence,
                'Found_Recurrence_Inc_Cnt': len(sn_incidents),
                'value': "Automation found " + str(len(sn_incidents))+" recurrence incidents in the last "+ str(key)+" Days.Refer the below incidents ."+ str(incidnet_det)
                }
                return result
        # if none of the incidnet found, it's retrun as false.   
        result = {
                'Found_Recurrence': Found_Recurrence,
                'Found_Recurrence_Inc_Cnt': 0,
                'value': "Automation could not find any recurrenc incidents."
                }    
        return result
    def Helix_recurrence_check(self, helix_username, helix_password, helix_url, inc_id, rec_ds_key_name, company_name, ci_name, short_desc, long_desc):
        # = %3D
        # ' %27
        # space %20
        # " %22
        # (  %28
        # , %2C
        # ) %29
        # % %25
        # : %3A
        # use this URL to encode the details  https://www.w3schools.com/html/html_urlencode.asp
        
        self.st2_fqdn = socket.getfqdn()
        st2_url = "https://{}/".format(self.st2_fqdn)
        self.st2_client = Client(base_url=st2_url)  
        # reading the values from Stackstorm Keystore
        res_key_store_value = self.st2_client.keys.get_by_name(rec_ds_key_name)
        # reading the value from value part        
        res_key_store_value =res_key_store_value.value           
        # Replace the single quotes to double quotes
        res_key_store_value = res_key_store_value.replace("'","\"")
        # convert string to dict
        convertedDict = json.loads(res_key_store_value)         
        #print(str(convertedDict))
        
        Found_Recurrence = False
        
        headers = {'Content-type': 'application/x-www-form-urlencoded' }      
        data = {"grant_type" : "password",
        "username" : helix_username,
        "password" : helix_password}
        
        endpoint = '/api/jwt/login'
        helix_inc_url = "https://{0}{1}".format(helix_url,endpoint)
        response = requests.post(helix_inc_url, headers=headers, data=data, verify=True) 
        helix_token =response.text
        headers = {'Content-type': 'application/json' ,'Authorization': 'AR-JWT '+str(helix_token),'Accept': 'application/json' }        
        # define the API for getting all the fields for incident
        endpoint = '/api/arsys/v1/entry/HPD:IncidentInterface?'        
        # and Company='xxxxxxx'           
        endpoint +='q=%27Company%27%3D%22'+company_name+'%22' 
        
        # and (
        endpoint +='%20AND%28'
        
        if ci_name:
            endpoint += '%27HPD_CI%27LIKE%22%25'+ci_name+'%25%22'
        if short_desc:
            endpoint += '%20AND%20'
            endpoint += '%27Description%27LIKE%22%25'+short_desc+'%25%22'
        if long_desc:
            endpoint += '%20AND%20'
            endpoint += '%27Detailed%20Decription%27LIKE%22%25'+long_desc+'%25%22'
               
               
        for key in convertedDict:
            endpointdays = ''
            # define the aging conditions
            pasttime = dt.date.today() - dt.timedelta(days=int(key))  
            #pastime_recdays = dt.datetime.strftime(pasttime, "%Y-%m-%dT%H:%M:%S.%f")
            pastime_recdays = dt.datetime.strftime(pasttime, "%Y-%m-%d")
            endpointdays = '%20AND%20%27Submit%20Date%27%3E%22'+pastime_recdays+'%22'
            endpointdays = endpoint + endpointdays
            endpointdays += '%20%29'   
            # adding the Fields details
            endpointdays = endpointdays + '&fields=values(Incident Number)'           
            helix_inc_url = "https://{0}{1}".format(helix_url,endpointdays)
            response = requests.get(helix_inc_url, headers=headers,verify=True)
            # get the API Response
            data = response.text                         
            # converting dictionary
            value = json.loads(data)            
            rec_threshold = convertedDict[key]
            Found_Recurrence_Inc_Cnt = 0
            Found_Recurrence = False
            res_length = 0
            try:
              if not value:
                res_length = 0
              else:
                res_length = 1
                sn_incidents = value["entries"]
              #res_length = len(value["entries"])
            except Exception as e:
                return "arul "+ str(e)
            #return res_length
            if res_length > 0 :
                if len(sn_incidents) > rec_threshold :
                    incidnet_det = ''
                    Found_Recurrence = True                 
                    # Prepaing the Recurrence incident number details                                
                    for inc in sn_incidents:                     
                        if (len(str(incidnet_det)) > 0):
                            incidnet_det = incidnet_det + ','+ str(inc["values"]["Incident Number"])
                        else:
                            incidnet_det = str(inc["values"]["Incident Number"])
                    # preparing the result format
                    result = {
                    'Found_Recurrence': Found_Recurrence,
                    'Found_Recurrence_Inc_Cnt': len(sn_incidents),
                    'value': "Automation found " + str(len(sn_incidents))+" recurrence incidents in the last "+ str(key)+" Days.Refer the below incidents ."+ str(incidnet_det)
                    }
                    # loggout the session
                    headers = {"Authorization": helix_token}
                    endpoint = '/api/jwt/logout'
                    helix_inc_logout = "https://{0}{1}".format(helix_url,endpoint)
                    response_logout = requests.post(helix_inc_logout, headers=headers,verify=True)         
                    return  result 
                
        # if none of the incidnet found, it's retrun as false.   
        result = {
          'Found_Recurrence': Found_Recurrence,
          'Found_Recurrence_Inc_Cnt': 0,          
          'value': "Automation could not find any recurrenc incidents."
        }    
        return result
    def run(self, inc_id, rec_ds_key_name, company_name, ci_name, short_desc, long_desc):
    
        itsm_tool = self.config['itsm_tool']
        sn_username = self.config['servicenow']['username']
        sn_password = self.config['servicenow']['password']
        sn_url = self.config['servicenow']['url']
        return_value = False
        if itsm_tool == 'servicenow':
            return_value = self.servicenow_recurrence_check(sn_username, sn_password, sn_url, inc_id, rec_ds_key_name, company_name, ci_name, short_desc, long_desc)
        elif itsm_tool == 'helix':
            
            helix_username = self.config['helix']['username']
            helix_password = self.config['helix']['password']
            helix_url = self.config['helix']['url'] 
            Company_name = self.config['helix']['Company_name'] 
            return_value = self.Helix_recurrence_check(helix_username, helix_password, helix_url, inc_id, rec_ds_key_name, company_name, ci_name, short_desc, long_desc)
            #Found_Recurrence = False
            #result = {
            #    'Found_Recurrence': Found_Recurrence,
            #    'Found_Recurrence_Inc_Cnt': 0,
            #    'value': "Automation could not find any recurrenc incidents."
            #    } 
            return return_value
        else:
            error_message = 'Could not get ITSM info please check the config file and try again'
            return_value = (False, {'error_message': error_message})

        return return_value

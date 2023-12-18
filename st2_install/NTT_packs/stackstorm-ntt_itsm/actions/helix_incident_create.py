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
import datetime as dt 
import requests
import json
import os

class helixincidentcreate(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(helixincidentcreate, self).__init__(config)
      
    def helix_setup(self):
        self.helix_username = self.config['helix']['username']
        self.helix_password = self.config['helix']['password']
        self.helix_url = self.config['helix']['url']
        self.helix_Automation_Login_ID = self.config['helix']['Automation_Login_ID']
        self.helix_Automation_Login_Name = self.config['helix']['Automation_Login_Name']
        self.Status_Reason = self.config['helix']['Status_Reason']
        self.Resolution_Category = self.config['helix']['Resolution_Category']
        self.Resolution_Category_Tier_2 = self.config['helix']['Resolution_Category_Tier_2']
        self.Resolution_Category_Tier_3 = self.config['helix']['Resolution_Category_Tier_3']
        self.Resolution_Method = self.config['helix']['Resolution_Method']
        self.Generic_Categorization_Tier_1 = self.config['helix']['Generic_Categorization_Tier_1']
                        
    def get_token_Helix(self): 

        headers = {'Content-type': 'application/x-www-form-urlencoded' }      
        data = {"grant_type" : "password",
        "username" : self.helix_username,
        "password" : self.helix_password}
        
        endpoint = '/api/jwt/login'
        helix_inc_url = "https://{0}{1}".format(self.helix_url,endpoint)
        response = requests.post(helix_inc_url, headers=headers, data=data, verify=True)  
        return response.text   
    def helix_inc_create(self, Company, CI_Name, First_Name, Last_Name, Impact, Reported_Source, Urgency, Service_Type, Description, Detailed_Decription, Categorization_Tier_1, Categorization_Tier_2, Categorization_Tier_3, Product_Categorization_Tier_1 , Product_Categorization_Tier_2, Product_Categorization_Tier_3, Product_Name, Assigned_Support_Company, Assigned_Support_Organization, Assigned_Group):
        notes_with_newline =''
        self.helix_setup()
        helix_token =''
        helix_token = self.get_token_Helix()
        # define the API for getting all the fields for incident
        endpoint = '/api/arsys/v1/entry/HPD:IncidentInterface_Create?fields=values(Incident Number)'
        if len(helix_token) > 0 : 
           
          headers = {'Authorization': 'AR-JWT '+str(helix_token),'Accept': 'application/json','Content-type': 'application/json'}
           
          det_desc =[]
          det_desc.append(Detailed_Decription)
          det_desc =str(Detailed_Decription)   
          content = '{  '
          content += '"values": { '
          content += '"z1D_Action" : "CREATE",'
          content += '"Phone_Number" : "###", '
          content += '"Status" : "1",'
          content += '"CI Name" : "'+CI_Name +'",'
          content += '"First_Name" : "'+First_Name +'",'
          content += '"Last_Name" : "'+Last_Name +'",'
          content += '"Company" : "'+Company +'",'
          content += '"Impact" : "'+Impact +'",'
          content += '"Reported Source" : "'+Reported_Source +'",'
          content += '"Urgency" : "'+Urgency +'",'
          content += '"Service_Type" : "'+Service_Type +'",'
          content += '"Description" : "'+Description +'",'
          content += '"Detailed_Decription" : "'+det_desc+'",'  
          content += '"Categorization Tier 1" : "'+Categorization_Tier_1+'",'  
          content += '"Categorization Tier 2" : "'+Categorization_Tier_2+'",' 
          content += '"Categorization Tier 3" : "'+Categorization_Tier_3+'",' 
          content += '"Product Categorization Tier 1" : "'+Product_Categorization_Tier_1+'",'
          content += '"Product Categorization Tier 2" : "'+Product_Categorization_Tier_2+'",'
          content += '"Product Categorization Tier 3" : "'+Product_Categorization_Tier_3+'",'
          content += '"Product Name" : "'+Product_Name+'",'
          content += '"Assigned Support Company" : "'+Assigned_Support_Company+'",'
          content += '"Assigned Support Organization" : "'+Assigned_Support_Organization+'",'
          content += '"Assigned Group" : "'+Assigned_Group+'"'         
          content += ' } '
          content += ' } '       
                      
          helix_inc_update = "https://{0}{1}".format(self.helix_url,endpoint)
          response_update = requests.post(helix_inc_update, headers=headers, data=content, verify=True)
          
          # get the API Response
          data = response_update.text
          # converting dictionary
          value = json.loads(data)          
          incident_No =  value["values"]["Incident Number"]              
          # loggout the session
          headers = {"Authorization": helix_token}
          endpoint = '/api/jwt/logout'
          helix_inc_logout = "https://{0}{1}".format(self.helix_url,endpoint)
          response_logout = requests.post(helix_inc_logout, headers=headers,verify=True)
                       
          return {"Response":response_update.text,"incident_No":incident_No }
           
    def run(self, Company, CI_Name, First_Name, Last_Name, Impact, Reported_Source, Urgency, Service_Type, Description, Detailed_Decription, Categorization_Tier_1, Categorization_Tier_2, Categorization_Tier_3, Product_Categorization_Tier_1 , Product_Categorization_Tier_2, Product_Categorization_Tier_3, Product_Name,  Assigned_Support_Company, Assigned_Support_Organization, Assigned_Group):
        
        return_value = self.helix_inc_create(Company, CI_Name, First_Name, Last_Name, Impact, Reported_Source, Urgency, Service_Type, Description, Detailed_Decription, Categorization_Tier_1, Categorization_Tier_2, Categorization_Tier_3, Product_Categorization_Tier_1 , Product_Categorization_Tier_2, Product_Categorization_Tier_3, Product_Name, Assigned_Support_Company, Assigned_Support_Organization, Assigned_Group)
        return return_value

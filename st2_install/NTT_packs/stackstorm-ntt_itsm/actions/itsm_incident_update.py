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
from datetime import timezone
from st2client.client import Client
import socket
import pytz
import requests
import json
import os
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import time

class ITSMIncidentUpdate(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(ITSMIncidentUpdate, self).__init__(config)

    def servicenow_update_REST_API(self, close, escalate, inc_id, notes, work_in_progress, pending, pending_mins, priorityupgrade, u_reason_for_priority_upgrade, priority, urgency, impact):
        endpoint = '/api/now/table/incident/' + inc_id

        if work_in_progress:
            payload = {
                'assigned_to': 'Automation Service',
                'incident_state': '-3',
                'state': '-3'
            }
            if notes:
                payload['work_notes'] = notes
        elif close:
            payload = {
                'incident_state': '7',
                'state': '7',
                'close_code': 'Solved Remotely (Permanently)',
                'work_notes':notes
            }
            if notes:
                payload['close_notes'] = notes
            else:
                raise "notes is a required field when closing an incident!"
        elif escalate:
            payload = {
                'assigned_to': '',
                'incident_state': '2',
                'state': '2'
            }
            if notes:
                payload['work_notes'] = notes
        elif pending:
            pending_mins = pending_mins +15
            nowtime = dt.datetime.now() + dt.timedelta(minutes = pending_mins)
            now_plus_pendingmins = dt.datetime.strftime(nowtime, "%Y-%m-%d %H:%M:%S")
            payload = {
                'incident_state': '-5',
                'u_state_reason': 'Monitoring',
                'u_pending_end_date': now_plus_pendingmins,
                'state': '-5'
            }
            if notes:
                payload['work_notes'] = notes
        elif priorityupgrade:
            payload = {
                'u_reason_for_priority_upgrade': u_reason_for_priority_upgrade,
                'priority': priority,
                'urgency': urgency,
                'impact': impact
            }
            if notes:
                payload['work_notes'] = notes
        elif len(notes) > 0:
            payload = {
                'work_notes': notes
            }
        else:
            raise Exception("One of close, escalate,pending,priorityupgrade or work_in_progress must be set to True!")

        inc = self.sn_api_call('PATCH', endpoint, payload=payload)

        return inc

    def servicenow_get_incident_status(self, inc_sys_id):
        itsm_tool = self.config['itsm_tool']
        sn_username = self.config['servicenow']['username']
        sn_password = self.config['servicenow']['password']
        sn_url = self.config['servicenow']['url']
        self.st2_fqdn = socket.getfqdn()
        st2_url = "https://{}/".format(self.st2_fqdn)
        self.st2_client = Client(base_url=st2_url)
        inc_status = ''
        inc_assigned_to = ''
        sn_task = []

        #Header details
        servicenow_headers = {'Content-type': 'application/json','Accept': 'application/json'}

        # define the conditions
        endpoint = '/api/now/table/incident?sysparm_query=sys_id='+inc_sys_id
        # define the url & end point details
        sn_inc_url = "https://{0}{1}".format(sn_url,endpoint)
        # connect the servicenow
        sn_result = requests.request('GET',
                                 sn_inc_url,
                                 auth=(sn_username, sn_password),
                                 headers=servicenow_headers,verify=False)
        # getting the result
        sn_task = sn_result.json()['result']
        #sn_task = sn_result
        #print(sn_task)
        inc_status = sn_task[0]['incident_state']
        #print(inc_status)
        inc_assigned_to_temp = sn_task[0]['assigned_to']
        if 'value' in inc_assigned_to_temp:
            inc_assigned_to = sn_task[0]['assigned_to']['value']
        else:
            inc_assigned_to = ''
        return inc_status,inc_assigned_to

    def servicenow_update_scripted_API(self, inc_id, work_in_progress, pending, pending_mins, close, escalate, notes):
        automation_service_sys='c7df48c44fb1aa8055699efd0210c74e'
        reassign_notes='Automation will not change the status of the incident. The incident is either not in the proper status for escalation/resolution or is currently not assigned to Automation.'
        payload = ''
        inc = ''
        endpoint = ''
        endpoint_notes = ''
        payload_notes = ''
        inc_notes = ''
        inc_status, inc_assigned_to = self.servicenow_get_incident_status(inc_id)
        if work_in_progress:
            endpoint = '/api/ntt11/incident_automation_stackstorm/MoveFromOpenorPendingToInProgress'
            payload = {
                'sys_id': inc_id
            }
        elif pending:
            endpoint = '/api/ntt11/incident_automation_stackstorm/MoveFromInProgressToPending'
            payload = {
                'sys_id': inc_id ,
                "u_pending_end_date":pending_mins+15
            }
        elif close:
            # Notes is mandatory field for ticket closure.
            if inc_assigned_to == automation_service_sys:
                endpoint = '/api/ntt11/incident_automation_stackstorm/MoveFromInProgressToResolved'
                if ((notes != None) and (len(str(notes)) > 0)):
                    payload = {
                        'sys_id': inc_id ,
                        'work_notes': notes
                    }
                else:
                    payload = {
                        'sys_id': inc_id ,
                        'work_notes': 'Automation is resolving the ticket.'
                    }
            elif inc_assigned_to != automation_service_sys and inc_status != 2:
                endpoint_notes = '/api/ntt11/incident_automation_stackstorm/UpdateWorkNotes'
                if ((notes != None) and (len(str(notes)) > 0)):
                    notes = reassign_notes+'\n'+notes
                else:
                    notes = reassign_notes
                payload_notes = {
                        'sys_id': inc_id ,
                        'work_notes': notes
                    }
                inc_notes = self.sn_api_call('POST', endpoint_notes, payload=payload_notes)                    
        elif escalate:
            endpoint = '/api/ntt11/incident_automation_stackstorm/MoveFromInProgressorPendingToOpen'
            payload = {
                'sys_id': inc_id
            }
        else:
            if ((notes != None) and (len(str(notes)) > 0)):
               do_nothing =''
            else:
                raise Exception("One of close, escalate,pending, work_in_progress or notes must be set to values")
                
        # If seperate worknte availale for open to inprogress and inprogress to escalate. Status change should happen first and then the worknote update.
        if (work_in_progress or pending):
          inc = self.sn_api_call('POST', endpoint, payload=payload)

        if work_in_progress:
            inc_status,inc_assigned_to = self.servicenow_get_incident_status(inc_id)
            
        inc_status = inc_status.strip()

        if (work_in_progress or pending or escalate):
            endpoint_notes = '/api/ntt11/incident_automation_stackstorm/UpdateWorkNotes'
            if inc_assigned_to == automation_service_sys and ((notes != None) and (len(str(notes)) > 0)):
                payload_notes = {
                    'sys_id': inc_id ,
                    'work_notes': notes
                }
                inc_notes = self.sn_api_call('POST', endpoint_notes, payload=payload_notes)
            elif inc_assigned_to != automation_service_sys and ((notes != None) and (len(str(notes)) > 0)) and inc_status != '2':
                work_note_update = reassign_notes+'\n'+notes
                payload_notes = {
                    'sys_id': inc_id ,
                    'work_notes': work_note_update
                }
                inc_notes = self.sn_api_call('POST', endpoint_notes, payload=payload_notes)
            elif inc_assigned_to != automation_service_sys and ((notes == None) or (len(str(notes)) <= 0)) and inc_status != '2':
                payload_notes = {
                    'sys_id': inc_id ,
                    'work_notes': reassign_notes
                }
                inc_notes = self.sn_api_call('POST', endpoint_notes, payload=payload_notes)

        #only worknote update
        if (not work_in_progress and not close and not pending and not escalate):
            if ((notes != None) and (len(str(notes)) > 0)) and inc_status != '2':
                endpoint_notes = '/api/ntt11/incident_automation_stackstorm/UpdateWorkNotes'
                payload_notes = {
                    'sys_id': inc_id ,
                    'work_notes': notes
                }
                inc_notes = self.sn_api_call('POST', endpoint_notes, payload=payload_notes)

        if (close or escalate) and (inc_assigned_to == automation_service_sys):
            inc = self.sn_api_call('POST', endpoint, payload=payload)

        if (work_in_progress or  pending or  close or escalate):
            if ((notes != None) and (len(str(notes)) > 0)):
               return {'Payload': payload ,'API':endpoint, 'Return':inc,'Payload_notes': payload_notes ,'API_notes':endpoint_notes, 'Return_notes':inc_notes}
            else:
               return {'Payload': payload ,'API':endpoint, 'Return':inc}
        elif len(str(notes)) > 0:
            return {'Payload_notes': payload_notes ,'API_notes':endpoint_notes, 'Return_notes':inc_notes}

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
    def helix_update(self, close, escalate, inc_id, notes, work_in_progress, pending, pending_mins, priorityupgrade, u_reason_for_priority_upgrade, priority, urgency, impact):
        if notes:
            notes = notes.replace(u"\u2018", "").replace(u"\u2019", "")
            notes = notes.replace("'","")
            notes = notes.replace('"','')
        status_change="false"
        note_update="false"
        notes_with_newline =''
        self.helix_setup()
        helix_token =''
        helix_token = self.get_token_Helix()
        # define the API for getting all the fields for incident
        endpoint = '/api/arsys/v1/entry/HPD:Help Desk/'+inc_id
        if len(helix_token) > 0 :

           headers = {'Authorization': 'AR-JWT '+str(helix_token),'Accept': 'application/json','Content-type': 'application/json'}

           if work_in_progress:
             status_change="true"
             content = '{  '
             content += '"values": { '
             content += '"Assignee Login ID" :  "'+self.helix_Automation_Login_ID+'",'
             content += '"Assignee" : "'+self.helix_Automation_Login_Name +'",'
             content += '"Status" : "In Progress",'
             content += '"z1D_Activity_Type" : "8000",'
             content += '"z1D_View_Access" : "1", '
             content += '"z1D_Secure_Log" : "0", '
             content += '"z1D_Summary" : "Automation Work Info update", '
             if len(str(notes)) <= 0 or notes == None:
                 content += '"z1D_Details" : "Incident assigned to Automation(Stackstorm).  Work in progress."'
             else:
                 worknotes =[]
                 worknotes.append(notes)
                 worknotes =str(worknotes)
                 content += '"z1D_Details" : "'+worknotes+'"'
             content += ' } '
             content += ' } '
           elif close:
             status_change="true"
             content = '{  '
             content += '"values": { '
             content += '"Status" : "Resolved",'
             content += '"z1D_Activity_Type" : "8000",'
             content += '"z1D_View_Access" : "1", '
             content += '"z1D_Secure_Log" : "0", '
             content += '"z1D_Summary" : "Automation resolution entry", '
             if len(str(notes)) <= 0 or notes == None:
                 content += '"z1D_Details" : "Automation is resolving the incident.",'
             else:
                 worknotes =[]
                 worknotes.append(notes)
                 worknotes =str(worknotes)
                 content += '"z1D_Details" : "'+worknotes+'",'
             content += '"Resolution" : "Automation is resolving the incident.see Work Log",'
             content += '"Status_Reason" : "'+self.Status_Reason+'",'
             content += '"Resolution Category" : "'+self.Resolution_Category+'",'
             content += '"Resolution Category Tier 2" : "'+self.Resolution_Category_Tier_2+'",'
             content += '"Resolution Category Tier 3" : "'+self.Resolution_Category_Tier_3+'",'
             content += '"Resolution Method" : "'+self.Resolution_Method+'",'
             content += '"Generic Categorization Tier 1" : "'+self.Generic_Categorization_Tier_1+'"'
             content += ' } '
             content += ' } '
           elif escalate:
             endPoint_desc = '/api/arsys/v1/entry/HPD:IncidentInterface?q=%27Entry+ID%27%3D%22'+inc_id+'%22'
             helix_inc_update = "https://{0}{1}".format(self.helix_url,endPoint_desc)
             response = requests.get(helix_inc_update, headers=headers,verify=True)
             data = response.text
             value = json.loads(data)
             detailed_description = value["entries"][0]["values"]["Detailed Decription"]
             detailed_description = detailed_description.replace('\n', ' ')
             status_change="true"
             content = '{  '
             content += '"values": { '
             content += '"Assignee" : null,'
             content += '"Status" : "Assigned",'
             content += '"z1D_Activity_Type" : "8000",'
             content += '"z1D_View_Access" : "1", '
             content += '"z1D_Secure_Log" : "0", '
             content += '"Detailed Decription" : "Auto-Ret|'+detailed_description+'",'
             content += '"z1D_Summary" : "Automation escalation entry", '
             if len(str(notes)) <= 0 or notes == None:
                 content += '"z1D_Details" : "Automation is escalating this incident"'
             else:
                 worknotes =[]
                 worknotes.append(notes)
                 worknotes =str(worknotes)
                 content += '"z1D_Details" : "'+worknotes+'"'
             content += ' } '
             content += ' } '
           elif pending:
             status_change="true"
             pending_mins = pending_mins +15
             nowtime = dt.datetime.now(pytz.timezone('US/Central')) + dt.timedelta(minutes = pending_mins)
             now_plus_pendingmins = dt.datetime.strftime(nowtime, "%Y-%m-%dT%H:%M:%S.%f")
             nowtime = dt.datetime.strftime(dt.datetime.now(pytz.timezone('US/Central')), "%Y-%m-%dT%H:%M:%S.%f")
             content = '{  '
             content += '"values": { '
             content += '"Status" : "Pending",'
             content += '"Status_Reason" : "14000",'
             #content += '"PendingSD__c" : "'+nowtime+'",'
             content += '"PendingED__c" : "'+now_plus_pendingmins+'",'
             content += '"z1D_Activity_Type" : "8000",'
             content += '"z1D_View_Access" : "1", '
             content += '"z1D_Secure_Log" : "0", '
             content += '"z1D_Summary" : "Automation Work Info update", '
             if len(str(notes)) <= 0 or notes == None:
                 content += '"z1D_Details" : "Incident moved to pending state."'
             else:
                 worknotes =[]
                 worknotes.append(notes)
                 worknotes =str(worknotes)
                 content += '"z1D_Details" : "'+worknotes+'"'
             content += ' } '
             content += ' } '
           else:
               if len(str(notes)) == 0 and notes == None:
                   raise Exception("One of close, escalate,pending,priorityupgrade or work_in_progress or worknote update must be set to True!")

           if len(str(notes)) > 0 and notes != None:
             # Notes string converted into dict for pass the multiple lines to json
             note_update="true"
             if "false" in status_change:
                 Only_notes_update="true"
                 worknotes =[]
                 worknotes.append(notes)
                 worknotes =str(worknotes)
                 content = '{  '
                 content += '"values": { '
                 content += '"z1D_Activity_Type" : "8000",'
                 content += '"z1D_View_Access" : "1", '
                 content += '"z1D_Secure_Log" : "0", '
                 content += '"z1D_Summary" : "Automation Work Info update", '
                 content += '"z1D_Details" : "'+worknotes+'"'
                 content += ' } '
                 content += ' } '


           helix_inc_update = "https://{0}{1}".format(self.helix_url,endpoint)
           response_update = requests.put(helix_inc_update, headers=headers, data=content, verify=True)

           # loggout the session
           headers = {"Authorization": helix_token}
           endpoint = '/api/jwt/logout'
           helix_inc_logout = "https://{0}{1}".format(self.helix_url,endpoint)
           response_logout = requests.post(helix_inc_logout, headers=headers,verify=True)

           return {"Response":response_update,"Content":content }

    def run(self, close, escalate, inc_id, notes, work_in_progress,pending, pending_mins, priorityupgrade, u_reason_for_priority_upgrade, priority, urgency, impact):
        itsm_tool = self.config['itsm_tool']
        #itsm_tool = 'helix'
        return_value = False
        if itsm_tool == 'servicenow':
            # Servicenow REST API
            # return_value = self.servicenow_update_REST_API(close, escalate, inc_id, notes, work_in_progress,pending, pending_mins, priorityupgrade, u_reason_for_priority_upgrade, priority, urgency, impact)
            # Servicenow Scripted API
            return_value = self.servicenow_update_scripted_API(inc_id, work_in_progress, pending,pending_mins, close, escalate, notes)

        elif itsm_tool == 'helix':
            return_value = self.helix_update(close, escalate, inc_id, notes, work_in_progress,pending, pending_mins, priorityupgrade, u_reason_for_priority_upgrade, priority, urgency, impact)
        else:
            error_message = 'Could not get ITSM info please check the config file and try again'
            return_value = (False, {'error_message': error_message})

        return return_value

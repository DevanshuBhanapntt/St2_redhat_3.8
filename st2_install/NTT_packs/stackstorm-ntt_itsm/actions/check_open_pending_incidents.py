#!/usr/bin/env python

import requests
from lib.base_action import BaseAction


class FetchOpenOrPendingIncidents(BaseAction):
    open_incs , pending_incs = 0, 0

    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(FetchOpenOrPendingIncidents, self).__init__(config=config)

    def check_servicenow_incidents(self, short_desc):
        self.sn_username = self.config['servicenow']['username']
        self.sn_password = self.config['servicenow']['password']
        self.sn_url = self.config['servicenow']['url']
        self.som_company_sys_id =  self.config['servicenow']['company_sys_id']
        self.servicenow_headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        incident_state = "2"
        incs_sts = False
        incident_sts_list = []
        for i in range(2):
            if i == 0:
                incident_state = "2"
            if i == 1:
                incident_state = "-5"
            url = "https://" + self.sn_url + "/api/now/table/incident?sysparm_query=active=true^incident_state=" + incident_state + "^company.sys_id=" + self.som_company_sys_id + "^priority=3^ORpriority=4^short_descriptionLIKE" + short_desc + "&sysparm_fields=number,company,cmdb_ci,short_description,sys_id,incident_state,opened_by"
            sn_result = requests.request('GET', url, auth=(self.sn_username, self.sn_password), headers=self.servicenow_headers)
            sn_result.raise_for_status()
            sn_incidents = sn_result.json()['result']
            if len(sn_incidents) == 0:
                incident_sts_list.append(True)
            else:
                incs_data = self.incidents_openedby(sn_incidents, incident_state)
                incident_sts_list.append(incs_data)
        if False in incident_sts_list:
            incs_sts = False
        elif True in incident_sts_list:
            incs_sts = True
        print("Create new incident: {}".format(incs_sts))
        return incs_sts

    def incidents_openedby(self, data, incident_state):
        create_incident = False
        payload = params = None
        for i in data:
            payload = params = None
            sn_api_call = requests.request('GET', url=i['opened_by']['link'], auth=(self.sn_username, self.sn_password), headers=self.servicenow_headers) #, json=payload, params=params)
            sn_api_call.raise_for_status()
            result = sn_api_call.json().get('result', [])
            opened_by = result['name']
            if opened_by == 'Automation Service' and incident_state == '2':
                FetchOpenOrPendingIncidents.open_incs += 1
            elif opened_by == 'Automation Service' and incident_state == '-5':
                FetchOpenOrPendingIncidents.pending_incs += 1
        if FetchOpenOrPendingIncidents.open_incs > 0 or FetchOpenOrPendingIncidents.pending_incs > 0:
            create_incident = False
        else:
            create_incident = True
        return create_incident

    def run(self, short_desc):
        val = self.check_servicenow_incidents(short_desc)
        return {"create_inc" : val }


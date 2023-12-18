from lib.base_action import BaseAction

class ServiceNowCreateIncident(BaseAction):

    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(ServiceNowCreateIncident, self).__init__(config)


    def run(self,company,requested_by,short_description,description,cmdb_ci,category,subcategory,assignment_group,impact):
        
        # REST API URL
        # endpoint = '/api/now/table/incident?sysparm_fields=number'
        # scripted/Customized API for NTT Data
        endpoint = '/api/ntt11/incident_automation_stackstorm/CreateIncident'
        
        # the below input fields only for Rest API
        # 'requested_by': requested_by,
        
        payload = {
                'company': company,
                'requested_by': requested_by,
                'short_description': short_description,
                'description': description,
                'cmdb_ci': cmdb_ci,
                'category' : category,
                'subcategory' : subcategory,
                'assignment_group': assignment_group,
                'impact': impact
            }

        inc = self.sn_api_call('POST', endpoint, payload=payload)
        #inc = ""
        return inc

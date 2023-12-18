from lib.base_action import BaseAction

class ServiceNowCreateProblem(BaseAction):

    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(ServiceNowCreateProblem, self).__init__(config)


    def run(self, assignment_group,company,description,short_description,u_problem_management_group,u_initiation_reason,cmdb_ci,u_problem_manager,u_problem_owner):
        # REST API URL
        endpoint = '/api/now/table/problem?sysparm_fields=number'
        payload = {
                'assignment_group': assignment_group,
                'company': company,
                'description': description,
                'short_description': short_description,
                'u_problem_management_group': u_problem_management_group,
                'u_initiation_reason' : u_initiation_reason,
                'cmdb_ci' :  cmdb_ci,
                'u_problem_manager' : u_problem_manager,
                'u_problem_owner': u_problem_owner
             }
        problem = self.sn_api_call('POST', endpoint, payload=payload)
        return problem
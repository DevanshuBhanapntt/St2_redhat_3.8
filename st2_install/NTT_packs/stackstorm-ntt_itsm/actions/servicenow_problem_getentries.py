from lib.base_action import BaseAction

class ServiceNowGetProblemDetail(BaseAction):

    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(ServiceNowGetProblemDetail, self).__init__(config)


    def run(self,company,short_description,cmdb_ci):
        query = 'active=1^company='+company+'^short_descriptionSTARTSWITH'+short_description+'^cmdb_ci='+cmdb_ci
        endpoint = '/api/now/table/problem?sysparm_query=' + query
        print(endpoint)
        problem = self.sn_api_call('GET', endpoint)
        return problem
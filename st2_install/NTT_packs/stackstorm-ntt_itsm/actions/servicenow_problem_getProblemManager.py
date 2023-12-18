from lib.base_action import BaseAction
import base_action

class ServiceNowGetProblemManagerDetail(BaseAction):

    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(ServiceNowGetProblemManagerDetail, self).__init__(config)
        self.base_action = base_action.BaseAction(config)

    def getmanagername(self,link):
        response = self.base_action.sn_api_call(method='GET',url=link)
        manager = response['name']
        return manager

    def run(self,query):
        endpoint = '/api/now/table/sys_user_group?sysparm_query=' + query
        print(endpoint)
        problem = self.sn_api_call('GET', endpoint)
        prob_manager = problem[0]
        prob_manager_link = (prob_manager['manager']['link'])
        print(prob_manager_link)
        manager = self.getmanagername(prob_manager_link)
        return manager
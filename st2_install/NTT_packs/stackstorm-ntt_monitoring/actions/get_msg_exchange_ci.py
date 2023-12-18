#!/usr/bin/env python
##################################
# Developer : Nalinikant Mohanty
##################################
from lib.base_action import BaseAction


class MsgExchangeCI(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(MsgExchangeCI, self).__init__(config)

    def get_ci_desc(self, ci_items, ci_item_dict, index):
        index = int(index)
        cmdb_ci = ci_items[index]
        description = ci_item_dict[cmdb_ci]
        index += 1
        return cmdb_ci, description, index

    def run(self, ci_items, ci_item_dict, index):
        cmdb_ci, description, index = self.get_ci_desc(ci_items, ci_item_dict, index)
        return {'cmdb_ci': cmdb_ci, 'ci_description': description, 'new_position': index}

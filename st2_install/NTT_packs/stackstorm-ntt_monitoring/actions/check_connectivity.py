#!/usr/bin/env python
from lib.base_action import BaseAction
import subprocess
import re

class CheckConnectivity(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(CheckConnectivity, self).__init__(config)
        
    def ListToString(self, listinput):
        stringoutput = ''
        for line in listinput:
           if line.strip() != "":
               stringoutput = stringoutput+ line
        return stringoutput
    
    def check_connectivity_status(self, username, password, ci_address):
        login_output = []
        script_name = "/opt/stackstorm/packs/ntt_monitoring/actions/nw_clogin.sh"
        script_options = '-noenable'
        #use -autoenable when noenable doent work for some devices
        #script_options = '-autoenable'
        command = 'help'
        execute_command = subprocess.Popen([script_name, script_options, '-u', username, '-p', password, '-c', command, ci_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        command_output = execute_command.stdout.readlines()
        start_index = end_index = 0
        convert_command_output = self.convert_bytes_to_string(command_output)
        command_out_string = self.ListToString(convert_command_output)
        print(command_out_string)
        for output in convert_command_output:
            if '>help' in output:
                start_index = convert_command_output.index(output)
            if '>logout' in output:
                end_index = convert_command_output.index(output)
        login_output = convert_command_output[int(start_index)+1:int(end_index)]
        connectivity_status = False
        for login_opt_str in login_output:
            if 'Ctrl-' in login_opt_str or 'available options' in login_opt_str:
                connectivity_status = True
                break
        return connectivity_status

    def convert_bytes_to_string(self, cmd_output_list):
        converted_list  = []
        for item in cmd_output_list:
            converted_list.append(item.decode('utf-8'))
        return converted_list

    def run(self, username, password, ci_address):
        connect_status = self.check_connectivity_status(username, password, ci_address)
        return connect_status

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
        command = 'show clock'
        execute_command = subprocess.Popen([script_name, script_options, '-u', username, '-p', password, '-c', command, ci_address.strip()], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        command_output = execute_command.stdout.readlines()
        start_index = end_index = 0
        convert_command_output = self.convert_bytes_to_string(command_output)
        command_out_string = self.ListToString(convert_command_output)
        print(command_out_string)
        for output in convert_command_output:
            if '#show clock' in output or '#  show clock' in output:
                start_index = convert_command_output.index(output)
            if '#exit' in output:
                end_index = convert_command_output.index(output)
        login_output = convert_command_output[int(start_index)+1:int(end_index)]
        print(login_output)
        connectivity_status = False
        day_list = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        for login_opt_str in login_output:
            print(login_opt_str)
            login_opt_date = self.day_month_regex(login_opt_str.strip(), "day")
            login_opt_month = self.day_month_regex(login_opt_str.strip(), "month")
            if login_opt_date in day_list and login_opt_month in month_list:
                connectivity_status = True
                break
                
        return connectivity_status

    def convert_bytes_to_string(self, cmd_output_list):
        converted_list  = []
        for item in cmd_output_list:
            converted_list.append(item.decode('utf-8'))
        return converted_list

    def convert_list_to_string(self, list_elements, include_space):
        string_value = ""
        for item in list_elements:
            if include_space:
                string_value += item + " "
            else:
                string_value += item
        return string_value

    def day_month_regex(self, output_string, day_month_check):
        day_data = "(Mon|Tue|Wed|Thu|Fri|Sat|Sun)"
        month_data = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        if day_month_check == "day":
            r = re.findall(day_data, output_string)
        elif day_month_check == "month":
            r = re.findall(month_data, output_string)
        day_month_value = self.convert_list_to_string(r, False)
        return day_month_value


    def run(self, username, password, ci_address):
        ci_address= ci_address.strip()
        connect_status = self.check_connectivity_status(username, password, ci_address)
        return connect_status

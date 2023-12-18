#!/usr/bin/env python
from lib.base_action import BaseAction
import subprocess
import re
import time



class CheckAPStatusRadio(BaseAction):
    output_data = ""
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(CheckAPStatusRadio, self).__init__(config)
    
    def ListToString(self, listinput):
        stringoutput = ''
        listinput = listinput.split("\n")
        for line in listinput:
           if line.strip() != "":
               stringoutput = stringoutput + line
        return stringoutput
    
    def check_ap_antenna_status(self, script_name, script_options, username, password, radio_command, ci_address, radio_start_index, radio_end_index, module_name):
        module_sts = []
        module_details = []
        antenna_radio_sts = (False, 'NONE')
        ap_antenna_status_all = []
        for i in range(2):
            if i == 0:
                radio_type = 'a'
            if i == 1:
                radio_type = 'b'
            radio_command = radio_command.replace('$type$', radio_type)
            ap_antenna_status , admin_sts, oper_sts = self.format_output(script_name, script_options, username, password, radio_command, ci_address, radio_start_index, radio_end_index, module_name)
            #print("AP antenna radio status is: {}".format(ap_antenna_status))
            ap_antenna_status_all += ap_antenna_status 
            
            if 'ENABLED' in admin_sts and 'UP' in oper_sts: 
                module_sts.append('UP')
                module_details.append(radio_command + ", " + module_name + "*ENABLED*UP")
            elif admin_sts.strip() == "" and oper_sts.strip() == "": 
                module_sts.append('DOWN')
                module_details.append(radio_command + ", " + module_name + "NOT_FOUND")
            else:
                module_sts.append('DOWN')
                module_details.append(radio_command + ", " + module_name + "*ENABLED*DOWN")
            radio_command = radio_command.replace('802.11'+radio_type, '802.11$type$')
        print("Accesspoint module name is: {}".format(module_name))
        print("Module status is: {}".format(module_sts))
        print("Module details are : {}".format(module_details)) 
        print("")   
        print("Automation executing show status for (all APs) on 802.11a and 802.11b:")   
        print("")        
        for item in ap_antenna_status_all:
           #print("Module_Name*Admin_Status*Oper_Status")
           output = self.ListToString(item)
           print(output)
        if len(module_sts) == 2 and 'DOWN' in module_sts:
            antenna_radio_sts = (False, 'ACCESSPOINT_ANTENNA_OFFLINE')
        elif len(module_sts) == 2 and 'DOWN' not in module_sts:
            antenna_radio_sts = (True, 'ACCESSPOINT_ANTENNA_ONLINE')
        return antenna_radio_sts

    def format_output(self, script_name, script_options, username, password, command, ci_address, start_index_check, end_index_check, module_name):
        cmd_output = []
        list_data = []
        admin_sts = ""
        oper_sts = ""
        output = self.execute_command_data(script_name, script_options, username, password, command, ci_address)
        start_index = 0
        end_index = 0
        str_command_output = self.convert_bytes_to_string_list(output)
        CheckAPStatusRadio.output_data = CheckAPStatusRadio.output_data + " " + self.convert_list_to_string(str_command_output, False)
        for i in str_command_output:
            if start_index_check in i:
                start_index = str_command_output.index(i)
            if end_index_check in i:
                end_index = str_command_output.index(i)
        cmd_output = str_command_output[int(start_index):int(end_index)]
        #print("Start Index is: {}".format(start_index))
        #print("End index is: {}".format(end_index))
        #print("Command output is: {}".format(cmd_output))
        
        for j in cmd_output:
            if j.strip() != '' and len(j.split()) >= 5:
                ap_data = j.split()
                ap_name = ap_data[0]
                if module_name in ap_name:
                    admin_sts = ap_data[2]
                    oper_sts = ap_data[3]
        
        return cmd_output , admin_sts, oper_sts
 
        #for j in cmd_output:
        #    if j.strip() != '' and len(j.split()) >= 5:
        #        ap_data = j.split()
        #        ap_name = ap_data[0]
        #        admin_sts = ap_data[2]
        #        oper_sts = ap_data[4]
        #        ap_admin_oper_sts = ap_name.strip() + '*' + admin_sts.strip() + '*' + oper_sts.strip()
        #        list_data.append(ap_admin_oper_sts)
        #print("Output: {}".format(list_data))
        #return list_data

    def execute_command_data(self, script_name, script_options, username, password, command, ci_address):
        execute_cmd = subprocess.Popen([script_name, script_options, '-u', username, '-p', password, '-c', command, ci_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        opt = execute_cmd.stdout.readlines()
        return opt

    def convert_bytes_to_string_list(self, list_elements):
        str_list = []
        for k in list_elements:
            str_list.append(k.decode('utf-8'))
        return str_list

    def convert_list_to_string(self, list_elements, include_space):
        string_value = ""
        for item in list_elements:
            if include_space:
                string_value += item + " "
            else:
                string_value += item
        return string_value

    def run(self, script_name, script_options, username, password, radio_command, ci_address, radio_start_index, radio_end_index, module_name):
        radio_status = self.check_ap_antenna_status(script_name, script_options, username, password, radio_command, ci_address, radio_start_index, radio_end_index, module_name)
        return radio_status

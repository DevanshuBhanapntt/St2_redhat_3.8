#!/usr/bin/env python
from lib.base_action import BaseAction
import subprocess
import re
import time
import datetime

class NetworkDeviceAlarm(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(NetworkDeviceAlarm, self).__init__(config)

    def check_version(self, script_name, script_options, username, password, version_command, ci_address):
        os_version = False
        cmd_data = self.execute_command_data(script_name, script_options, username, password, version_command, ci_address)
        version_command_output = self.convert_output_to_list(cmd_data)
        for i in version_command_output:
            if 'nexus' in i.lower() or 'nx-os' in i.lower():
                os_version = True
                break
        return os_version
        
    def ListToString(self, listinput):
        stringoutput = ''
        for line in listinput:
           if line.strip() != "":
               stringoutput = stringoutput+"\n"+line
        stringoutput = stringoutput + "\n"
        return stringoutput

    def check_inventory_status(self, script_name, script_options, username, password, version_command, inventory_command, switch_detail_command, show_log_command, ci_address, module_name):
        module_name = module_name.strip()
        ci_address = ci_address.strip()
        inventory_status = (False, "NONE")
        version_status = self.check_version(script_name, script_options, username, password, version_command, ci_address)
        if module_name == "ERROR_MODULE_NAME":
            module_sts = (False, "ERROR_MODULE_NAME")
            return module_sts
        if version_status:
            print("Network device type is Nexus\n")
            stack_member_cnt = 1
            command_data = self.execute_command_data(script_name, script_options, username, password, inventory_command, ci_address)
            inventory_command_sts = self.convert_output_to_list(command_data)
            inventory_command_sts_out = self.ListToString(inventory_command_sts)
            print("Inventory command status: {}".format(inventory_command_sts_out))
            #module_data = 'NAME: "'+module_name+'"'
            module_data = module_name
            if any(module_data in list_data for list_data in inventory_command_sts):
                inventory_status = (True, "MODULE_AVAILABLE_IN_INVENTORY")
                print("{} Module is available in inventory".format(module_name.strip()))
            else:
                inventory_status = (False, "MODULE_NOT_AVAILABLE_IN_INVENTORY")
                print("{} Module is not available in inventory".format(module_name.strip()))
            return inventory_status
        else:
            print("Network device is not Nexus OS")
            show_log_status = (False, "NONE")
            stack_member_cnt = 0
            #print("show switch detail")
            switch_command_data = self.execute_command_data(script_name, script_options, username, password, switch_detail_command, ci_address)
            switch_details = self.convert_output_to_list(switch_command_data)
            switch_details_out = self.ListToString(switch_details)
            print("Switch detail command output is: {}".format(switch_details_out))
            for item in switch_details:
                if 'master' in item.lower() or 'member' in item.lower() or 'active' in item.lower():
                    stack_member_cnt += 1
                else:
                    stack_member_cnt = 1
            if stack_member_cnt > 0:
                if stack_member_cnt > 1:
                    log_dates = self.convert_date_time()
                    log_date_format_1 = log_dates[0] + ".*[Ss]witch"
                    module_parameter_1 = log_dates[0] + ".*" + module_name
                    log_date_format_2 = log_dates[1] + ".*[Ss]witch"
                    module_parameter_2 = log_dates[1] + ".*" + module_name
                    log_command_filter = show_log_command + " | i \" " + log_date_format_1 + "|" + log_date_format_2 + "|" + module_parameter_1 + "|" + module_parameter_2 + "\""
                    show_log_cmd = self.execute_command_data(script_name, script_options, username, password, log_command_filter, ci_address)
                    show_log_output = self.convert_output_to_list(show_log_cmd)
                    show_log_out = self.ListToString(show_log_output)
                    print("Show log command is: {}".format(log_command_filter))
                    print("show log output is: {}".format(show_log_out))
                    for output in show_log_output:
                        if ('switch' in output.lower() and 'down' in output.lower()) or 'removed' in output.lower() or module_name.lower() in output.lower() and 'show log' not in output.lower():
                            show_log_status = (False, 'SWITCH_DOWN')
                            break
                            #print("Switch status is: DOWN")
                        elif ('invalid input detected at' in output.lower()):
                            show_log_status = (False, 'PERMISSHION_ERROR_TO_EXECUTE_COMMAND')
                            break
                        else:
                            show_log_status = (True, 'SWITCH_UP')
                            #print("Switch staus is: UP")
                    return show_log_status
                elif stack_member_cnt == 1:
                    command_data = self.execute_command_data(script_name, script_options, username, password, inventory_command, ci_address)
                    inventory_command_sts = self.convert_output_to_list(command_data)
                    inventory_command_sts_out = self.ListToString(inventory_command_sts)
                    print("Inventory command status: {}".format(inventory_command_sts_out))
                    #module_data = 'NAME: "'+module_name+'"'
                    module_data = module_name
                    if any(module_data in list_data for list_data in inventory_command_sts):
                        inventory_status = (True, "MODULE_AVAILABLE_IN_INVENTORY")
                        print("{} Module is available in inventory".format(module_name.strip()))
                    else:
                        inventory_status = (False, "MODULE_NOT_AVAILABLE_IN_INVENTORY")
                        print("{} Module is not available in inventory".format(module_name.strip()))
                    return inventory_status
            elif stack_member_cnt < 1:
                print("Automation user unable to find the status of the switch/stack member. Escalating the incident.")
                return show_log_status

    def execute_command_data(self, script_name, script_options, username, password, command, ci_address):
        execute_cmd = subprocess.Popen([script_name, script_options, '-u', username, '-p', password, '-c', command, ci_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        opt = execute_cmd.stdout.readlines()
        opt_str = self.convert_bytes_to_string_list(opt)
        #opt_list = self.convert_output_to_list(opt_str)
        return opt_str

    def convert_bytes_to_string_list(self, list_elements):
        str_list = []
        for k in list_elements:
            str_list.append(k.decode('utf-8'))
        return str_list

    def convert_output_to_list(self, output_data):
        output_list = []
        for output in output_data:
            output_list.append(output.strip())
        return output_list

    def convert_date_time(self):
        cr_time = datetime.datetime.now().replace(microsecond=0)
        pr_time = cr_time - datetime.timedelta(minutes=120)
        #print("current time: {}".format(cr_time))
        #print("previous time: {}".format(pr_time))
        month_mapping = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun", "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"}

        current_year = str(cr_time).split('-')[0]
        current_month = str(cr_time).split('-')[1]
        current_date = str(cr_time).split('-')[2].split()[0]
        previous_date = str(pr_time).split('-')[2].split()[0]
        current_time = str(cr_time).split()[1].split(':')[0]
        previous_time = str(pr_time).split()[1].split(':')[0]

        present_time = current_year + " " + month_mapping[current_month] + " " + current_date + " " + current_time
        if int(current_date) < 10:
            current_date = str(current_date).replace('0', '')
            present_time = current_year + " " + month_mapping[current_month] + "  " + current_date + " " + current_time
        #print("Present time: {}".format(present_time))

        previous_time_data = current_year + " " + month_mapping[current_month] + "  " + previous_date + " " + previous_time
        if int(previous_date) < 10:
            previous_date = str(previous_date).replace('0', '')
            previous_time_data = current_year + " " + month_mapping[current_month] + "  " + previous_date + " " + previous_time
        #print("Previous date: {}".format(previous_time_data))
        return present_time, previous_time_data


    def run(self, script_name, script_options, username, password, version_command, inventory_command, switch_detail_command, show_log_command, ci_address, module_name):
        module_str = module_name.split(':')[4].strip()
        pattern = "\((.*?)\)"
        try:
            module_name = re.search(pattern, module_str).group(1)
        except Exception as e:
            module_name = "ERROR_MODULE_NAME"
        inventory_details = self.check_inventory_status(script_name, script_options, username, password, version_command, inventory_command, switch_detail_command, show_log_command, ci_address, module_name)
        return inventory_details

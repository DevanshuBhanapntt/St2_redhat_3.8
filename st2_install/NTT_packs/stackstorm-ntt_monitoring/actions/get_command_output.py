#!/usr/bin/env python
from lib.base_action import BaseAction
import subprocess
import re
import time


class GetCommandOutput(BaseAction):
    output_data = ""
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(GetCommandOutput, self).__init__(config)

    def check_controller_ipaddress(self, script_name, script_options, username, password, mobility_command, ci_address, mobility_start_index_check, end_index_check):
        worknote_mobility = ["Gathering Mobility Group IP Addresses"]
        GetCommandOutput.output_data = GetCommandOutput.output_data + " " + self.convert_list_to_string(worknote_mobility, True)    
        ip_addresses = self.format_output(script_name, script_options, username, password, mobility_command, ci_address, mobility_start_index_check, end_index_check)
        return ip_addresses

    def check_controller_mac_address(self, script_name, script_options, username, password, mobility_command, mac_command, accesspoint_name, ci_address, mobility_start_index_check, mac_start_index_check, end_index_check):
        ip_mac_list = []
        mac_list = []
        ip_address_list = self.check_controller_ipaddress(script_name, script_options, username, password, mobility_command, ci_address, mobility_start_index_check, end_index_check)
        #print("IP address list: {}".format(ip_address_list))
        ap_cmd_name = mac_command + " " + accesspoint_name
        mac_address = self.format_output(script_name, script_options, username, password, ap_cmd_name, ci_address, mac_start_index_check, end_index_check)
        #print("Mac addres is: {}".format(mac_address))
        for mac in mac_address:
            if '-' not in mac:
                mac_list.append(mac)
        if len(mac_list) == 1:
            for ip in ip_address_list:
                ip_mac_list.append(ip+"*"+self.convert_list_to_string(mac_list, False))
        elif len(mac_list) < 1:
            #print("In else")
            for ip in ip_address_list:
                if ip != ci_address:
                    #print("IP is: {}".format(ip))
                    new_mac_address = self.format_output(script_name, script_options, username, password, ap_cmd_name, ip, mac_start_index_check, end_index_check)
                    #print("new mac output: {}".format(new_mac_address))
                    if len(new_mac_address) > 0:
                        for mac in new_mac_address:
                            if '-' not in mac:
                                #print("mac is: {}".format(mac))
                                mac_list.append(mac)
                                for ip_new in ip_address_list:
                                   ip_mac_list.append(ip_new+"*"+self.convert_list_to_string(mac_list, False))
                                break
                    else:
                        continue
        else:
            print("Multiple mac ids are available")
        print("IP Mac address list: {}".format(ip_mac_list))
        return ip_mac_list

    def check_ap_join_stauts(self, script_name, script_options, username, password, mobility_command, mac_command, accesspoint_name, ci_address, mobility_start_index_check, ap_join_status_cmd, mac_start_index_check, end_index_check):
        print("Accesspoint name: {}".format(accesspoint_name))
        timestamp_status = False
        ap_join_timestamp_list = []
        controller_connected_status = ""
        ap_join_timestamp = ""
        ip_mac_address = self.check_controller_mac_address(script_name, script_options, username, password, mobility_command, mac_command, accesspoint_name, ci_address, mobility_start_index_check, mac_start_index_check, end_index_check)
        for x in range(0,4):
            if len(ip_mac_address) > 0:
                for ip in ip_mac_address:
                    #print("IP is: {}".format(ip)) 
                    mac_output = ip.split('*')[1]               
                    worknote_ap = ["Automation found MAC Address " + mac_output + "for AP " + accesspoint_name + " on controller " + ci_address]
                    GetCommandOutput.output_data = GetCommandOutput.output_data + "\n\n" + self.convert_list_to_string(worknote_ap, True)
                    worknote_stats = ["Automation found that AP "+ accesspoint_name + " with mac address " + mac_output + " is connected to controller" + ci_address + ". Waiting 90 seconds to check the join status again."]
                    GetCommandOutput.output_data = GetCommandOutput.output_data + "\n\n" + self.convert_list_to_string(worknote_stats, True) 
                    time.sleep(90)  
                    worknote_time1 = ["Command output of 1st join check:"]                
                    GetCommandOutput.output_data = GetCommandOutput.output_data + "\n\n" + self.convert_list_to_string(worknote_time1, True)
                    ap_join_sts = self.format_output(script_name, script_options, username, password, ap_join_status_cmd+" "+ip.split('*')[1], ip.split('*')[0], ap_join_status_cmd, end_index_check)
                    #print("ap join status: {}".format(ap_join_sts))
                    for item in ap_join_sts:
                        if 'Is the AP currently connected to controller' in item:
                            controller_connected_status = item.split()[7]
                    if controller_connected_status == 'Yes': 
                        time.sleep(90)
                        worknote_time2 = ["Command output of 2nd join check:"]                
                        GetCommandOutput.output_data = GetCommandOutput.output_data + "\n\n" + self.convert_list_to_string(worknote_time2, True)
                        new_ap_join_sts = self.format_output(script_name, script_options, username, password, ap_join_status_cmd+" "+ip.split('*')[1], ip.split('*')[0], ap_join_status_cmd, end_index_check)
                        for i in range(2):
                            if i == 0:
                                list_value = ap_join_sts
                            if i == 1:
                                list_value = new_ap_join_sts
                            for item_new in list_value:
                                if 'Time at which the AP joined this controller last time' in item_new:
                                    ap_join_timestamp = item_new.split()[10:]
                                    date_format = self.validate_date(ap_join_timestamp[0], ap_join_timestamp[1])
                                    if date_format:
                                        ap_join_timestamp_list.append(self.convert_list_to_string(ap_join_timestamp, True))
                        if ap_join_timestamp_list and ap_join_timestamp_list[0] == ap_join_timestamp_list[1]:
                            timestamp_status = True
                        elif ap_join_timestamp_list and ap_join_timestamp_list[0] != ap_join_timestamp_list[1]:
                            print("Escalate the ticket as flapping condition")
                            ticket_status = (False, "FLAPPING")
                        break
                    else:
                        controller_connected_status = "No"
                        continue
                break      
            else:
                time.sleep(300)
            
        if controller_connected_status == "":
            print("Automation did not find the MAC address in show ap search after 20 minutes. Escalating the ticket.")
            ticket_status = (False, "RESULTS_EMPTY")
        elif controller_connected_status == "No":
            print("Automation found the controller connected status is 'No' even after 20 minutes. Escalating the ticket.")
            ticket_status = (False, "FAILURE")
        else:
            print("Controller connected status: {}".format(controller_connected_status))
            print("Timestamp status: {}".format(timestamp_status))
            worknote_time = ["Automation found that the join time for AP "+ accesspoint_name +" on controller "+ ci_address +" remained the same after 90 seconds."]
            GetCommandOutput.output_data = GetCommandOutput.output_data + " " + self.convert_list_to_string(worknote_time, True)
            ticket_status = (True, "SUCCESS")
        #return controller_connected_status, timestamp_status
        print("\n\nOutput data is:\n\n {}".format(GetCommandOutput.output_data))
        return ticket_status

    def format_output(self, script_name, script_options, username, password, command, ci_address, start_index_check, end_index_check):
        cmd_output = []
        list_data = []
        output = self.execute_command_data(script_name, script_options, username, password, command, ci_address)
        start_index = 0
        end_index = 0
        str_command_output = self.convert_bytes_to_string_list(output)
        GetCommandOutput.output_data = GetCommandOutput.output_data + " " + self.convert_list_to_string(str_command_output, False)
        GetCommandOutput.output_data = GetCommandOutput.output_data + "\n"
        for i in str_command_output:
            if start_index_check in i:
                start_index = str_command_output.index(i)
            if end_index_check in i:
                end_index = str_command_output.index(i)
        cmd_output = str_command_output[int(start_index)+1:int(end_index)]
        #print("Start Index is: {}".format(start_index))
        #print("End index is: {}".format(end_index))
        #print("Command output is: {}".format(cmd_output))

        for j in cmd_output:
            if 'show ap join stats summary' in command and j.strip() != '':
                list_data.append(j.strip())
            else:
                add_string = re.sub(' +', '*', j.strip())
                if add_string != '':
                    list_data.append(add_string.split('*')[1])
        #print("Output: {}".format(list_data))        
        return list_data

    def execute_command_data(self, script_name, script_options, username, password, command, ci_address):
        #use -autoenable when -noenable doesnt work for some devices
        #script_options = '-autoenable'
        execute_cmd = subprocess.Popen([script_name, script_options, '-u', username, '-p', password, '-c', command, ci_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        opt = execute_cmd.stdout.readlines()
        return opt

    def convert_bytes_to_string_list(self, list_elements):
        str_list = [] 
        for k in list_elements:
            if 'spawn' not in k.decode('utf-8') and 'config paging disable' not in k.decode('utf-8') and 'The system has unsaved' not in k.decode('utf-8') and 'Would you like to save them' not in k.decode('utf-8') and (k.decode('utf-8')).strip() != "" and 'logout' not in k.decode('utf-8'):
                str_list.append(k.decode('utf-8'))
            if 'logout' in k.decode('utf-8'):
                str_list.append(k.decode('utf-8'))
                str_list.append("")
                str_list.append("")
        return str_list

    def convert_list_to_string(self, list_elements, include_space):
        string_value = ""
        for item in list_elements:
            if include_space:
                string_value += item + " "
            else:
                string_value += item
        return string_value

    def validate_date(self, month, dt):
        is_valid_date = False
        month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        if month in month_list and int(dt) <= 31:
            is_valid_date = True
        return is_valid_date

    def run(self, script_name, script_options, username, password, mobility_command, mac_command, accesspoint_name, ci_address, mobility_start_index_check, ap_join_status_cmd, mac_start_index_check, end_index_check):
        if(accesspoint_name):
            accesspoint_status = self.check_ap_join_stauts(script_name, script_options, username, password, mobility_command, mac_command, accesspoint_name, ci_address, mobility_start_index_check, ap_join_status_cmd, mac_start_index_check, end_index_check)
        else:
            accesspoint_status = "Access Point Name is not found in the incident description. Escalating the ticket."
            ticket_status = (False, "FAILURE")
        print("Access point details are: {}".format(accesspoint_status))
        return accesspoint_status

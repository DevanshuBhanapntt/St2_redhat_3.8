#!/usr/bin/env python
from lib.base_action import BaseAction
import subprocess
import re
import time
import datetime
import socket
import os

class PowerSupply(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(PowerSupply, self).__init__(config)
        
    def substring(self, s, after, before):
        s = s.strip()
        s1 = s.partition(after)[2]
        s2 = s1.partition(before)[0]
        s2 = s2.strip()
        return s2
    
    def substring_after(self, s, after):
        s = s.strip()
        s1 = s.partition(after)[2]
        s1 = s1.strip()
        return s1
        
    def check_version(self, script_name, script_options, username, password, version_command, ci_address):
        os_version = False
        cmd_data = self.execute_command_data(script_name, script_options, username, password, version_command, ci_address)
        version_command_output = self.convert_output_to_list(cmd_data)
        return version_command_output
    
    def get_power_supply_command(self, version_command_output):
        model = ""
        Power_Supply_cmd = ""
        model_check_output = ""        
        for line in version_command_output:
            if 'bytes of memory' in line.lower() or 'chassis' in line.lower() or 'bytes of' in line.lower() or 'processor' in line.lower():
               model_check_output += line        
        
        if 'Nexus7000 ' in model_check_output:
            model = self.substring(model_check_output, "Nexus7000 ", " ")
            model = model.strip()
        if 'Nexus ' in model_check_output:
            model = self.substring(model_check_output, "Nexus ", " ")
            model = model.strip()
        if 'cisco ' in model_check_output:
            model = self.substring(model_check_output, "cisco ", " ")
            model = model.strip()
        if 'Cisco ' in model_check_output:
            model = self.substring(model_check_output, "Cisco ", " ")
            model = model.strip()
        
        if '6509' in model or '6513' in model:
            Power_Supply_cmd = "show env | include power-supply"
        if '3850' in model or '3750' in model or '2960' in model or '2950' in model or '3560' in model or '3550' in model:
            Power_Supply_cmd = "show env power"
        if '4506' in model or '4507' in model or '4510' in model or '4500' in model:
            Power_Supply_cmd = "show environment status powersupply"
        if '6504' in model or '6506' in model:
            Power_Supply_cmd = "show environment status | incl power-supply"
        if '3925' in model or '3945' in model or '2951' in model or '2911' in model or 'C9300-48P' in model or 'C9300-48U' in model or 'C9500-48Y4C' in model or 'C9500-40X' in model:
            Power_Supply_cmd = "show env all"
        if 'ASR' in model:
            Power_Supply_cmd = "sh env all | i PEM"
        if '7206' in model:
            Power_Supply_cmd = "sh env all"
        if '5548' in model or '7009' in model or '7010' in model or '7018' in model or '5020' in model or '5596' in model or '5612' in model or '5624' in model or '7004' in model or 'C9300-24P' in model or 'WS-C3650-48PD' in model:
            Power_Supply_cmd = "show environment power"
        return model,Power_Supply_cmd
    
    def check_power_supply_ok(self, power_supply_output, model_id):
        Power_Supply_Okay = True             
        
        if '6509' in model_id or '6504' in model_id or '6506' in model_id:
            for line in power_supply_output:
                if 'power-output-fail: fail' in line.lower() or 'power-output-fail: bad' in line.lower() or 'power-output-fail: no input power' in line.lower() or 'power-output-fail: off' in line.lower():
                    Power_Supply_Okay = False
        if '3850' in model_id or '5020' in model_id or '3750' in model_id or '4506' in model_id or '4507' in model_id or '3560' in model_id:
            for line in power_supply_output:
                if 'fail' in line.lower() or 'bad' in line.lower() or 'no input power' in line.lower() or 'unavail' in line.lower() or 'off' in line.lower():
                    Power_Supply_Okay = False
        if '2960' in model_id or '2950' in model_id or '3550' in model_id:
            for line in power_supply_output:
                if 'power' in line.lower() and ('fail' in line.lower() or 'bad' in line.lower() or 'no input power' in line.lower() or 'unavail' in line.lower() or 'off' in line.lower()):
                    Power_Supply_Okay = False
        if '4948' in model_id or '4510' in model_id or '4500' in model_id:
            for line in power_supply_output:
                if 'ps' in line.lower() and ('fail' in line.lower() or 'bad' in line.lower() or 'no input power' in line.lower() or 'unavail' in line.lower() or 'off' in line.lower()):
                    Power_Supply_Okay = False
        if '5548' in model_id or '5596' in model_id or '5612' in model_id or '5624' in model_id:
            for line in power_supply_output:
                if 'pac' in line.lower() and ('fail' in line.lower() or 'bad' in line.lower() or 'no input power' in line.lower() or 'unavail' in line.lower() or 'off' in line.lower()):
                    Power_Supply_Okay = False
        if '7009' in model_id or '7010' in model_id or '7018' in model_id or '7206' in model_id or '7004' in model_id or 'C9300-24P' in model_id:
            for line in power_supply_output:
                if 'ac' in line.lower() and ('fail' in line.lower() or 'bad' in line.lower() or 'no input power' in line.lower() or 'unavail' in line.lower() or 'off' in line.lower() or 'fault' in line.lower()):
                    Power_Supply_Okay = False
        if '3925' in model_id or '3945' in model_id or '2951' in model_id or '2911' in model_id or '2900' in model_id or 'C9300-48P' in model_id or 'WS-C3650-48PD' in model_id or 'C9500-48Y4C' in model_id or 'C9500-40X' in model_id or 'C9300-48U' in model_id:
            for line in power_supply_output:
                if 'output status' in line.lower() and ('fail' in line.lower() or 'bad' in line.lower() or 'no input power' in line.lower() or 'unavail' in line.lower() or 'off' in line.lower()):
                    Power_Supply_Okay = False
        if 'ASR' in model_id:
            for line in power_supply_output:
                if ('pem vout' in line.lower() and '0 v' in line.lower()) or ('pem iout' in line.lower() and '0 a' in line.lower()):
                    Power_Supply_Okay = False
        return Power_Supply_Okay
        
    def check_power_status(self, script_name, script_options, username, password, version_command, show_clock, Power_Supply_cmd, ci_address):
        ci_address = ci_address.strip()
        version_output = self.check_version(script_name, script_options, username, password, version_command, ci_address)
        model,Power_Supply_cmd = self.get_power_supply_command(version_output)        
        if not Power_Supply_cmd:
            print("Automation not able to find the device model to check its power status. Hence Escalating the Incident")
        else:
            command_data = self.execute_command_data(script_name, script_options, username, password, show_clock, ci_address)
            show_clock_sts = self.convert_output_to_list(command_data)
            command_data = self.convert_list_to_string(command_data,False)
            print("show clock command output:\n {}".format(command_data))
            #return command_data
            #print("Network device is not Nexus OS")
            #print("Output of command: show environment status | include power-supply")
            power_command_data = self.execute_command_data(script_name, script_options, username, password, Power_Supply_cmd, ci_address)
            power_details = self.convert_output_to_list(power_command_data)
            power_command_data = self.convert_list_to_string(power_command_data,False)
            print("Power supply command output is:\n {}".format(power_command_data))
            power_supply_status = self.check_power_supply_ok(power_details, model)
            if (power_supply_status):
                print('Power supply status is okay')
            return power_supply_status


    def execute_command_data(self, script_name, script_options, username, password, command, ci_address):
        poweroutput = []       
        command_success = ""
        #use -autoenable when noenable doesnt work for some devices
        #script_options = '-autoenable'
        execute_cmd = subprocess.Popen([script_name, script_options, '-u', username, '-p', password, '-c', command, ci_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        opt = execute_cmd.stdout.readlines()
        opt_str = self.convert_bytes_to_string_list(opt)
        filename = "/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_poweroutput.txt"
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_poweroutput.txt", 'wb')
        file1.writelines(opt)
        file1.close()
        command_temp = command[1:]        
        with open(filename) as myfile:
            if command in myfile.read():
                command_success = True
                check_cmd_in_file = command
            elif command_temp in myfile.read():
                command_success = True
                check_cmd_in_file = command_temp
                
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_poweroutput.txt", 'rb') 
        Lines = file1.readlines()
        if command_success:
            append = 0
            for line in Lines:
                if check_cmd_in_file in line.decode('utf-8'):
                    append = 1
                if append == 1:
                    if b'Connection' not in line and b'=' not in line and b'spawn' not in line and b'exit' not in line and b'xit' not in line and b"'" not in line and b'password' not in line and b'CCCCCC' not in line:                
                        poweroutput.append(line.decode('utf-8'))
        else:
            for line in Lines:
                if b'Connection' not in line and b'=' not in line and b'spawn' not in line and b'exit' not in line and b'xit' not in line and b"'" not in line and b'password' not in line and b'CCCCCC' not in line:
                    poweroutput.append(line.decode('utf-8'))
        return poweroutput

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
    
    def convert_list_to_string(self, list_elements, include_space):
        string_value = ""
        for item in list_elements:
            if include_space:
                string_value += item + " "
            else:
                string_value += item
        return string_value

    def run(self, script_name, script_options, username, password, version_command, show_clock, Power_Supply_cmd, ci_address):
        #module_name = module_name.split(':')[2].strip()
        power_status = self.check_power_status(script_name, script_options, username, password, version_command, show_clock, Power_Supply_cmd, ci_address)
        os.remove("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_poweroutput.txt")       
        return power_status

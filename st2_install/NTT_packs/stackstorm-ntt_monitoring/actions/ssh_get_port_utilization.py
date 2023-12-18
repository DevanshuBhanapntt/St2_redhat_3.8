#!/usr/bin/env python
# Copyright 2019 Encore Technologies
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from st2common.runners.base_action import Action
import subprocess
from fractions import Fraction
import paramiko
import sys


class SSHGetPortUtilization(Action):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(SSHGetPortUtilization, self).__init__(config)

    def ListToString(self, listinput):
        stringoutput = ''
        for line in listinput:
           if line.strip() != "":
               stringoutput = stringoutput+ line
        return stringoutput

    def convert_bytes_to_string(self, cmd_output_list):
        converted_list  = []
        for item in cmd_output_list:
            converted_list.append(item.decode('utf-8'))
        return converted_list
        
    def execute_interface_command(self, interface, vendor, username, password, ci_address, is_entuity, entuity_ip, interface_ip, entuity_user, entuity_pass, command):
        if 'true' in is_entuity:       
            port = 22        
            script_command = "/home/bao_net_mon/clogin -noenable -b "+interface_ip+" -u "+username+" -p "+password+" -c '"+command+"' "+ci_address
            ssh = paramiko.SSHClient() 
            ssh.load_system_host_keys()            
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(entuity_ip, username=entuity_user, password=entuity_pass, look_for_keys = False) #timeout=10
            stdin, stdout, stderr = ssh.exec_command(script_command,get_pty=True)
            command_output = stdout.readlines()
            command_output = self.ListToString(command_output)
            error = stderr.readlines()
            error = self.ListToString(error)
            ssh.close()
            self.check_stderr(error, 'status', interface)
            status_output = command_output
        else:
            script_name = "/opt/stackstorm/packs/ntt_monitoring/actions/nw_clogin.sh"
            script_options = '-autoenable'        
            execute_command = subprocess.Popen([script_name, script_options, '-u', username, '-p', password, '-c', command, ci_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            command_output = execute_command.stdout
            command_output = self.convert_bytes_to_string(command_output)
            error = execute_command.stderr
            error = self.convert_bytes_to_string(error)
            self.check_stderr(error, 'status', interface)
            status_output = self.ListToString(command_output)
        
        if 'Error: Couldn' in status_output and 'login:' in status_output:
            raise Exception("""Error checking utilization for interface {}.
                            Error message: {}""".format(interface, status_output))    
        
        return  status_output,error

    def get_utilization(self, interface, vendor, username, password, ci_address, is_entuity, entuity_ip, interface_ip, entuity_user, entuity_pass):
        command = "show interface " + interface        
        status_output,error = self.execute_interface_command(interface, vendor, username, password, ci_address, is_entuity, entuity_ip, interface_ip, entuity_user, entuity_pass,command)
        #status_stdout = status_output.split("\n")
        #stdout_interface = ''
        #for line in status_stdout:
        #    if line.strip != "":
        #        stdout_interface += stdout_interface + "\n"

        print(status_output)
        if ("is up" in status_output) and (vendor == "Dell"):
            command = "show interface utilization " + interface
            command_output,error = self.execute_interface_command(interface, vendor, username, password, ci_address, is_entuity, entuity_ip, interface_ip, entuity_user, entuity_pass,command)
            self.check_stderr(error, 'utilization', interface)
            return self.parse_dell_output(command_output)
        elif ("is up" in status_output) and (vendor != "Dell"):
            #print('into 1')
            result_dict = self.parse_cisco_output(status_output)
            command = "show ip flow top-talkers"
            command_output,error = self.execute_interface_command(interface, vendor, username, password, ci_address, is_entuity, entuity_ip, interface_ip, entuity_user, entuity_pass,command)
            self.check_stderr(error, 'top talkers', interface)
            result_dict['top_talkers'] = command_output
            return result_dict
        else:
            raise Exception("""Interface {} is down.
                             Error message: {}""".format(interface, error))

    def check_stderr(self, stderr, cmd, interface):
        if stderr:
            raise Exception("""Error getting {} for interface {}.
                            Error message: {}""".format(cmd, interface, error))

    def parse_dell_output(self, output):
        for line in output.splitlines():
            if "Input" in line:
                input_utilization = float(line.split("Input")[1].split("Mbits/sec")[0])
            elif "Output" in line:
                output_utilization = float(line.split("Output")[1].split("Mbits/sec")[0])

        rxload = input_utilization / 100
        txload = output_utilization / 100
        result_dict = {
            'rxload': rxload,
            'txload': txload,
            'reliability': 0
        }

        return result_dict

    def parse_cisco_output(self, output):
        txload = output.split("txload")[1].split(",")[0]
        txload = txload.strip()
        txload = txload.split('/')
        txload_f1 = int(txload[0])
        txload_f2 = int(txload[1])
        txload_percent = int((txload_f1 / txload_f2) * 100)

        rxload = output.split("rxload")[1].split('\n')[0]
        rxload = rxload.strip()
        rxload = rxload.split('/')
        rxload_f1 = int(rxload[0])
        rxload_f2 = int(rxload[1])
        rxload_percent = int((rxload_f1 / rxload_f2) * 100)

        reliability = output.split("reliability")[1].split(",")[0]
        reliability = reliability.strip()
        reliability = reliability.split('/')
        reliability_f1 = int(reliability[0])
        reliability_f2 = int(reliability[1])
        reliability_percent = int((reliability_f1 / reliability_f2) * 100)

        result_dict = {
            'rxload': rxload_percent,
            'txload': txload_percent,
            'reliability': reliability_percent
        }

        return result_dict

    def run(self, **kwargs):
        interface = kwargs['interface']
        ip_addr = kwargs['ci_address']
        ci_address = kwargs['ci_address']
        password = kwargs['ssh_password']
        username = kwargs['ssh_username']
        vendor = kwargs['device_vendor']
        is_entuity = kwargs['is_entuity']
        entuity_ip = kwargs['entuity_ip']
        interface_ip = kwargs['interface_ip']
        entuity_user = kwargs['entuity_user']
        entuity_pass = kwargs['entuity_pass']
        port = 22
        utilization = ''

        try:
            utilization = self.get_utilization(interface, vendor, username, password, ci_address, is_entuity, entuity_ip, interface_ip, entuity_user, entuity_pass)
        except Exception as e:
            print("Could not establish an SSH client with the device. "
                  "Error: {}".format(e).replace("'", ""))


        return utilization

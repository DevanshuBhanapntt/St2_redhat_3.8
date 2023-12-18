#!/usr/bin/env python
from lib.base_action import BaseAction
import subprocess
import re
import os

class Get_notNXOS(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(Get_notNXOS, self).__init__(config)

    def get_notnxos(self, username, password, ci_address, peer_ip):
        login_output = []
        script_name = "/opt/stackstorm/packs/ntt_monitoring/actions/nw_clogin.sh"
        script_options = '-noenable'
        neighbor_command = 'show ip ospf neighbor detail'
        interface_command = 'show ip ospf interface'
        router_command = "show ip ospf border-routers"
        peerip=ci_address
        ip_address=b''
        ip_address=ci_address
        check_output = ""
        execute_command = subprocess.Popen([script_name, script_options, '-u', username, '-p', password, '-c', neighbor_command, ci_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        command_output = execute_command.stdout.readlines()
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_notnxosdetail.txt", 'wb')
        file1.writelines(command_output)
        file1.close()
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_notnxosdetail.txt", 'rb')
        Lines = file1.readlines()
        appendline = ""
        pingpeerip= "ping "+peerip
        for line in Lines:
            neighbouroutput = line.decode()
            appendline += line.decode()
            
        execute_command1 = subprocess.Popen([script_name, script_options, '-u', username, '-p', password, '-c', interface_command, ci_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        command_output1 = execute_command1.stdout.readlines()
        start_index = end_index = 0
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_notnxosdetail.txt", 'wb')
        file1.writelines(command_output1)
        file1.close()
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_notnxosdetail.txt", 'rb')
        Lines = file1.readlines()
        for line in Lines:
            if b'Connection' not in line and b'=' not in line and b'spawn' not in line and b'exit' not in line and b'VTY' not in line and b'xit' not in line and b"'" not in line and b'password' not in line and b'CCCCCC' not in line :
               interfaceoutput= line.decode()
               appendline += line.decode()
        execute_command = subprocess.Popen([script_name, script_options, '-u', username, '-p', password, '-c', pingpeerip, ci_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        command_output = execute_command.stdout.readlines()
        start_index = end_index = 0
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_notnxosfile.txt", 'wb')
        file1.writelines(command_output)
        file1.close()
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_notnxosfile.txt", 'rb')
        Lines = file1.readlines()
        for line in Lines:
            if b'Connection' not in line and b'=' not in line and b'spawn' not in line and b'exit' not in line and b'VTY' not in line and b'xit' not in line and b"'" not in line and b'password' not in line and b'CCCCCC' not in line :
            #elif b'Success' in line :   
                peerpingoutput= line.decode()
                appendline += line.decode()
            if b'Success' in line :
               appendline += line.decode()
        execute_command = subprocess.Popen([script_name, script_options, '-u', username, '-p', password, '-c',router_command, ci_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        command_output = execute_command.stdout.readlines()
        start_index = end_index = 0
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_notnxosdetail.txt", 'wb')
        file1.writelines(command_output)
        file1.close()
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_notnxosdetail.txt", 'rb')
        Lines = file1.readlines()
        for line in Lines:
            if b'Connection' not in line and b'=' not in line and b'spawn' not in line and b'exit' not in line and b'VTY' not in line and b'xit' not in line and b"'" not in line and b'password' not in line and b'CCCCCC' not in line :
                pinginterfaceoutput= line.decode()
                appendline += line.decode()
            if b'Success' in line :
               appendline += line.decode()

        print(appendline)
        #os.remove('/opt/stackstorm/packs/ntt_monitoring/actions/cpufile.txt')


    def run(self, username, password, ci_address, peer_ip):
        neighbor_status = self.get_notnxos(username, password, ci_address, peer_ip)
        return neighbor_status
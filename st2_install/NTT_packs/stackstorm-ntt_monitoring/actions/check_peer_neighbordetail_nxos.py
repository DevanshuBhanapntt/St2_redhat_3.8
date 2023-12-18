#!/usr/bin/env python
from lib.base_action import BaseAction
import subprocess
import re
import os

class Get_NXOS(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(Get_NXOS, self).__init__(config)

    def get_nxos(self, username, password, ci_address, peer_ip):
        login_output = []
        script_name = "/opt/stackstorm/packs/ntt_monitoring/actions/nw_clogin.sh"
        script_options = '-noenable'
        neighbor_command = 'show ip ospf neighbors detail'
        interface_command = 'show ip ospf interface'
        router_command = "show ip ospf border-routers"
        peerip=ci_address
        ip_address=b''
        ip_address=ci_address
        check_output = ""
        execute_command = subprocess.Popen([script_name, script_options, '-u', username, '-p', password, '-c', neighbor_command, ci_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #execute_command1 = subprocess.Popen([script_name, script_options, '-u', username, '-p', password, '-c', interface_command, ci_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #print(execute_command)
        command_output = execute_command.stdout.readlines()
        #command_output1 = execute_command1.stdout.readlines()
        #command_output = execute_command.stdout
        #print(command_output)
        #output_string=execute_command.split("\n", 1)[1]
        #print(output_string)
        #start_index = end_index = 0
        #convert_command_output = self.convert_bytes_to_string(command_output)
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_nxosdetail.txt", 'wb')
        file1.writelines(command_output)
        file1.close()
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_nxosdetail.txt", 'rb')
        Lines = file1.readlines()
        #Lines="""AUGMILIDF18SW01#^M
#AUGMILIDF18SW01#terminal length 0
#AUGMILIDF18SW01#show ip ospf neighbor
#Neighbor ID Pri State Dead Time Address Interface
#10.164.168.1 1 FULL/DROTHER 00:00:34 10.164.168.1 GigabitEthernet0
#155.16.58.59 1 FULL/DR 00:00:32 10.164.168.254 Vlan100
#AUGMILIDF18SW01#"""
        appendline = ""
        pingpeerip= "ping "+peerip
        for line in Lines:
            neighbouroutput= line.decode()
            appendline += line.decode()
 
        execute_command1 = subprocess.Popen([script_name, script_options, '-u', username, '-p', password, '-c', interface_command, ci_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        command_output1 = execute_command1.stdout.readlines()
        start_index = end_index = 0
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_nxosdetail.txt", 'wb')
        file1.writelines(command_output1)
        file1.close()
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_nxosdetail.txt", 'rb')
        Lines = file1.readlines()
        for line in Lines:
            if b'Connection' not in line and b'=' not in line and b'spawn' not in line and b'exit' not in line and b'VTY' not in line and b'xit' not in line and b"'" not in line and b'password' not in line and b'CCCCCC' not in line :
               interfaceoutput= line.decode()
               appendline += line.decode()
        execute_command = subprocess.Popen([script_name, script_options, '-u', username, '-p', password, '-c', pingpeerip, ci_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        command_output = execute_command.stdout.readlines()
        start_index = end_index = 0
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_nxosfile.txt", 'wb')
        file1.writelines(command_output)
        file1.close()
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_nxosfile.txt", 'rb')
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
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_nxosdetail.txt", 'wb')
        file1.writelines(command_output)
        file1.close()
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_nxosdetail.txt", 'rb')
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
        neighbor_status = self.get_nxos(username, password, ci_address, peer_ip)
        # using the os.path.exists() function to check the existence of the file
        #if os.path.exists("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_cpufile.txt"):
        os.remove("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_nxosdetail.txt")
           #print("File deleted successfully")
        #else:
           #print("File does not exist")
        return neighbor_status





















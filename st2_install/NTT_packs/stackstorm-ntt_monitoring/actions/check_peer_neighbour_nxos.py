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

    def get_nxos(self, username, password, ci_address, neighbour_command, peer_ip):
        login_output = []
        script_name = "/opt/stackstorm/packs/ntt_monitoring/actions/nw_clogin.sh"
        script_options = '-noenable'
        command = 'show ip ospf neighbor'
        interface_command = 'show interface'
        peerip=ci_address
        ip_address=b''
        ip_address=ci_address
        check_output = ""
        execute_command = subprocess.Popen([script_name, script_options, '-u', username, '-p', password, '-c', command, ci_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_nxosfile.txt", 'wb')
        file1.writelines(command_output)
        file1.close()
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_nxosfile.txt", 'rb')
        Lines = file1.readlines()
        #Lines="""AUGMILIDF18SW01#^M
#AUGMILIDF18SW01#terminal length 0
#AUGMILIDF18SW01#show ip ospf neighbor
#Neighbor ID Pri State Dead Time Address Interface
#10.164.168.1 1 FULL/DROTHER 00:00:34 10.164.168.1 GigabitEthernet0
#155.16.58.59 1 FULL/DR 00:00:32 10.164.168.254 Vlan100
#AUGMILIDF18SW01#"""
        appendline = ""
        interface_cmd = ""
        pingpeerip= "ping "+peerip
        for line in Lines:
            #if b'Connection' not in line and b'=' not in line and b'spawn' not in line and b'exit' not in line and b'VTY' not in line and b'xit' not in line and b"'" not in line and b'password' not in line and b'CCCCCC' not in line :
                neighbouroutput= line.decode()
                appendline += line.decode()
                if re.search(peer_ip, str(neighbouroutput)):
                  check_output += "Peer IP is present\n"
                  interface_name=""
                  interface_name=neighbouroutput.split()[6]
                  interface_cmd=interface_command+" "+interface_name

        execute_command1 = subprocess.Popen([script_name, script_options, '-u', username, '-p', password, '-c', interface_cmd, ci_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        command_output1 = execute_command1.stdout.readlines()
        start_index = end_index = 0
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_notnxosfile.txt", 'wb')
        file1.writelines(command_output1)
        file1.close()
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_notnxosfile.txt", 'rb')
        Lines = file1.readlines()
        pingwithinterface = ""
        for line in Lines:
            if b'Connection' not in line and b'=' not in line and b'spawn' not in line and b'exit' not in line and b'VTY' not in line and b'xit' not in line and b"'" not in line and b'password' not in line and b'CCCCCC' not in line :
               interfaceoutput= line.decode()
               appendline += line.decode()
               if re.search('up', str(interfaceoutput)):
                   check_output += "Line Protocol is UP\n"
                   pingwithinterface="ping "+peerip+" count 10 packet-size 1500 interval 1"
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
                if re.search('100', str(peerpingoutput)):
                    check_output += "Peer Ping is OK\n"
            if b'Success' in line :
               appendline += line.decode()
        execute_command = subprocess.Popen([script_name, script_options, '-u', username, '-p', password, '-c', pingwithinterface, ci_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        command_output = execute_command.stdout.readlines()
        start_index = end_index = 0
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_nxosfile.txt", 'wb')
        file1.writelines(command_output)
        file1.close()
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_nxosfile.txt", 'rb')
        Lines = file1.readlines()
        for line in Lines:
            if b'Connection' not in line and b'=' not in line and b'spawn' not in line and b'exit' not in line and b'VTY' not in line and b'xit' not in line and b"'" not in line and b'password' not in line and b'CCCCCC' not in line :
                pinginterfaceoutput= line.decode()
                appendline += line.decode()
                if re.search('100', str(pinginterfaceoutput)):
                    check_output += "Peer Ping with interface is OK\n"
            if b'Success' in line :
               appendline += line.decode()

        #print(neighbouroutput)
        if re.search('Peer IP is present', str(check_output)) and re.search('Line Protocol is UP', str(check_output)) and re.search('Peer Ping is OK', str(check_output)) and re.search('Peer Ping with interface is OK', str(check_output)):
            print("Peer IP is present, Line Protocol is UP, Peer Ping is OK and Peer Ping with Interface is OK.")
        elif re.search('Peer IP is not present', str(check_output)):
              print("Peer IP is not present: {}".format(peerip))
        #print(check_output)
        print(appendline)
        #os.remove('/opt/stackstorm/packs/ntt_monitoring/actions/cpufile.txt')


    def run(self, username, password, ci_address, neighbour_command, peer_ip):
        neighbor_status = self.get_nxos(username, password, ci_address, neighbour_command, peer_ip)
        # using the os.path.exists() function to check the existence of the file
        #if os.path.exists("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_cpufile.txt"):
        #os.remove("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_nxosfile.txt")
           #print("File deleted successfully")
        #else:
           #print("File does not exist")
        return neighbor_status
#!/usr/bin/env python
from lib.base_action import BaseAction
import subprocess
import re
import os

class CheckOS(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(CheckOS, self).__init__(config)

    def check_version(self, username, password, ci_address, version_command):
        device_type = ''
        script_name = "/opt/stackstorm/packs/ntt_monitoring/actions/nw_clogin.sh"
        script_options = '-noenable'
        ip_address=b''
        ip_address=ci_address
        execute_command = subprocess.Popen([script_name, script_options, '-u', username, '-p', password, '-c', version_command, ci_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        command_output = execute_command.stdout.readlines()
        start_index = end_index = 0
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_checkos.txt", 'wb')
        file1.writelines(command_output)
        file1.close()
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_checkos.txt", 'rb')
        Lines = file1.readlines()
        for line in Lines:
            if b'Connection' not in line and b'=' not in line and b'spawn' not in line and b'exit' not in line and b'#' not in line and b'xit' not in line and b"'" not in line and b'password' not in line and b'CCCCCC' not in line :
                versionoutput = line.decode()
                if re.findall('IOS', versionoutput):
                    device_type = "IOS Device"
                    break
                if re.findall('NX-OS', versionoutput):
                    device_type = "Nexus Device"
                    break
        return device_type


    def run(self, username, password, ci_address, version_command):
        device_type = self.check_version(username, password, ci_address, version_command)
        os.remove("/opt/stackstorm/packs/ntt_monitoring/actions/"+ci_address+"_checkos.txt")
        return device_type

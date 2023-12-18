#!/usr/bin/env python
from lib.base_action import BaseAction
import subprocess
import re
import os

class Checkuptime(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(Checkuptime, self).__init__(config)

    def check_uptime_status(self, username, password, ci_address, uptime_command, inc_number):
        login_output = []
        script_name = "/opt/stackstorm/packs/ntt_monitoring/actions/nw_clogin.sh"
        script_options = '-noenable'
        #command = 'help'
        ip_address=b''
        ip_address=ci_address
        execute_command = subprocess.Popen([script_name, script_options, '-u', username, '-p', password, '-c', uptime_command, ci_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #print(execute_command)
        command_output = execute_command.stdout.readlines()
        #command_output = execute_command.stdout
        #print(command_output)
        #output_string=execute_command.split("\n", 1)[1]
        #print(output_string)
        start_index = end_index = 0
        #convert_command_output = self.convert_bytes_to_string(command_output)
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+inc_number+"_uptime_peer.txt", 'wb')
        file1.writelines(command_output)
        file1.close()
        file1 = open("/opt/stackstorm/packs/ntt_monitoring/actions/"+inc_number+"_uptime_peer.txt", 'rb')
        Lines = file1.readlines()
        for line in Lines:
          if re.findall(b'Switchover|unknown|LocalSoft|error|Illegal|Trap|Interrupt', line):
            print("One of the exception string like Switchover|unknown|LocalSoft|error|Illegal|Trap|Interrupt has occurred. Hence Escalate")
            break
          else:
            if b'Connection' not in line and b'=' not in line and b'spawn' not in line and b'exit' not in line and b'#' not in line and b'xit' not in line and b"'" not in line and b'password' not in line and b'CCCCCC' not in line :
                uptimeoutput= line.decode()
                if re.search('uptime', str(uptimeoutput)):
                   #uptimeline=uptimeline.decode()
                   week_string_pattern = r"\d\d week"
                   week_output=re.compile(week_string_pattern)
                   week_result=week_output.findall(uptimeoutput)
                   if ('week' in uptimeoutput) or ('weeks' in uptimeoutput):
                     print("Uptime is high")
                   elif ('day' in uptimeoutput) or ('days' in uptimeoutput):
                     print("Uptime is high")
                   elif ('hour' in uptimeoutput) or ('hours' in uptimeoutput):
                     print("Uptime is high")
                   elif ('minute' in uptimeoutput) or ('minutes' in uptimeoutput):
                        minute_string_pattern = r"\d\d minute"
                        minute_output=re.compile(minute_string_pattern)
                        minute_result=minute_output.findall(uptimeoutput)
                        if minute_result:
                           minute_result1=(minute_output.findall(uptimeoutput)[0]).split(" ")[0]
                           if int(minute_result1) > 30:
                              print("Uptime is high: "+minute_result1)
                           else:
                              print("Uptime is Low:"+minute_result1)
                        else:
                           print("Uptime is Low:"NA)
                   else:
                        print("Uptime is Low:"NA)                   
                   
                   #print(day_result)
                                       
                #print(uptimeoutput)
        #os.remove('/opt/stackstorm/packs/ntt_monitoring/actions/cpufile.txt')


    def run(self, username, password, ci_address, uptime_command, inc_number):
        connect_status = self.check_uptime_status(username, password, ci_address, uptime_command, inc_number)
        os.remove("/opt/stackstorm/packs/ntt_monitoring/actions/"+inc_number+"_uptime_peer.txt")
        return connect_status


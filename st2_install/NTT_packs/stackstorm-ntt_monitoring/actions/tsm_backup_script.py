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
# Developer : Anitha Janarthanan
from st2common.runners.base_action import Action
import paramiko
from fractions import Fraction
import subprocess
import os
import re


class TSMBackup(Action):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(TSMBackup, self).__init__(config)

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
        
    def substring_before(self, s, before):
        s = s.strip()
        s1 = s.partition(before)[0]
        s1 = s1.strip()
        return s1
        
    def ListToString(self, listinput):
        stringoutput = ''
        for line in listinput:
            stringoutput=stringoutput+ '\n' + line
        return stringoutput
       
    
    def get_ipaddress(self, command_result):
        ipaddress = ""
        FindAfter = self.substring_after(command_result,"(")        
        ipaddress = self.substring_before(FindAfter,")")
        ipaddress = ipaddress.strip()
        return ipaddress
        
    def system_info(self, command_result, affected_drive, ip_address):
        system_drive = ""
        notes = ""
        notes = notes + "Checking drive "+affected_drive+" in "+ip_address
        command_out = command_result.split("\n")
        for line in command_out:
            if 'SystemDrive' in line:
                FindAfter = self.substring_after(line,":")    
                system_drive = FindAfter.strip()
        
        if system_drive != "":
            notes = notes + ip_address +" is reachable and the System Drive has been identified as "+system_drive
        else:
            notes = notes + "Unable to connect to the machine and determine the system drive, Escalating the incident."
            
        return {'notes': notes,
                'SystemDrive': system_drive}
    
    def parse_dsm_content(self, command_result, affected_drive, ip_address, ci_name, path):
        notes = ""     
        PasswordGenerate = False  
        SchedLog = False       
        ErrorLog = False
        Domain = False
        NodeLog = False
        NodenameLog = False
        tcpserveraddress = False
        content = command_result.split("\n")
        notes = notes + "---------------------------------------\n"
        notes = notes + "TSM dsm.opt configuration verification:\n"
        notes = notes + "---------------------------------------\n"
        notes = notes + "path="+path+"\n"
        if command_result != '' and 'Exception' not in command_result:
            Node = "NodeName[ \t]*"+ci_name
            notes = notes + "Node="+Node
            for line in content:
                if 'schedlogname' in line.lower():
                    notes = notes + "SchedLog="+line+"\n"
                elif 'errorlogname' in line.lower():
                    notes = notes + "ErrorLog="+line+"\n"
                elif 'passwordaccess' in line.lower() and 'generate' in line.lower():
                    PasswordGenerate = True
                    notes = notes + "True password Generate is defined in the DSM.opt file"+"\n"
                elif 'schedlogretention' in line.lower():
                    SchedLog = True
                    notes = notes + "True SchedLog retention is defined in the DSM.opt file"+"\n"
                elif 'errorlogretention' in line.lower():
                    ErrorLog = True
                    notes = notes + "True ErrorLog retention is defined in the DSM.opt file"+"\n"
                elif 'DOMAIN' in line:
                    Domain = True
                    notes = notes + "True Domain is defined in the DSM.opt file"+"\n"
                    Domain = line
                    notes = notes + "Domain="+Domain+"\n"
                elif 'NODENAME' in line.upper():
                    NodeLog = True
                    notes = notes + "True Nodename option is defined in the DSM.opt file" +"\n"
                    Nodename = line                   
                elif 'tcpserveraddress' in line.upper():
                    tcpserveraddress = True
                    notes = notes + "True TSM Server Address is defined in the DSM.opt file"+"\n"
                    TCPAddress = line.split(' ')[1]
                    notes = notes + "TCPAddress="+TCPAddress+"\n"
                elif 'NODENAME' in line.upper() and ci_name.upper() in line.upper():
                    NodenameLog = True
                    notes = notes + "Nodename ("+Nodename+") is defined in the DSM.opt matches ESM Name ("+ci_name+") in the incident"+"\n"                    
                    
            if PasswordGenerate is False:
                notes = notes + "False password Generate option is not defined in the DSM.opt file"+"\n"
            if SchedLog is False:
                notes = notes + "False SchedLog Retention option is not defined in the DSM.opt file"+"\n"
            if ErrorLog is False:    
                notes = notes + "False ErrorLog Retention option is not defined in the DSM.opt file"+"\n"
            if Domain is False:    
                notes = notes + "False Domain option is not defined in the DSM.opt file"+"\n"
            if NodeLog is False:
                notes = notes + "False Nodename option is not defined in the DSM.opt file"+"\n"
            if tcpserveraddress is False:    
                notes = notes + "False TSM Server Address is not defined in the DSM.opt file"+"\n"
            if NodenameLog is False:    
                notes = notes + "Nodename ("+Nodename+") in DSM.opt file does not match the Name of the machine listed in the incident ("+ci_name+")" +"\n"                   
        else:
            notes = notes + "TSM dsm.opt configuration did not pass the health checks." +"\n"

        return notes 

    def tcp_session_check(self, ip_address):
        import socket
        notes = ""
        port=1500
        timeout_seconds=300
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout_seconds)
        result = sock.connect_ex((ip_address,int(port)))
        notes = notes + "---------------------------------------"+"\n"
        notes = notes + "Starting to check the port"+"\n"
        notes = notes + "---------------------------------------"+"\n"
        if result == 0:
           notes = notes + "TSM Server is accepting sessions."+"\n"
        else:
           notes = notes + "TSM Server is not accepting sessions."+"\n"
        sock.close() 
        return notes
  
    def get_backup_time(self, command_result, ip_address, affected_drive):
        ElapsedProcessingTime = self.substring_after(command_result , 'time:')
        ElapsedProcessingTime = ElapsedProcessingTime.strip()
        ProcessingTimeHours = ElapsedProcessingTime.split(':')[0]
        ProcessingTimeMins = ElapsedProcessingTime.split(':')[1]
        ProcessingTimeSeconds = ElapsedProcessingTime.split(':')[2]
        ProcessingTimeHours = int(ProcessingTimeHours) + 0.5
        BackupProcessingTimeMinutes = (ProcessingTimeHours * 60) + int(ProcessingTimeMins)
        return BackupProcessingTimeMinutes
        
    def arizona_time(self, ip_address):
        import pytz
        isarizona = "false"
        tz = pytz.timezone('Pacific/Johnston')
        ct = datetime.datetime.now(tz=tz)
        time = ct.isoformat()
        #2017-01-13T11:29:22.601991-05:00
        time = time.split('T')[1]
        time_hour = time.split(':')[0]
        time_mins = time.split(':')[1]
        arizonatimehours = int(time_hour) * 60
        arizonatimetotalmins = arizonatimehours + int(time_mins)
        if (arizonatimetotalmins == 540 and arizonatimetotalmins == 545):
            isarizona = "true"
        return isarizona
        
    def get_backup_name(self, detailed_desc):
        if 'failed in' in detailed_desc:
            FindAfter = self.substring_after(detailed_desc, 'failed in')
            backup_name = self.substring_before(FindAfter, ')')
            backup_name = backup_name.strip()
            
        if 'missed start window' in detailed_desc:
            FindAfter = self.substring_after(detailed_desc, 'missed start window')
            backup_name = self.substring_before(FindAfter, ')')
            backup_name = backup_name.strip()
            
        return backup_name
        
    def get_backup_processid(self, command_result):
        process_id = ""
        content = command_result.split('\n')
        for line in content:
            if 'ProcessId' in line:
                Find_After = self.substring_after(line, ':')
                process_id = Find_After.strip()
        return process_id
        
    def get_backup_notes(self, command_result):
        command_out = command_result.split("\n")
        backup_failure = ""
        backup_notes = ""
        for line in command_out:
            if 'finished with' in line and 'failure' in line:
                backup_failure = backup_failure + line+"\n"
            elif 'Total number of objects failed:' in line:
                backup_failure = backup_failure + line+"\n"
            elif 'Error processing' in line:
                backup_failure = backup_failure + line+"\n"
            elif 'Total number of objects inspected:' in line:
                backup_notes = backup_notes + line + "\n"
            elif 'Total number of objects backed up:' in line:
                backup_notes = backup_notes + line + "\n"
            elif 'Total number of objects updated:' in line:
                backup_notes = backup_notes + line + "\n"
            elif 'Total number of objects rebound:' in line:
                backup_notes = backup_notes + line + "\n"
            elif 'Total number of objects deleted:' in line:
                backup_notes = backup_notes + line + "\n"
            elif 'Total number of objects expired:' in line:
                backup_notes = backup_notes + line + "\n"
            elif 'Total number of objects failed:' in line:
                backup_notes = backup_notes + line + "\n"
            elif 'Total number of subfile objects:' in line:
                backup_notes = backup_notes + line + "\n"
            elif 'Total number of bytes transferred:' in line:
                backup_notes = backup_notes + line + "\n"
            elif 'Data transfer time:' in line:
                backup_notes = backup_notes + line + "\n"
            elif 'Network data transfer rate:' in line:
                backup_notes = backup_notes + line + "\n"
            elif 'Aggregate data transfer rate:' in line:
                backup_notes = backup_notes + line + "\n"
            elif 'Objects compressed by:' in line:
                backup_notes = backup_notes + line + "\n"
            elif 'Subfile objects reduced by:' in line:
                backup_notes = backup_notes + line + "\n"
            elif 'Elapsed processing time:' in line:
                backup_notes = backup_notes + line + "\n"                
                           
        return {'backup_failure': backup_failure,
                'backup_notes': backup_notes}
    
    def run(self, **kwargs):
        ip_address = kwargs['ip_address']
        activity = kwargs['activity']
        password = kwargs['password']
        username = kwargs['username']
        command_result = kwargs['command_result']
        affected_drive = kwargs['affected_drive']
        ci_name = kwargs['ci_name']
        detailed_desc = kwargs['detailed_desc']
        path = kwargs['path']
        if 'Ping' in activity: 
            output = self.get_ipaddress(command_result)
        if 'SystemInfo' in activity:
            output = self.system_info(command_result, affected_drive, ip_address)
        if 'parse-dsm-content' in activity:
            output = self.parse_dsm_content(command_result, affected_drive, ip_address, ci_name, path)
        if 'tcp_session_check' in activity:
            output = self.tcp_session_check(ip_address)
        if 'get_backup_time' in activity:
            output = self.get_backup_time(command_result, ip_address, affected_drive)
        if 'arizona_time' in activity:
            output = self.get_backup_time(ip_address)
        if 'get_backup_name' in activity:
            output = self.get_backup_name(detailed_desc)
        if 'get_backup_processid' in activity:
            output = self.get_backup_processid(command_result)
        if 'get_backup_notes' in activity:
            output = self.get_backup_notes(command_result)
        return output

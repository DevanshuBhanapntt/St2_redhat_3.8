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
import sys


class SNMPGetVendor(Action):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(SNMPGetVendor, self).__init__(config)

    def get_arg(self, key, kwargs_dict):
        if key in kwargs_dict:
            value = kwargs_dict[key]
            return value
        else:
            return None

    def get_vendor(self,
                   ip_addr,
                   version,
                   auth_key,
                   community,
                   nms_ip,
                   oid,
                   password,
                   port,
                   privacy,
                   priv_key,
                   protocol,
                   security,
                   username):
        if version == 'v2':
            if (community and ip_addr and oid):
                try:
                    snmp_sysdescr = subprocess.check_output("snmpget -v2c -c {} {} {} sysDescr.0"
                                                        .format(community,
                                                                ip_addr,
                                                                oid), shell=True, stderr=subprocess.STDOUT)
                    #snmp_sysdescr = snmp_sysdescr.decode()
                except subprocess.CalledProcessError as e:
                    print (e.output.decode())
                    sys.exit(e.returncode)
                snmp_sysdescr = snmp_sysdescr.decode()
            else:
                raise ValueError("SNMP v2 command is missing arguments."
                                 " Please check the parameters and try again")
        else:
            if (password and port and privacy and priv_key and protocol and security and username):
                try:    
                    snmp_sysdescr = subprocess.check_output("""snmpget -v3 -u {} -a {} -A '{}' -l {} -x {} -X '{}' {} .1.3.6.1.2.1.1.1.0 sysDescr.0""".format(username,protocol,auth_key,security,privacy,priv_key,ip_addr),shell=True,stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as e:
                    print (e.output.decode())
                    sys.exit(e.returncode)
                snmp_sysdescr = snmp_sysdescr.decode()
            else:
                raise ValueError("SNMP v3 command is missing arguments. "
                                 "Please check the parameters and try again")

        return snmp_sysdescr

    def parse_response(self, snmp_sysdescr):
        if "4032" in snmp_sysdescr:
            return "Dell"
        elif "Cisco" in snmp_sysdescr:
            return "Cisco"
        elif "Linux" in snmp_sysdescr:
            return "Cisco"
        elif "IOS" in snmp_sysdescr:
            return "IOS"
        elif "NX-OS" in snmp_sysdescr:
            return "NEXUS"
        elif "dell networking" in snmp_sysdescr:
            return "PowerConnect"


    def run(self, **kwargs):
        kwargs_dict = dict(kwargs)
        version = self.get_arg('snmp_version', kwargs_dict)
        ip_addr = self.get_arg('snmp_ip', kwargs_dict)
        oid = self.get_arg('snmp_oid', kwargs_dict)
        community = self.get_arg('snmp_community', kwargs_dict)
        auth_key = self.get_arg('snmp_auth_key', kwargs_dict)
        nms_ip = self.get_arg('nms_ip', kwargs_dict)
        password = self.get_arg('snmp_password', kwargs_dict)
        port = self.get_arg('snmp_port', kwargs_dict)
        privacy = self.get_arg('snmp_privacy', kwargs_dict)
        priv_key = self.get_arg('snmp_priv_key', kwargs_dict)
        protocol = self.get_arg('snmp_protocol', kwargs_dict)
        security = self.get_arg('snmp_security', kwargs_dict)
        username = self.get_arg('snmp_username', kwargs_dict)

        snmp_sysdescr = self.get_vendor(ip_addr,
                                        version,
                                        auth_key,
                                        community,
                                        nms_ip,
                                        oid,
                                        password,
                                        port,
                                        privacy,
                                        priv_key,
                                        protocol,
                                        security,
                                        username)
        vendor = self.parse_response(snmp_sysdescr)

        return vendor

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
# from lib.action_base import BaseAction
from st2common.runners.base_action import Action

import re


class OsVersionParse(Action):

    # Type of the OS
    # Values:
    #  - 'windows'
    #  - 'linux'
    #  - 'other'
    # map from string to array of strings that can create that symbol
    TYPES_MAP = {'windows': ['windows'],
                 'linux': ['linux', 'centos', 'fedora', 'rhel', 'ubuntu', 'debian'],
                 'other': []}

    # Distribution of the Linux OS (if type == 'linux')
    # Values:
    #  - 'centos'
    #  - 'fedora'
    #  - 'gentoo'
    #  - 'redhat'
    #  - 'suse'
    #  - 'debian'
    #  - 'ubuntu'
    #  - 'other'
    # map from string to array of strings that can create that symbol
    LINUX_DISTROS_MAP = {'centos': ['centos'],
                         'fedora': ['fedora'],
                         'gentoo': ['gentoo'],
                         'redhat': ['redhat', 'red hat', 'rhel'],
                         'suse': ['suse', 'sles'],
                         'debian': ['debian'],
                         'ubuntu': ['ubuntu'],
                         'other': []}

    # OS family types:
    #  - redhat = RHEL + Centos + Fedora
    #  - debian = Ubuntu + Debian
    #
    # map from string to array of strings that can create that symbol
    LINUX_FAMILY_MAP = {'gentoo': ['gentoo'],
                        'redhat': ['redhat', 'red hat', 'rhel', 'centos', 'fedora'],
                        'suse': ['suse', 'sles'],
                        'debian': ['debian', 'ubuntu'],
                        'other': []}

    # Version of the OS
    # Windows:
    #  - 'dos'
    #  - '3.1'
    #  - '95'
    #  - '98'
    #  - 'nt'
    #  - '2000'
    #  - 'xp'
    #  - 'vista'
    #  - '7'
    #  - '8'
    #  - '10'
    #  - 'server2003'
    #  - 'server2008'
    #  - 'server2012'
    #  - 'server2016'
    #  - 'other'
    #
    # Linux
    #  Some version number string matching the VERSION_NUM_REGEX regex.
    #
    # Version number regex to extract a version number from the @name
    # string.
    # http://stackoverflow.com/questions/8955657/regex-pattern-to-extract-version-number-from-string
    # \d  = digit [0-9]
    # \d+ = one or more digits
    # \.  = one dot
    # (\.\d+)* = zero or more occurences of dot-digits (.[0-9])
    # ( |$) = match space or end of line
    # Note: include once space on either side so we ensure the number is
    #       isolated because we don't want to match things like the 32 in 32-bit
    #       or the 64 in x64.
    # W605 = invalid escape sequence flake8 error that we want to ignore
    VERSION_NUM_REGEX = " \d+(\.\d+)*( |$)"  # noqa: W605

    # System architecture
    # Values:
    #  - 'x86'
    #  - 'x64'
    #  - 'other'
    # map from string to array of strings that can create that symbol
    ARCHS_MAP = {'x86': ['x86', '32-bit'],
                 'x64': ['x64', '64-bit'],
                 'other': []}

    def __init__(self, config):
        super(OsVersionParse, self).__init__(config)

    def find_str_in_map_or_other(self, string, map):
        """Tries to find 'string' in any of the values in 'map'. If it finds
        a value, then the key is returned where the match was found.
        Map is expected to be a dictionary where each value in the dictionary
        is a list.
        map = {'key1': ['value0', 'value1'],
               'key2': ['value3', 'value4']}
        :param string: the tring to search for in the map values
        :param map: map of lists of strings to look in
        :returns: the key where 'string' was found in a value, or if not found
        'other'
        :rtype: string
        """
        for key, value_array in list(map.items()):
            for value in value_array:
                if value in string:
                    return key
        return 'other'

    def parse_type(self, name_down):
        """ Find the "type" of the OS, either "linux" or "windows" by trying
        to find those keywords using the TYPES_MAP
        :param name_down: full name of the OS in all lowercase
        :returns: the type of the os based on the TYPES_MAP, or 'other'
        :rtype: string
        """
        return self.find_str_in_map_or_other(name_down, OsVersionParse.TYPES_MAP)

    def parse_linux_distro(self, name_down):
        """ Find the linux distro by trying to match keywords from the LINUX_DISTROS_MAP
        in 'name_down'
        :param name_down: full name of the OS in all lowercase
        :returns: the linux distro based on the LINUX_DISTROS_MAP, or 'other'
        :rtype: string
        """
        return self.find_str_in_map_or_other(name_down, OsVersionParse.LINUX_DISTROS_MAP)

    def parse_linux_family(self, name_down):
        """ Find the linux family by trying to match keywords from the LINUX_FAMILY_MAP
        in 'name_down'
        :param name_down: full name of the OS in all lowercase
        :returns: the linux distro based on the LINUX_FAMILY_MAP, or 'other'
        :rtype: string
        """
        return self.find_str_in_map_or_other(name_down, OsVersionParse.LINUX_FAMILY_MAP)

    def parse_arch(self, name_down):
        """ Find the architecture by trying to match keywords from the ARCHS_MAP
        in 'name_down'
        :param name_down: full name of the OS in all lowercase
        :returns: the architecture based on the ARCHS_MAP, or 'other'
        :rtype: string
        """
        return self.find_str_in_map_or_other(name_down, OsVersionParse.ARCHS_MAP)

    def parse_version(self, name_down, type):
        """ Parse the version of the OS based on what the 'type' is.
        :param name_down: full name of the OS in all lowercase
        :param type: type of the OS, either 'linux' or 'windows'
        :returns: the version of the OS parsed from 'name_down'
        :rtype: string
        """
        if type == 'windows':
            return self.parse_windows_version(name_down)
        elif type == 'linux':
            return self.parse_linux_version(name_down)
        return 'other'

    def get_version_num_str(self, name_down):
        """Try to match strings with the pattern (vmware):
           Red Hat Enterprise Linux 7.4
           Windows 2012 R2
           pattern = <os text> <version> <arch>

        If this fails then try to mach the string with the pattern (rhev):
            rhel_7.4_x64
            windows_2012_x64
            pattern = <distro>_<version>_<arch>
        :param name_down: full name of the OS in all lowercase
        :returns: the version of the OS (if a pattern is matched) otherwise None
        :rtype: string or None
        """
        match = re.search(OsVersionParse.VERSION_NUM_REGEX, name_down)
        if match:
            version_str = match.group()
            # remove spaces that were in the regex
            # W605 = invalid escape sequence flake8 error that we want to ignore
            return re.sub('\s', '', version_str)  # noqa: W605
        elif 'rhel' in name_down or 'windows' in name_down:
            # In RHEV the pattern of the string is:

            # split the distro from the version
            version_parts = name_down.split('_')
            if len(version_parts) > 1:
                version = version_parts[1]
                # return the version with out the architecture
                return version.split('x')[0]
        return None

    def parse_windows_version(self, name_down):
        """Pulls the windows verison information from 'name_down'.
        If a numeric version can't be found, then we attempt to match against
        text versions (vista, nt, xp, etc)

        :param name_down: full name of the OS in all lowercase
        :returns: the version of windows from 'name_down' or 'other'
        :rtype: string
        """

        version_num_str = self.get_version_num_str(name_down)
        version = 'other'
        if version_num_str:
            if version_num_str == '2019':
                version = 'server2019'
            elif version_num_str == '2016':
                version = 'server2016'
            elif version_num_str == '2012':
                version = 'server2012'
            elif version_num_str == '2008':
                version = 'server2008'
            elif version_num_str == '2003':
                version = 'server2003'
            elif version_num_str == '2000':
                version = '2000'
            elif version_num_str == '98':
                version = '98'
            elif version_num_str == '95':
                version = '95'
            elif version_num_str == '10':
                version = '10'
            elif version_num_str == '8':
                version = '8'
            elif version_num_str == '7':
                version = '7'
            elif version_num_str == '3.1':
                version = '3.1'
        else:
            if 'vista' in name_down:
                version = 'vista'
            elif 'xp' in name_down:
                version = 'xp'
            elif 'nt' in name_down:
                version = 'nt'
            elif 'dos' in name_down:
                version = 'dos'
        return version

    def parse_linux_version(self, name_down):
        """ Parse the version of the linux OS.
        :param name_down: full name of the OS in all lowercase
        :returns: the version of the OS parsed from 'name_down'
        :rtype: string
        """
        return self.get_version_num_str(name_down)

    def run(self, **kwargs):
        """

        :returns:
        :rtype: dict
        """
        kwargs_dict = dict(kwargs)
        name = kwargs_dict['os_name']
        name_down = name.lower()

        os_version = {'name': name}

        # parse type (windows/linux)
        os_version['type'] = self.parse_type(name_down)

        # parse linux distro (linux only)
        if os_version['type'] == 'linux':
            os_version['linux_distro'] = self.parse_linux_distro(name_down)
            os_version['linux_family'] = self.parse_linux_family(name_down)

        # parse version (2003, 7.4, nt)
        os_version['version'] = self.parse_version(name_down, os_version['type'])

        # parse architecture (x86, x64, etc)
        os_version['arch'] = self.parse_arch(name_down)

        # parse version number into parts (['7', '4'])
        if os_version['version']:
            version_parts = os_version['version'].split('.')
        else:
            version_parts = []
        os_version['version_parts'] = version_parts

        # parse major version number (ex: version='7.4', version_major='7')
        if len(version_parts) > 0:
            os_version['version_major'] = version_parts[0]
        else:
            os_version['version_major'] = "-1"

        # parse minor version number (ex: version='7.4', version_minor='4')
        if len(version_parts) > 1:
            os_version['version_minor'] = version_parts[1]
        else:
            os_version['version_minor'] = "-1"

        return os_version

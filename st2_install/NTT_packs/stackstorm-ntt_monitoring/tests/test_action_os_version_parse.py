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
from os_version_parse import OsVersionParse

from ntt_base_action_test_case import NTTBaseActionTestCase
from st2common.runners.base_action import Action

__all__ = [
    'OsVersionParseTestCase'
]


class OsVersionParseTestCase(NTTBaseActionTestCase):
    __test__ = True
    action_cls = OsVersionParse

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, OsVersionParse)
        self.assertIsInstance(action, Action)

    def test_find_str_in_map_or_other_found(self):
        action = self.get_action_instance({})
        test_dict = {'key0': ['123', '456'],
                     'key1': ['abc', 'def']}
        test_str = 'xx__abc__xx'
        expected_key = 'key1'

        result = action.find_str_in_map_or_other(test_str, test_dict)
        self.assertEqual(result, expected_key)

    def test_find_str_in_map_or_other_not_found(self):
        action = self.get_action_instance({})
        test_dict = {'key0': ['123', '456'],
                     'key1': ['abc', 'def']}
        test_str = 'xxxxxxxx'
        expected_key = 'other'

        result = action.find_str_in_map_or_other(test_str, test_dict)
        self.assertEqual(result, expected_key)

    def test_parse_type_linux(self):
        action = self.get_action_instance({})
        test_os = "red hat enterprise linux 7.4".lower()
        expected = 'linux'
        result = action.parse_type(test_os)
        self.assertEqual(result, expected)

    def test_parse_type_windows(self):
        action = self.get_action_instance({})
        test_os = "windows server 2012 R2".lower()
        expected = 'windows'
        result = action.parse_type(test_os)
        self.assertEqual(result, expected)

    def test_parse_type_other(self):
        action = self.get_action_instance({})
        test_os = "macosx sierra 11".lower()
        expected = 'other'
        result = action.parse_type(test_os)
        self.assertEqual(result, expected)

    def test_parse_linux_distro_centos(self):
        action = self.get_action_instance({})
        result = action.parse_linux_distro("centos 7.7 x64".lower())
        self.assertEqual(result, 'centos')

        result = action.parse_linux_distro("fedora 30 x64".lower())
        self.assertEqual(result, 'fedora')

        result = action.parse_linux_distro("Red Hat Enterprise linux 7.7 x64".lower())
        self.assertEqual(result, 'redhat')

        result = action.parse_linux_distro("Suse 19 x64".lower())
        self.assertEqual(result, 'suse')

        result = action.parse_linux_distro("Debian 12 x64".lower())
        self.assertEqual(result, 'debian')

        result = action.parse_linux_distro("Ubuntu 16.04 x64".lower())
        self.assertEqual(result, 'ubuntu')

    def test_parse_linux_distro_other(self):
        action = self.get_action_instance({})
        result = action.parse_linux_distro("macosx sierra 11".lower())
        self.assertEqual(result, 'other')

    def test_parse_linux_family_rhel(self):
        action = self.get_action_instance({})
        result = action.parse_linux_family("Red Hat Enterprise Linux 7.4 x86".lower())
        self.assertEqual(result, 'redhat')

        result = action.parse_linux_family("CentOS 7.4 x86".lower())
        self.assertEqual(result, 'redhat')

        result = action.parse_linux_family("Fedora 29 x64".lower())
        self.assertEqual(result, 'redhat')

    def test_parse_linux_family_debian(self):
        action = self.get_action_instance({})
        result = action.parse_linux_family("Debian 9 x64".lower())
        self.assertEqual(result, 'debian')

        result = action.parse_linux_family("Ubuntu 16.04 x64".lower())
        self.assertEqual(result, 'debian')

    def test_parse_arch_x86(self):
        action = self.get_action_instance({})
        test_os = "Red Hat Enterprise Linux 7.4 x86".lower()
        expected = 'x86'
        result = action.parse_arch(test_os)
        self.assertEqual(result, expected)

    def test_parse_arch_x64(self):
        action = self.get_action_instance({})
        test_os = "Red Hat Enterprise Linux 7.4 x64".lower()
        expected = 'x64'
        result = action.parse_arch(test_os)
        self.assertEqual(result, expected)

    def test_parse_arch_32bit(self):
        action = self.get_action_instance({})
        test_os = "Red Hat Enterprise Linux 7.4 32-bit".lower()
        expected = 'x86'
        result = action.parse_arch(test_os)
        self.assertEqual(result, expected)

    def test_parse_arch_64bit(self):
        action = self.get_action_instance({})
        test_os = "Red Hat Enterprise Linux 7.4 64-bit".lower()
        expected = 'x64'
        result = action.parse_arch(test_os)
        self.assertEqual(result, expected)

    def test_parse_arch_other(self):
        action = self.get_action_instance({})
        test_os = "Red Hat Enterprise Linux 7.4 SPARC".lower()
        expected = 'other'
        result = action.parse_arch(test_os)
        self.assertEqual(result, expected)

    def test_get_version_num_str_vmware_rhel(self):
        action = self.get_action_instance({})
        test_os = "Red Hat Enterprise Linux 7.4".lower()
        expected = '7.4'
        result = action.get_version_num_str(test_os)
        self.assertEqual(result, expected)

    def test_get_version_num_str_vmware_windows(self):
        action = self.get_action_instance({})
        test_os = "Windows 2012 R2".lower()
        expected = '2012'
        result = action.get_version_num_str(test_os)
        self.assertEqual(result, expected)

    def test_get_version_num_str_rhev_rhel(self):
        action = self.get_action_instance({})
        test_os = "rhel_7.4_x64".lower()
        expected = '7.4'
        result = action.get_version_num_str(test_os)
        self.assertEqual(result, expected)

    def test_get_version_num_str_rhev_windows(self):
        action = self.get_action_instance({})
        test_os = "windows_2012_x64".lower()
        expected = '2012'
        result = action.get_version_num_str(test_os)
        self.assertEqual(result, expected)

    def test_parse_linux_version_vmware(self):
        action = self.get_action_instance({})
        test_os = "Red Hat Enterprise Linux 7.4".lower()
        expected = '7.4'
        result = action.get_version_num_str(test_os)
        self.assertEqual(result, expected)

    def test_parse_linux_version_rhev(self):
        action = self.get_action_instance({})
        test_os = "rhel_7.4_x64".lower()
        expected = '7.4'
        result = action.get_version_num_str(test_os)
        self.assertEqual(result, expected)

    def test_parse_windows_version_2016(self):
        action = self.get_action_instance({})
        test_os = "Windows 2016".lower()
        expected = 'server2016'
        result = action.parse_windows_version(test_os)
        self.assertEqual(result, expected)

    def test_parse_windows_version_2012(self):
        action = self.get_action_instance({})
        test_os = "Windows 2012".lower()
        expected = 'server2012'
        result = action.parse_windows_version(test_os)
        self.assertEqual(result, expected)

    def test_parse_windows_version_2008(self):
        action = self.get_action_instance({})
        test_os = "Windows 2008".lower()
        expected = 'server2008'
        result = action.parse_windows_version(test_os)
        self.assertEqual(result, expected)

    def test_parse_windows_version_2003(self):
        action = self.get_action_instance({})
        test_os = "Windows 2003".lower()
        expected = 'server2003'
        result = action.parse_windows_version(test_os)
        self.assertEqual(result, expected)

    def test_parse_windows_version_2000(self):
        action = self.get_action_instance({})
        test_os = "Windows 2000".lower()
        expected = '2000'
        result = action.parse_windows_version(test_os)
        self.assertEqual(result, expected)

    def test_parse_windows_version_98(self):
        action = self.get_action_instance({})
        test_os = "Windows 98".lower()
        expected = '98'
        result = action.parse_windows_version(test_os)
        self.assertEqual(result, expected)

    def test_parse_windows_version_95(self):
        action = self.get_action_instance({})
        test_os = "Windows 95".lower()
        expected = '95'
        result = action.parse_windows_version(test_os)
        self.assertEqual(result, expected)

    def test_parse_windows_version_10(self):
        action = self.get_action_instance({})
        test_os = "Windows 10".lower()
        expected = '10'
        result = action.parse_windows_version(test_os)
        self.assertEqual(result, expected)

    def test_parse_windows_version_8(self):
        action = self.get_action_instance({})
        test_os = "Windows 8".lower()
        expected = '8'
        result = action.parse_windows_version(test_os)
        self.assertEqual(result, expected)

    def test_parse_windows_version_7(self):
        action = self.get_action_instance({})
        test_os = "Windows 7".lower()
        expected = '7'
        result = action.parse_windows_version(test_os)
        self.assertEqual(result, expected)

    def test_parse_windows_version_3_1(self):
        action = self.get_action_instance({})
        test_os = "Windows 3.1".lower()
        expected = '3.1'
        result = action.parse_windows_version(test_os)
        self.assertEqual(result, expected)

    def test_parse_windows_version_vista(self):
        action = self.get_action_instance({})
        test_os = "Windows Vista".lower()
        expected = 'vista'
        result = action.parse_windows_version(test_os)
        self.assertEqual(result, expected)

    def test_parse_windows_version_xp(self):
        action = self.get_action_instance({})
        test_os = "Windows XP".lower()
        expected = 'xp'
        result = action.parse_windows_version(test_os)
        self.assertEqual(result, expected)

    def test_parse_windows_version_nt(self):
        action = self.get_action_instance({})
        test_os = "Windows NT".lower()
        expected = 'nt'
        result = action.parse_windows_version(test_os)
        self.assertEqual(result, expected)

    def test_parse_windows_version_dos(self):
        action = self.get_action_instance({})
        test_os = "Windows DOS".lower()
        expected = 'dos'
        result = action.parse_windows_version(test_os)
        self.assertEqual(result, expected)

    def test_parse_version_windows(self):
        action = self.get_action_instance({})
        test_os = "Windows 2012 R2".lower()
        expected = 'server2012'
        result = action.parse_version(test_os, 'windows')
        self.assertEqual(result, expected)

    def test_parse_version_linux(self):
        action = self.get_action_instance({})
        test_os = "Red Hat Enterprise Linux 7.4 x64".lower()
        expected = '7.4'
        result = action.parse_version(test_os, 'linux')
        self.assertEqual(result, expected)

    def test_parse_version_other(self):
        action = self.get_action_instance({})
        test_os = "Solaris 11 x64".lower()
        expected = 'other'
        result = action.parse_version(test_os, 'other')
        self.assertEqual(result, expected)

    def test_run_linux_rhel(self):
        action = self.get_action_instance({})
        test_os = "Red Hat Enterprise Linux 7.4 x64"
        kwargs_dict = {'os_name': test_os}
        expected = {'name': test_os,
                    'type': 'linux',
                    'linux_distro': 'redhat',
                    'linux_family': 'redhat',
                    'version': '7.4',
                    'arch': 'x64',
                    'version_parts': ['7', '4'],
                    'version_major': '7',
                    'version_minor': '4'}
        result = action.run(**kwargs_dict)
        self.assertEqual(result, expected)

    def test_run_linux_ubuntu(self):
        action = self.get_action_instance({})
        test_os = "Ubuntu 16.04 x64"
        kwargs_dict = {'os_name': test_os}
        expected = {'name': test_os,
                    'type': 'linux',
                    'linux_distro': 'ubuntu',
                    'linux_family': 'debian',
                    'version': '16.04',
                    'arch': 'x64',
                    'version_parts': ['16', '04'],
                    'version_major': '16',
                    'version_minor': '04'}
        result = action.run(**kwargs_dict)
        self.assertEqual(result, expected)

    def test_run_windows(self):
        action = self.get_action_instance({})
        test_os = "Windows 2012 R2 64-bit"
        kwargs_dict = {'os_name': test_os}
        expected = {'name': test_os,
                    'type': 'windows',
                    'version': 'server2012',
                    'arch': 'x64',
                    'version_parts': ['server2012'],
                    'version_major': 'server2012',
                    'version_minor': '-1'}
        result = action.run(**kwargs_dict)
        self.assertEqual(result, expected)

    def test_run_other(self):
        action = self.get_action_instance({})
        test_os = "Mac OSX Sierra"
        kwargs_dict = {'os_name': test_os}
        expected = {'name': test_os,
                    'type': 'other',
                    'version': 'other',
                    'arch': 'other',
                    'version_parts': ['other'],
                    'version_major': 'other',
                    'version_minor': '-1'}
        result = action.run(**kwargs_dict)
        self.assertEqual(result, expected)

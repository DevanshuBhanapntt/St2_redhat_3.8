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
from st2tests.base import BaseSensorTestCase

from sensors.servicenow_incident_sensor import ServiceNowIncidentSensor
from st2reactor.sensor.base import PollingSensor
import mock
import yaml

__all__ = [
    'ServiceNowIncidentSensorTestCase'
]


class ServiceNowIncidentSensorTestCase(BaseSensorTestCase):
    __test__ = True
    sensor_cls = ServiceNowIncidentSensor

    def test_init(self):
        config = yaml.safe_load(self.get_fixture_content('config_good.yaml'))
        sensor = self.get_sensor_instance(config)
        self.assertIsInstance(sensor, ServiceNowIncidentSensor)
        self.assertIsInstance(sensor, PollingSensor)

    @mock.patch('sensors.servicenow_incident_sensor.Client')
    @mock.patch('sensors.servicenow_incident_sensor.socket')
    def test_setup(self, mock_socket, mock_client):
        config = yaml.safe_load(self.get_fixture_content('config_good.yaml'))
        sensor = self.get_sensor_instance(config)
        mock_socket.getfqdn.return_value = "st2_test"
        mock_client.return_value = "Client"
        expected_headers = {'Content-type': 'application/json',
                            'Accept': 'application/json'}
        sensor.setup()
        self.assertEqual(sensor.sn_username, 'snuser')
        self.assertEqual(sensor.sn_password, 'snpass')
        self.assertEqual(sensor.sn_url, 'test.service-now.com')
        self.assertEqual(sensor.servicenow_headers, expected_headers)
        self.assertEqual(sensor.st2_fqdn, 'st2_test')
        self.assertEqual(sensor.st2_client, 'Client')

    @mock.patch('sensors.servicenow_incident_sensor.ServiceNowIncidentSensor.check_incidents')
    @mock.patch('sensors.servicenow_incident_sensor.requests')
    def test_poll(self, mock_requests, mock_check_incidents):
        config = yaml.safe_load(self.get_fixture_content('config_good.yaml'))
        sensor = self.get_sensor_instance(config)
        sensor.sn_url = "test_sn_server"
        sensor.sn_username = "test_username"
        sensor.sn_password = "test_password"
        sensor.servicenow_headers = "test_headers"
        test_json_data = {
            'result': [
                {'number': 'test1'}
            ]
        }
        mock_request = mock.Mock()
        mock_request.raise_for_status = mock.Mock()
        mock_request.status_code = 200
        mock_request.json = mock.Mock(return_value=test_json_data)
        mock_requests.request.return_value = mock_request
        mock_check_incidents.return_value = 'test'

        sensor.poll()
        mock_check_incidents.assert_called_once_with([{'number': 'test1'}])

    @mock.patch('sensors.servicenow_incident_sensor.ServiceNowIncidentSensor.check_description')
    @mock.patch('sensors.servicenow_incident_sensor.requests')
    def test_check_incidents(self, mock_requests, mock_check_description):
        config = yaml.safe_load(self.get_fixture_content('config_good.yaml'))
        sensor = self.get_sensor_instance(config)
        test_incidents = [
            {
                'number': 'INC10957090'
            }
        ]
        mock_keys = mock.Mock(value="['INC9876', 'INC1234']")
        mock_st2_client = mock.MagicMock()
        mock_st2_client.keys.get_by_name.return_value = mock_keys
        sensor.st2_client = mock_st2_client
        mock_check_description.return_value = 'test_desctiption'

        sensor.check_incidents(test_incidents)
        mock_check_description.assert_called_once_with({'number': 'INC10957090'})

    @mock.patch('sensors.servicenow_incident_sensor.ServiceNowIncidentSensor.check_description')
    @mock.patch('sensors.servicenow_incident_sensor.requests')
    def test_check_incidents_multipe(self, mock_requests, mock_check_description):
        config = yaml.safe_load(self.get_fixture_content('config_good.yaml'))
        sensor = self.get_sensor_instance(config)
        test_incidents = [
            {
                'number': 'INC9876'
            },
            {
                'number': 'INC10957090'
            }
        ]
        mock_keys = mock.Mock(value="['INC9876', 'INC1234']")
        mock_st2_client = mock.MagicMock()
        mock_st2_client.keys.get_by_name.return_value = mock_keys
        sensor.st2_client = mock_st2_client
        mock_check_description.return_value = 'test_desctiption'

        sensor.check_incidents(test_incidents)
        mock_check_description.assert_called_once_with({'number': 'INC10957090'})

    @mock.patch('sensors.servicenow_incident_sensor.base_action.BaseAction.sn_api_call')
    def test_get_company_and_ag(self, mock_api_call):
        config = yaml.safe_load(self.get_fixture_content('config_good.yaml'))
        sensor = self.get_sensor_instance(config)
        test_inc = {
            'number': 'INC10957090',
            'description': '1.1.1.1 is not responding to ping',
            'short_description': 'short description',
            'sys_id': '123456',
            'assignment_group': {
                'link': 'test.service-now.com',
                'value': '123'
            },
            'company': {
                'link': 'company.service-now.com',
                'value': '321'
            }
        }

        test_assign_group = {'name': 'group1', 'id': '123'}
        test_company = {'name': 'comp1', 'id': '321'}
        mock_api_call.side_effect = [test_assign_group, test_company]

        expected_result = ('group1', 'comp1')

        result = sensor.get_company_and_ag(test_inc)
        self.assertEqual(result, expected_result)
        mock_api_call.assert_has_calls = [
            mock.call(method='GET', url='test.service-now.com'),
            mock.call(method='GET', url='company.service-now.com')
        ]

    @mock.patch('sensors.servicenow_incident_sensor.ServiceNowIncidentSensor.get_company_and_ag')
    def test_check_description_ping_windows(self, mock_get_comp_ag):
        config = yaml.safe_load(self.get_fixture_content('config_good.yaml'))
        sensor = self.get_sensor_instance(config)
        test_incidents = {
            'number': 'INC10957090',
            'description': '1.1.1.1 is not responding to ping',
            'short_description': 'short description',
            'sys_id': '123456',
            'assignment_group': {
                'link': 'test.service-now.com',
                'value': '123'
            },
            'company': {
                'link': 'company.service-now.com',
                'value': '321'
            }
        }

        mock_get_comp_ag.return_value = ('intel-test', 'comp1')

        test_trigger_payload = {
            'assignment_group': 'intel-test',
            'check_uptime': True,
            'ci_address': '1.1.1.1',
            'customer_name': 'comp1',
            'detailed_desc': '1.1.1.1 is not responding to ping',
            'inc_number': 'INC10957090',
            'inc_sys_id': '123456',
            'os_type': 'windows',
            'short_desc': 'short description'
        }

        sensor.check_description(test_incidents)
        self.assertTriggerDispatched(trigger='ntt_itsm.unreachable_ping',
                                     payload=test_trigger_payload)

    @mock.patch('sensors.servicenow_incident_sensor.ServiceNowIncidentSensor.get_company_and_ag')
    def test_check_description_linux(self, mock_get_comp_ag):
        config = yaml.safe_load(self.get_fixture_content('config_good.yaml'))
        sensor = self.get_sensor_instance(config)
        test_incidents = {
            'number': 'INC10957090',
            'description': '1.1.1.1 is not responding to ping',
            'short_description': 'short description',
            'sys_id': '123456',
            'assignment_group': {
                'link': 'test.service-now.com',
                'value': '123'
            },
            'company': {
                'link': 'company.service-now.com',
                'value': '321'
            }
        }

        mock_get_comp_ag.return_value = ('linux-test', 'comp1')

        test_trigger_payload = {
            'assignment_group': 'linux-test',
            'check_uptime': True,
            'ci_address': '1.1.1.1',
            'customer_name': 'comp1',
            'detailed_desc': '1.1.1.1 is not responding to ping',
            'inc_number': 'INC10957090',
            'inc_sys_id': '123456',
            'os_type': 'linux',
            'short_desc': 'short description'
        }

        sensor.check_description(test_incidents)
        self.assertTriggerDispatched(trigger='ntt_itsm.unreachable_ping',
                                     payload=test_trigger_payload)

    @mock.patch('sensors.servicenow_incident_sensor.ServiceNowIncidentSensor.get_company_and_ag')
    def test_check_description_cpu(self, mock_get_comp_ag):
        config = yaml.safe_load(self.get_fixture_content('config_good.yaml'))
        sensor = self.get_sensor_instance(config)
        test_incidents = {
            'number': 'INC10957090',
            'description': 'cpu utilization on 1.1.1.1 , th is 5%',
            'short_description': 'short description',
            'sys_id': '123456',
            'assignment_group': {
                'link': 'test.service-now.com',
                'value': '123'
            },
            'company': {
                'link': 'company.service-now.com',
                'value': '321'
            }
        }

        mock_get_comp_ag.return_value = ('intel-test', 'comp1')

        test_trigger_payload = {
            'assignment_group': 'intel-test',
            'ci_address': '1.1.1.1',
            'cpu_name': '_total',
            'cpu_type': 'ProcessorTotalProcessorTime',
            'customer_name': 'comp1',
            'detailed_desc': 'cpu utilization on 1.1.1.1 , th is 5%',
            'inc_number': 'INC10957090',
            'inc_sys_id': '123456',
            'os_type': 'windows',
            'short_desc': 'short description',
            'threshold_percent': '5'
        }

        sensor.check_description(test_incidents)
        self.assertTriggerDispatched(trigger='ntt_itsm.high_cpu',
                                     payload=test_trigger_payload)

    @mock.patch('sensors.servicenow_incident_sensor.ServiceNowIncidentSensor.get_company_and_ag')
    def test_check_description_memory_uasge(self, mock_get_comp_ag):
        config = yaml.safe_load(self.get_fixture_content('config_good.yaml'))
        sensor = self.get_sensor_instance(config)
        test_incidents = {
            'number': 'INC10957090',
            'description': 'memory usage on 1.1.1.1',
            'short_description': 'short description',
            'sys_id': '123456',
            'assignment_group': {
                'link': 'test.service-now.com',
                'value': '123'
            },
            'company': {
                'link': 'company.service-now.com',
                'value': '321'
            }
        }

        mock_get_comp_ag.return_value = ('intel-test', 'comp1')

        test_trigger_payload = {
            'assignment_group': 'intel-test',
            'ci_address': '1.1.1.1',
            'inc_number': 'INC10957090',
            'inc_sys_id': '123456',
            'customer_name': 'comp1',
            'detailed_desc': 'memory usage on 1.1.1.1',
            'memory_threshold': None,
            'os_type': 'linux',
            'short_desc': 'short description'
        }

        sensor.check_description(test_incidents)
        self.assertTriggerDispatched(trigger='ntt_itsm.high_memory',
                                     payload=test_trigger_payload)

    @mock.patch('sensors.servicenow_incident_sensor.ServiceNowIncidentSensor.get_company_and_ag')
    def test_check_description_memory_used(self, mock_get_comp_ag):
        config = yaml.safe_load(self.get_fixture_content('config_good.yaml'))
        sensor = self.get_sensor_instance(config)
        test_incidents = {
            'number': 'INC10957090',
            'description': 'memory used on 1.1.1.1 , th is 5%',
            'short_description': 'short description',
            'sys_id': '123456',
            'assignment_group': {
                'link': 'test.service-now.com',
                'value': '123'
            },
            'company': {
                'link': 'company.service-now.com',
                'value': '321'
            }
        }

        mock_get_comp_ag.return_value = ('intel-test', 'comp1')

        test_trigger_payload = {
            'assignment_group': 'intel-test',
            'ci_address': '1.1.1.1',
            'inc_number': 'INC10957090',
            'inc_sys_id': '123456',
            'customer_name': 'comp1',
            'detailed_desc': 'memory used on 1.1.1.1 , th is 5%',
            'memory_threshold': '5',
            'os_type': 'linux',
            'short_desc': 'short description'
        }

        sensor.check_description(test_incidents)
        self.assertTriggerDispatched(trigger='ntt_itsm.high_memory',
                                     payload=test_trigger_payload)

    @mock.patch('sensors.servicenow_incident_sensor.ServiceNowIncidentSensor.get_company_and_ag')
    def test_check_description_disk(self, mock_get_comp_ag):
        config = yaml.safe_load(self.get_fixture_content('config_good.yaml'))
        sensor = self.get_sensor_instance(config)
        test_incidents = {
            'number': 'INC10957090',
            'description': 'C: logical disk free space on 1.1.1.1 , th is 5%',
            'short_description': 'short description',
            'sys_id': '123456',
            'assignment_group': {
                'link': 'test.service-now.com',
                'value': '123'
            },
            'company': {
                'link': 'company.service-now.com',
                'value': '321'
            }
        }

        mock_get_comp_ag.return_value = ('intel-test', 'comp1')

        test_trigger_payload = {
            'assignment_group': 'intel-test',
            'ci_address': '1.1.1.1',
            'inc_number': 'INC10957090',
            'customer_name': 'comp1',
            'detailed_desc': 'C: logical disk free space on 1.1.1.1 , th is 5%',
            'disk_name': 'C',
            'inc_sys_id': '123456',
            'os_type': 'windows',
            'threshold_percent': '5',
            'short_desc': 'short description'
        }

        sensor.check_description(test_incidents)
        self.assertTriggerDispatched(trigger='ntt_itsm.high_disk',
                                     payload=test_trigger_payload)

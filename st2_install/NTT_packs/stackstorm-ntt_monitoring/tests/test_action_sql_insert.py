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
from ntt_base_action_test_case import NTTBaseActionTestCase
import datetime
from sqlalchemy.engine.url import URL
import decimal

import mock

from sql_insert import SQLInsert
from st2common.runners.base_action import Action

__all__ = [
    'SQLInsertTestCase'
]


class SQLInsertTestCase(NTTBaseActionTestCase):
    __test__ = True
    action_cls = SQLInsert

    def test_init(self):
        action = self.get_action_instance(self.config_good)
        self.assertIsInstance(action, SQLInsert)
        self.assertIsInstance(action, Action)

    def test_convert_timestamp(self):
        action = self.get_action_instance(self.config_good)
        result = action.convert_timestamp('2021-06-16 20:08:24.586607+00:00')
        self.assertEqual(result, datetime.datetime(2021, 6, 16, 20, 8, 24, 586607))

    def test_row_to_dict(self):
        action = self.get_action_instance(self.config_good)
        test_row = mock.Mock(test1='value', test2='value2')
        test_row.keys.return_value = ['test1', 'test2']
        expected_result = {
            'test1': 'value',
            'test2': 'value2'
        }
        result = action.row_to_dict(test_row)
        self.assertEqual(result, expected_result)

    def test_row_to_dict_unit_convert(self):
        action = self.get_action_instance(self.config_good)
        test_row = mock.Mock(teststring='value',
                            testinteger=1,
                            testdecimal=decimal.Decimal('5.543'),
                            testfloat=2.352,
                            testdict={'test': 'value'},
                            testdatetime=datetime.datetime(2019, 1, 1, 0, 0))
        test_row.keys.return_value = ['teststring',
                                    'testinteger',
                                    'testdecimal',
                                    'testfloat',
                                    'testdict',
                                    'testdatetime']
        expected_result = {
            'testinteger': 1,
            'testdict': {'test': 'value'},
            'testdecimal': 5.543,
            'teststring': 'value',
            'testdatetime': '2019-01-01T00:00:00',
            'testfloat': 2.352
        }
        result = action.row_to_dict(test_row)
        self.assertEqual(result, expected_result)

    def test_format_data(self):
        action = self.get_action_instance(self.config_good)
        test_dict = {"key1": "value1",
                     "key2": "value2"}
        expected_result = "@key1='value1',@key2='value2'"
        result = action.format_data(test_dict)
        self.assertEqual(result, expected_result)

    def test_format_data_none(self):
        action = self.get_action_instance(self.config_good)
        test_dict = {}
        expected_result = ""
        result = action.format_data(test_dict)
        self.assertEqual(result, expected_result)

    def test_build_connection(self):
        action = self.get_action_instance(self.config_good)
        test_dict = {
            'host': 'test_host',
            'username': 'test_username',
            'password': 'test_password',
            'database': 'test_database',
            'port': 1,
            'drivername': 'mssql'
        }

        result = action.build_connection(**test_dict)

        test_dict['drivername'] = 'mssql+pymssql'
        expected_output = URL(**test_dict)

        self.assertEqual(result, expected_output)

    def test_sql_run_procedure_return_rows(self):
        action = self.get_action_instance(self.config_good)

        mock_session = mock.Mock()
        test_row = mock.Mock(test1='value', test2='value2')
        test_row.keys.return_value = ['test1', 'test2']
        mock_exec = mock.Mock(rowcount=1, returns_rows=True)
        mock_exec.fetchall.return_value = [test_row]
        mock_session.execute.return_value = mock_exec
        mock_session.commit.return_value = "Rows commited"
        mock_session.close.return_value = "Session closed"
        mock_session.rollback.return_value = "Transactions rolled back"
        expected_value = [{'test1': 'value', 'test2': 'value2'}]

        result = action.sql_run_procedure(mock_session, "this is a test")
        self.assertEqual(result, expected_value)

    def test_sql_run_procedure(self):
        action = self.get_action_instance(self.config_good)

        mock_session = mock.Mock()
        mock_exec = mock.Mock(rowcount=1, returns_rows=False)
        mock_session.execute.return_value = mock_exec
        mock_session.commit.return_value = "Rows commited"
        mock_session.close.return_value = "Session closed"
        mock_session.rollback.return_value = "Transactions rolled back"
        expected_value = {'affected_rows': 1}

        result = action.sql_run_procedure(mock_session, "this is a test")
        self.assertEqual(result, expected_value)

    def test_return_details_data(self):
        action = self.get_action_instance(self.config_good)
        test_dict = {"name": "value1",
                     "value": "value2",
                     "metric_id": "1"}
        expected_result = "@Name='value1',@Value='value2',@Metric_ID='1'"
        result = action.return_details_data(**test_dict)
        self.assertEqual(result, expected_result)

    @mock.patch('sql_insert.SQLInsert.sql_run_procedure')
    @mock.patch('sql_insert.sessionmaker')
    @mock.patch('sql_insert.sqlalchemy')
    def test_run(self, mock_sqlalchemy, mock_sessionmaker, mock_procedure):
        action = self.get_action_instance(self.config_good)
        test_dict = {
            'account_name': 'test_account',
            'account_service': 'test_account_service',
            'configuration_item': 'test_configuration_item',
            'end_timestamp': '2021-06-16 20:11:39.089285+00:00',
            'incident_id': 'test_incident_id',
            'metric_data': {
                'test': 'value'
            },
            'metric_procedure': 'test_metric_procedure',
            'metric_detail_procedure': 'test_metric_detail_procedure',
            'process_data': {
                'test1': 'value1'
            },
            'process_procedure': 'test_process_procedure',
            'start_timestamp': '2021-06-16 20:08:24.586607+00:00',
            'host': 'test_host',
            'username': 'test_username',
            'password': 'test_password',
            'database': 'test_database',
            'port': 1,
            'drivername': 'mssql'
        }

        mock_sqlalchemy.create_engine.return_value = 'Mock Engine'
        mock_session = mock.Mock()
        mock_sessionmaker().return_value = mock_session
        mock_procedure.side_effect = [
            [{'METRIC_ID': '1'}],
            'test',
            ['test1'],
            ['test2'],
            {'name': 'test3'},
            ['test4']
        ]
        expected_result = [{'METRIC_ID': '1'}, 'test', 'test1', 'test2', {'name': 'test3'}, 'test4']

        result = action.run(**test_dict)
        self.assertEqual(result, expected_result)

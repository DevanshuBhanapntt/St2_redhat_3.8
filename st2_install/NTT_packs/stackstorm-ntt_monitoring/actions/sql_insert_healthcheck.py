#!/usr/bin/env python
# Copyright 2019 NTT Technologies
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
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
import decimal
import datetime

DEFAULT_KNOWN_DRIVER_CONNECTORS = {
    'postgresql': 'postgresql+psycopg2',
    'mysql': 'mysql+pymysql',
    'oracle': 'oracle+cx_oracle',
    'mssql': 'mssql+pymssql',
    'firebird': 'firebird+fdb'
}


class SQLInserthealthcheck(Action):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(SQLInserthealthcheck, self).__init__(config)

    def convert_timestamp(self, timestamp):
        # remove timezone overlap
        trim_timezone = timestamp.split("+")[0]
        datetime_object = datetime.datetime.strptime(trim_timezone, '%Y-%m-%d %H:%M:%S.%f')

        return datetime_object

    def row_to_dict(self, row):
        """When SQLAlchemy returns information from a query the rows are
        tuples and have some data types that need to be converted before
        being returned.
        returns: dictionary of values
        """
        return_dict = {}
        for column in row.keys():
            value = getattr(row, column)

            if isinstance(value, datetime.date):
                return_dict[column] = value.isoformat()
            elif isinstance(value, decimal.Decimal):
                return_dict[column] = float(value)
            else:
                return_dict[column] = value

        return return_dict

    def format_data(self, proc_data_obj):
        proc_data_string = ""
        if proc_data_obj:
            proc_data_list = []
            for name, value in proc_data_obj.items():
                proc_data_list.append("@{0}='{1}'".format(name, value))

            proc_data_string = ",".join(proc_data_list)

        return proc_data_string

    def build_connection(self, drivername, database, host, password, port, username):
        connection = {
            'host': host,
            'username': username,
            'password': password,
            'database': database,
            'port': port,
            'drivername': drivername
        }

        # Update Driver with a connector
        default_driver = DEFAULT_KNOWN_DRIVER_CONNECTORS.get(connection['drivername'], None)
        if default_driver:
            connection['drivername'] = default_driver

        # Format the connection string
        return URL(**connection)

    def sql_run_procedure(self, session, exec_stmt):
        return_result = None
        try:
            exec_result = session.execute(exec_stmt)

            if exec_result.returns_rows:
                return_result = []
                all_results = exec_result.fetchall()
                for row in all_results:
                    # Rows are returned as tuples with keys.
                    # Convert that to a dictionary for return
                    return_result.append(self.row_to_dict(row))
            else:
                return_result = {'affected_rows': exec_result.rowcount}

            session.commit()
        except Exception as error:
            session.rollback()

            # Return error to the user
            raise error
        finally:
            session.close()

        return return_result

    def run(self,                        
            database,
            drivername,
            host,
            username,
            password,
            port,
            HCAuditLog_procedure,
            HCMetric_procedure,
            HCAuditLog_data,
            HCMetric_data):
        database_connection_string = self.build_connection(drivername,
                                                           database,
                                                           host,
                                                           password,
                                                           port,
                                                           username)
        engine = sqlalchemy.create_engine(database_connection_string)
        session = sessionmaker(bind=engine)()
        # Execute the HealthCheck Audit log procedure
        HCAuditLog_stmt = "EXEC {} {}".format(HCAuditLog_procedure, self.format_data(HCAuditLog_data))        
        HCAuditLog_return = self.sql_run_procedure(session, HCAuditLog_stmt)       
        HealthCheckID = HCAuditLog_return[0]['HealthCheckID']
        # Adding the HealthCheckID into the HCMetric_data object       
        HCMetric_data['HealthCheckID'] = HealthCheckID 
        # Execute the HealthCheck metric data procedure
        HCMetric_stmt = "EXEC {} {}".format(HCMetric_procedure, self.format_data(HCMetric_data))
        HCMetric_return = self.sql_run_procedure(session, HCMetric_stmt)       
        return HealthCheckID

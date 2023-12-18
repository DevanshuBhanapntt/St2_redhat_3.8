#!/usr/bin/env python
##################################
# Developer : Nalinikant Mohanty
# This action is used to get the DB whitespace and Incremental Back Up days.
# If threshold for any of the feature is breached then its a failure
# If your account does not have either DB whitespace or Incremental Back Up check then comment the piece of code below
# Respective section has been indicated with commented line below.
##################################
from lib.base_action import BaseAction
from bs4 import BeautifulSoup
from st2client.models.keyvalue import KeyValuePair
import datetime
import re




class ExchangeHealthCheck(BaseAction):
    def __init__(self, config):
        """Creates a new Action given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new Action
        """
        super(ExchangeHealthCheck, self).__init__(config)

    def Threshold_check(self, HTML_doc):
        data_list = []
        data_list_sorted = []
        # worknotes_db_space = "Whitespce Logs: \n"
        # worknotes_db_backup = "\nIncremental Backup Logs:"
        config_item_dict = {}
        db_whitespace_th = 30
        db_incremental_th = 2

        server_index = HTML_doc.find("<th>Server</th>")
        data = HTML_doc[server_index:len(HTML_doc)]
        newDoc = "<html><body><table><tr>" + data
        S = BeautifulSoup(newDoc, "html.parser")
        HTML_rows = S.find_all('tr')

        for row in HTML_rows:
            table_data = row.find_all('td')
            if len(table_data) > 0:
                data_len = len(table_data)
                data_dict = dict()
                if data_len == 10 or data_len == 9:
                    data_dict["server"] = table_data[0].text
                    data_dict["database"] = table_data[1].text
                    data_dict["db_size"] = re.sub("[^\d\.]", "", table_data[4].text)
                    data_dict["db_whitespace"] = re.sub("[^\d\.]", "", table_data[5].text)
                    if data_len == 10:
                        backup_date = table_data[8].text

                        if 'AM' in backup_date:
                            filtered_backup_date = backup_date.replace('AM', '').strip()

                        elif 'PM' in backup_date:
                            backup_date = backup_date.replace('PM', '').strip()
                            date = backup_date.split(' ')[0]
                            time = backup_date.split(' ')[1]
                            hour = time.split(':')[0]
                            if int(hour) < 12:
                                new_time = ''
                                actual_hour = 12 + int(hour)
                                if len(hour) == 1:
                                    new_time = str(actual_hour) + time[1:]
                                elif len(hour) == 2:
                                    new_time = str(actual_hour) + time[2:]

                                filtered_backup_date = date + ' ' + new_time
                            else:
                                filtered_backup_date = backup_date
                        else:
                            filtered_backup_date = backup_date
                        data_dict["db_backup"] = filtered_backup_date

                    data_list.append(data_dict)

        for d in data_list:
            i = 0
            s = frozenset(d.items())
            for ds in data_list_sorted:
                fs = frozenset(ds.items())
                if hash(s) == hash(fs):
                    i = i + 1
            if i == 0:
                data_list_sorted.append(d)

        # DB Whitespace Check (If not required please comment the whole for loop below)
        for list in data_list_sorted:
            worknotes_db_space = ''
            if len(list) != 0:
                traverse_list_server = list.get("server")
                traverse_list_db = list.get("database")
                traverse_list_db_space = list.get("db_whitespace")
                traverse_list_db_size = list.get("db_size")

                if float(traverse_list_db_size) != 0.0:
                    traverse_list_db_space = float(traverse_list_db_space)
                    traverse_list_db_size = float(traverse_list_db_size)
                    whitespace = (traverse_list_db_space / traverse_list_db_size) * 100
                    if float(whitespace) >= float(db_whitespace_th):
                        worknotes_db_space = "Whitespace for database: {} of server: {} is : {}. It is more than threshold level of: {}. \n".format(
                            str(traverse_list_db), str(traverse_list_server), str(whitespace), str(db_whitespace_th))

                        if traverse_list_server not in config_item_dict:
                            config_item_dict[str(traverse_list_server)] = worknotes_db_space
                        else:
                            failed_dbs = config_item_dict[traverse_list_server]
                            failed_dbs = failed_dbs + worknotes_db_space
                            config_item_dict[str(traverse_list_server)] = failed_dbs

        # DB Whitespace check ends

        # Incremental Back Up check (If not required please comment the whole for loop below)
        for list in data_list_sorted:
            worknotes_db_backup = ''
            if len(list) != 0:
                traverse_list_server = list.get("server")
                traverse_list_db = list.get("database")
                traverse_list_db_backup = list.get("db_backup")

                if traverse_list_db_backup:
                    new_traverse_list_db_backup = datetime.datetime.strptime(traverse_list_db_backup,
                                                                             "%m/%d/%Y %H:%M:%S")
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    now_date = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
                    delta = now_date - new_traverse_list_db_backup
                    days = int(delta.days)

                    if days >= db_incremental_th:

                        worknotes_db_backup = "Incremental Backup for database: {} of server: {} is : {}. It is more than threshold level of: {} days. \n".format(
                            str(traverse_list_db), str(traverse_list_server), str(traverse_list_db_backup),
                            str(db_incremental_th))

                        if traverse_list_server not in config_item_dict:
                            config_item_dict[str(traverse_list_server)] = worknotes_db_backup
                        else:
                            failed_dbs = config_item_dict[traverse_list_server]
                            failed_dbs = failed_dbs + worknotes_db_backup
                            config_item_dict[(traverse_list_server)] = failed_dbs

        # Incremental Back Up check ends

        return config_item_dict


    def run(self, HTML_doc):
        #fh = open("/opt/stackstorm/Test.html", 'r')
        #HTML_doc = fh.read()
        #fh.close()
        config_item_dict = {}
        ci_list = []
        if len(HTML_doc) > 0:
            config_item_dict = self.Threshold_check(HTML_doc)
            ci_list = list(config_item_dict.keys())
    
        return {'config_item': config_item_dict, 'ci_list': ci_list}


#!/bin/bash
servicename=$PT_servicename
OS_Type=$(uname);

####Linux Section####
if [[ "$OS_Type" == "Linux" ]]
then
    #check Redhat Linux version
         chk_version=$(cat /etc/redhat-release)
         echo -e "\nThe Redhat Linux version : \n$chk_version\n"
                if [[ "$chk_version" =~ "6" ]]
                then
                        echo -e "\nThe Redhat Linux version of this machine falls under Redhat family version 6.\n"
                        ver=6
                #NTPD Service Remediation Steps
                        if [[ "$servicename" == "ntpd" ]]
                        then
                                #check NTPD Service
                                chk_ntpd=$(sudo service ntpd status)
                                echo -e "\nThe status of the NTPD service is as follows: \n$chk_ntpd\n"
                                if [[ "$chk_ntpd" =~ "running" ]]
                                then
                                        echo -e "Current Time: `date`\n"
                                        echo -e "\nThe NTPD service is running...No further remediation steps required\n"
                                        echo -e "\nStatus: Success\n"
                                else
                                    echo -e "Current Time: `date`\n"
                                        echo -e "\nThe NTPD service is not running currently. Automation will perform the remediation steps to start the NTPD service.\n"
                                        start_ntpd=$(sudo service ntpd start)
                                        if [[ "$start_ntpd" =~ "OK" ]]
                                        then
                                                echo -e "Current Time: `date`\n"
                                                echo -e "\nAutomation has successfully started the NTPD service. \nThe NTPD status is as follows: \n$start_ntpd \n"
                                                echo -e "\nAutomation will monitor the NTPD service status for 5 minutes...\n"
                                                sleep 300;
                                                chk_ntpd=$(sudo service ntpd status)
                                                        echo -e "Current Time: `date`\n"
                                                        echo -e "\nThe status of the NTPD service is as follows: \n$chk_ntpd\n"
                                                        if [[ "$chk_ntpd" =~ "running" ]]
                                                        then
                                                                echo -e "\nAfter monitoring for 5 minutes, the NTPD status is running...\n"
                                                                echo -e "\nStatus: Success\n"
                                                        fi
                                                        if [[ "$chk_ntpd" =~ "stopped" ]]
                                                        then
                                                                echo -e "\nAfter monitoring for 5 minutes, the NTPD status is not running...\n"
                                                                echo -e "\nStatus: Failed\n"
                                                        fi
                                        else
                                        echo -e "\nAutomation failed to start the NTPD service.\n"
                                        fi
                                fi
                        fi
                #CROND Service Remediation Steps
                        if [[ "$servicename" == "crond" ]]
                        then
                                #check CROND Service
                                chk_crond=$(sudo service crond status)
                                echo -e "\nThe status of the CROND service is as follows: \n$chk_crond\n"
                                if [[ "$chk_crond" =~ "running" ]]
                                then
                                        echo -e "Current Time: `date`\n"
                                        echo -e "\nThe CROND service is running...No further remediation steps required\n"
                                        echo -e "\nStatus: Success\n"
                                else
                                        echo -e "Current Time: `date`\n"
                                        echo -e "\nThe CROND service is not running currently. Automation will perform the remediation steps to start the CROND service.\n"
                                        start_crond=$(sudo service crond start)
                                        if [[ "$start_crond" =~ "OK" ]]
                                        then
                                                echo -e "Current Time: `date`\n"
                                                echo -e "\nAutomation has successfully started the CROND service. \nThe CROND status is as follows: \n$start_crond \n"
                                                echo -e "\nAutomation will monitor the CROND service status for 5 minutes...\n"
                                                sleep 300;
                                                chk_crond=$(sudo service crond status)
                                                        echo -e "Current Time: `date`\n"
                                                        echo -e "\nThe status of the CROND service is as follows: \n$chk_crond\n"
                                                        if [[ "$chk_crond" =~ "running" ]]
                                                        then
                                                                echo -e "\nAfter monitoring for 5 minutes, the CROND status is running...\n"
                                                                echo -e "\nStatus: Success\n"
                                                        fi
                                                        if [[ "$chk_crond" =~ "stopped" ]]
                                                        then
                                                                echo -e "\nAfter monitoring for 5 minutes, the CROND status is not running...\n"
                                                                echo -e "\nStatus: Failed\n"
                                                        fi
                                        else
                                        echo -e "\nAutomation failed to start the crond service.\n"
                                        fi
                                fi
                        fi
                #SSHD Service Remediation Steps
                        if [[ "$servicename" == "sshd" ]]
                        then
                                #check SSHD Service
                                chk_sshd=$(sudo service sshd status)
                                echo -e "\nThe status of the SSHD service is as follows: \n$chk_sshd\n"
                                if [[ "$chk_sshd" =~ "running" ]]
                                then
                                        echo -e "Current Time: `date`\n"
                                        echo -e "\nThe SSHD service is running...No further remediation steps required\n"
                                        echo -e "\nStatus: Success\n"
                                else
                                        echo -e "Current Time: `date`\n"
                                        echo -e "\nThe SSHD service is not running currently. Automation will perform the remediation steps to start the SSHD service.\n"
                                        start_sshd=$(sudo service sshd start)
                                        if [[ "$start_sshd" =~ "OK" ]]
                                        then
                                                echo -e "Current Time: `date`\n"
                                                echo -e "\nAutomation has successfully started the SSHD service. \nThe SSHD status is as follows: \n$start_sshd \n"
                                                echo -e "\nAutomation will monitor the SSHD service status for 5 minutes...\n"
                                                sleep 300;
                                                chk_sshd=$(sudo service sshd status)
                                                        echo -e "Current Time: `date`\n"
                                                        echo -e "\nThe status of the SSHD service is as follows: \n$chk_sshd\n"
                                                        if [[ "$chk_sshd" =~ "running" ]]
                                                        then
                                                                echo -e "\nAfter monitoring for 5 minutes, the SSHD status is running...\n"
                                                                echo -e "\nStatus: Success\n"
                                                        fi
                                                        if [[ "$chk_sshd" =~ "stopped" ]]
                                                        then
                                                                echo -e "\nAfter monitoring for 5 minutes, the SSHD status is not running...\n"
                                                                echo -e "\nStatus: Failed\n"
                                                        fi
                                        else
                                        echo -e "\nAutomation failed to start the sshd service.\n"
                                        fi
                                fi
                        fi
                #XINETD Service Remediation Steps
                        if [[ "$servicename" == "xinetd" ]]
                        then
                                #check XINETD Service
                                chk_xinetd=$(sudo service xinetd status)
                                echo -e "\nThe status of the XINETD service is as follows: \n$chk_xinetd\n"
                                if [[ "$chk_xinetd" =~ "running" ]]
                                then
                                        echo -e "Current Time: `date`\n"
                                        echo -e "\nThe XINETD service is running...No further remediation steps required\n"
                                        echo -e "\nStatus: Success\n"
                                else
                                        echo -e "Current Time: `date`\n"
                                        echo -e "\nThe XINETD service is not running currently. Automation will perform the remediation steps to start the XINETD service.\n"
                                        start_xinetd=$(sudo service xinetd start)
                                        if [[ "$start_xinetd" =~ "OK" ]]
                                        then
                                                echo -e "Current Time: `date`\n"
                                                echo -e "\nAutomation has successfully started the XINETD service. \nThe XINETD status is as follows: \n$start_xinetd \n"
                                                echo -e "\nAutomation will monitor the XINETD service status for 5 minutes...\n"
                                                sleep 300;
                                                chk_xinetd=$(sudo service xinetd status)
                                                        echo -e "Current Time: `date`\n"
                                                        echo -e "\nThe status of the XINETD service is as follows: \n$chk_xinetd\n"
                                                        if [[ "$chk_xinetd" =~ "running" ]]
                                                        then
                                                                echo -e "\nAfter monitoring for 5 minutes, the XINETD status is running...\n"
                                                                echo -e "\nStatus: Success\n"
                                                        fi
                                                        if [[ "$chk_xinetd" =~ "stopped" ]]
                                                        then
                                                                echo -e "\nAfter monitoring for 5 minutes, the XINETD status is not running...\n"
                                                                echo -e "\nStatus: Failed\n"
                                                        fi
                                        else
                                        echo -e "\nAutomation failed to start the xinetd service.\n"
                                        fi
                                fi
                        fi
                #SYSLOG Service Remediation Steps
                        if [[ "$servicename" == "syslogd" ]]
                        then
                                #check SYSLOG Service
                                chk_rsyslog=$(sudo service rsyslog status)
                                echo -e "\nThe status of the SYSLOG service is as follows: \n$chk_rsyslog\n"
                                if [[ "$chk_rsyslog" =~ "running" ]]
                                then
                                        echo -e "Current Time: `date`\n"
                                        echo -e "\nThe SYSLOG service is running...No further remediation steps required\n"
                                        echo -e "\nStatus: Success\n"
                                else
                                        echo -e "Current Time: `date`\n"
                                        echo -e "\nThe SYSLOG service is not running currently. Automation will perform the remediation steps to start the SYSLOG service.\n"
                                        start_rsyslog=$(sudo service rsyslog start)
                                        if [[ "$start_rsyslog" =~ "OK" ]]
                                        then
                                                echo -e "Current Time: `date`\n"
                                                echo -e "\nAutomation has successfully started the SYSLOG service. \nThe SYSLOG status is as follows: \n$start_rsyslog\n"
                                                echo -e "\nAutomation will monitor the SYSLOG service status for 5 minutes...\n"
                                                sleep 300;
                                                chk_rsyslog=$(sudo service rsyslog status)
                                                        echo -e "Current Time: `date`\n"
                                                        echo -e "\nThe status of the SYSLOG service is as follows: \n$chk_rsyslog\n"
                                                        if [[ "$chk_rsyslog" =~ "running" ]]
                                                        then

                                                                echo -e "\nAfter monitoring for 5 minutes, the SYSLOG status is running...\n"
                                                                echo -e "\nStatus: Success\n"
                                                        fi
                                                        if [[ "$chk_rsyslog" =~ "stopped" ]]
                                                        then
                                                                echo -e "\nAfter monitoring for 5 minutes, the SYSLOG status is not running...\n"
                                                                echo -e "\nStatus: Failed\n"
                                                        fi
                                        else
                                        echo -e "\nAutomation failed to start the rsyslog service.\n"
                                        fi
                                fi
                        fi
                fi
        #####################RHEL 7####################################################
                if [[ "$chk_version" =~ "7" ]]
                then
                        echo -e "\nThe Redhat Linux version of this machine falls under Redhat family version 7. \n"
                        ver=7
                #NTPD Service Remediation Steps
                        if [[ "$servicename" == "ntpd" ]]
                        then
                        #check NTPD Service
                        chk_ntpd=$(sudo systemctl status ntpd.service)
                        echo -e "\nThe status of the NTPD service is as follows: \n$chk_ntpd\n"
                                if [[ "$chk_ntpd" =~ "running" ]]
                                then
                                        echo -e "Current Time: `date`\n"
                                        echo -e "\nThe NTPD service is running...No further remediation steps required\n"
                                        echo -e "\nStatus: Success\n"
                                else
                                        echo -e "Current Time: `date`\n"
                                        echo -e "\nThe NTPD service is not running currently. Automation will perform the remediation steps to start the NTPD service.\n"
                                        sudo systemctl enable ntpd.service
                                        sudo systemctl start ntpd.service
                                        start_ntpd=$(sudo systemctl status ntpd.service)
                                        if [[ "$start_ntpd" =~ "running" ]]
                                        then
                                                echo -e "Current Time: `date`\n"
                                                echo -e "\nAutomation has successfully started the NTPD service. \nThe NTPD status is as follows: \n$start_ntpd \n"
                                                echo -e "\nAutomation will monitor the NTPD service status for 5 minutes...\n"
                                                sleep 300;
                                                chk_ntpd=$(sudo systemctl status ntpd.service)
                                                echo -e "Current Time: `date`\n"
                                                echo -e "\nThe status of the NTPD service is as follows: \n$chk_ntpd\n"
                                                        if [[ "$chk_ntpd" =~ "running" ]]
                                                        then
                                                                echo -e "\nAfter monitoring for 5 minutes, the NTPD status is running...\n"
                                                                echo -e "\nStatus: Success\n"
                                                        fi
                                                        if [[ "$chk_ntpd" =~ "dead" ]]
                                                        then
                                                                echo -e "\nAfter monitoring for 5 minutes, the NTPD status is not running...\n"
                                                                echo -e "\nStatus: Failed\n"
                                                        fi
                                        else
                                        echo -e "\nAutomation failed to start the NTPD service.\n"
                                        fi
                                fi
                        fi
                #CROND Service Remediation Steps
                        if [[ "$servicename" == "crond" ]]
                        then
                        #check CROND Service
                        chk_crond=$(sudo systemctl status crond.service)
                        echo -e "\nThe status of the CROND service is as follows: \n$chk_crond\n"
                                if [[ "$chk_crond" =~ "running" ]]
                                then
                                        echo -e "Current Time: `date`\n"
                                        echo -e "\nThe CROND service is running...No further remediation steps required\n"
                                        echo -e "\nStatus: Success\n"
                                else
                                        echo -e "Current Time: `date`\n"
                                        echo -e "\nThe CROND service is not running currently. Automation will perform the remediation steps to start the CROND service.\n"
                                        sudo systemctl enable crond.service
                                        sudo systemctl start crond.service
                                        start_crond=$(sudo systemctl status crond.service)
                                        if [[ "$start_crond" =~ "running" ]]
                                        then
                                                echo -e "Current Time: `date`\n"
                                                echo -e "\nAutomation has successfully started the CROND service. \nThe CROND status is as follows: \n$start_crond\n"
                                                echo -e "\nAutomation will monitor the CROND service status for 5 minutes...\n"
                                                sleep 300;
                                                chk_crond=$(sudo systemctl status crond.service)
                                                echo -e "Current Time: `date`\n"
                                                echo -e "\nThe status of the CROND service is as follows: \n$chk_crond\n"
                                                        if [[ "$chk_crond" =~ "running" ]]
                                                        then
                                                                echo -e "\nAfter monitoring for 5 minutes, the CROND status is running...\n"
                                                                echo -e "\nStatus: Success\n"
                                                        fi
                                                        if [[ "$chk_crond" =~ "dead" ]]
                                                        then
                                                                echo -e "\nAfter monitoring for 5 minutes, the CROND status is not running...\n"
                                                                echo -e "\nStatus: Failed\n"
                                                        fi
                                        else
                                        echo -e "\nAutomation failed to start the crond service.\n"
                                        fi
                                fi
                        fi
                #SSHD Service Remediation Steps
                        if [[ "$servicename" == "sshd" ]]
                        then
                        #check SSHD Service
                        chk_sshd=$(sudo systemctl status sshd.service)
                        echo -e "\nThe status of the SSHD service is as follows: \n$chk_sshd\n"
                                if [[ "$chk_sshd" =~ "running" ]]
                                then
                                        echo -e "Current Time: `date`\n"
                                        echo -e "\nThe SSHD service is running...No further remediation steps required\n"
                                        echo -e "\nStatus: Success\n"
                                else
                                        echo -e "Current Time: `date`\n"
                                        echo -e "\nThe SSHD service is not running currently. Automation will perform the remediation steps to start the SSHD service.\n"
                                        sudo systemctl enable sshd.service
                                        sudo systemctl start sshd.service
                                        start_sshd=$(sudo systemctl status sshd.service)
                                        if [[ "$start_sshd" =~ "running" ]]
                                        then
                                                echo -e "Current Time: `date`\n"
                                                echo -e "\nAutomation has successfully started the SSHD service. \nThe SSHD status is as follows: \n$start_sshd\n"
                                                echo -e "\nAutomation will monitor the SSHD service status for 5 minutes...\n"
                                                sleep 300;
                                                chk_sshd=$(sudo systemctl status sshd.service)
                                                echo -e "Current Time: `date`\n"
                                                echo -e "\nThe status of the SSHD service is as follows: \n$chk_sshd\n"
                                                        if [[ "$chk_sshd" =~ "running" ]]
                                                        then
                                                                echo -e "\nAfter monitoring for 5 minutes, the SSHD status is running...\n"
                                                                echo -e "\nStatus: Success\n"
                                                        fi
                                                        if [[ "$chk_sshd" =~ "dead" ]]
                                                        then
                                                                echo -e "\nAfter monitoring for 5 minutes, the SSHD status is not running...\n"
                                                                echo -e "\nStatus: Failed\n"
                                                        fi
                                        else
                                        echo -e "\nAutomation failed to start the sshd service.\n"
                                        fi
                                fi
                        fi
                #XINETD Service Remediation Steps
                        if [[ "$servicename" == "xinetd" ]]
                        then
                        #check XINETD Service
                        chk_xinetd=$(sudo systemctl status xinetd.service)
                        echo -e "\nThe status of the XINETD service is as follows: \n$chk_xinetd\n"
                                if [[ "$chk_xinetd" =~ "running" ]]
                                then
                                        echo -e "Current Time: `date`\n"
                                        echo -e "\nThe XINETD service is running...No further remediation steps required\n"
                                        echo -e "\nStatus: Success\n"
                                else
                                        echo -e "Current Time: `date`\n"
                                        echo -e "\nThe XINETD service is not running currently. Automation will perform the remediation steps to start the XINETD service.\n"
                                        sudo systemctl enable xinetd.service
                                        sudo systemctl start xinetd.service
                                        start_xinetd=$(sudo systemctl status xinetd.service)
                                        if [[ "$start_xinetd" =~ "running" ]]
                                        then
                                                echo -e "Current Time: `date`\n"
                                                echo -e "\nAutomation has successfully started the XINETD service. \nThe XINETD status is as follows: \n$start_xinetd \n"
                                                echo -e "\nAutomation will monitor the XINETD service status for 5 minutes...\n"
                                                sleep 300;
                                                chk_xinetd=$(sudo systemctl status xinetd.service)
                                                echo -e "Current Time: `date`\n"
                                                echo -e "\nThe status of the XINETD service is as follows: \n$chk_xinetd\n"
                                                        if [[ "$chk_xinetd" =~ "running" ]]
                                                        then
                                                                echo -e "\nAfter monitoring for 5 minutes, the XINETD status is running...\n"
                                                                echo -e "\nStatus: Success\n"
                                                        fi
                                                        if [[ "$chk_xinetd" =~ "dead" ]]
                                                        then
                                                                echo -e "\nAfter monitoring for 5 minutes, the XINETD status is not running...\n"
                                                                echo -e "\nStatus: Failed\n"
                                                        fi
                                        else
                                        echo -e "\nAutomation failed to start the xinetd service.\n"
                                        fi
                                fi
                        fi
                #SYSLOG Service Remediation Steps
                        if [[ "$servicename" == "syslogd" ]]
                        then
                        #check SYSLOG Service
                        chk_rsyslog=$(sudo systemctl status rsyslog.service)
                        echo -e "\nThe status of the SYSLOG service is as follows: \n$chk_rsyslog\n"
                                if [[ "$chk_rsyslog" =~ "running" ]]
                                then
                                        echo -e "Current Time: `date`\n"
                                        echo -e "\nThe SYSLOG service is running...No further remediation steps required\n"
                                        echo -e "\nStatus: Success\n"
                                else
                                        echo -e "Current Time: `date`\n"
                                        echo -e "\nThe SYSLOG service is not running currently. Automation will perform the remediation steps to start the SYSLOG service.\n"
                                        sudo systemctl enable rsyslog.service
                                        sudo systemctl start rsyslog.service
                                        start_rsyslog=$(sudo systemctl status rsyslog.service)
                                        if [[ "$start_rsyslog" =~ "running" ]]
                                        then
                                                echo -e "Current Time: `date`\n"
                                                echo -e "\nAutomation has successfully started the SYSLOG service. \nThe SYSLOG status is as follows: \n$start_rsyslog \n"
                                                echo -e "\nAutomation will monitor the SYSLOG service status for 5 minutes...\n"
                                                sleep 300;
                                                chk_rsyslog=$(sudo systemctl status rsyslog.service)
                                                echo -e "Current Time: `date`\n"
                                                echo -e "\nThe status of the SYSLOG service is as follows: \n$chk_rsyslog\n"
                                                        if [[ "$chk_rsyslog" =~ "running" ]]
                                                        then
                                                                echo -e "\nAfter monitoring for 5 minutes, the SYSLOG status is running...\n"
                                                                echo -e "\nStatus: Success\n"
                                                        fi
                                                        if [[ "$chk_rsyslog" =~ "dead" ]]
                                                        then
                                                                echo -e "\nAfter monitoring for 5 minutes, the SYSLOG status is not running...\n"
                                                                echo -e "\nStatus: Failed\n"
                                                        fi
                                        else
                                        echo -e "\nAutomation failed to start the rsyslog service.\n"
                                        fi
                                fi
                fi
fi

        if [[ "$servicename" != "ntpd" && "$servicename" != "crond" && "$servicename" != "sshd" && "$servicename" != "xinetd" && "$servicename" != "syslogd" ]]
        then
        echo -e "\nService name $servicename does not correspond to the unix processes for remediation through Automation\n"
        fi
fi

if [[ "$OS_Type" != "Linux" && "$OS_Type" != "AIX" && "$OS_Type" != "SunOS" ]]
then
        echo "Command not found for OS $OS_Type"
fi


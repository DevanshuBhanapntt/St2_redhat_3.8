#!/bin/bash
status="$PT_status"
threshold="$PT_threshold"
username="$PT_unix_username"
password="$PT_unix_password"
solaris_username="$PT_solaris_username"
solaris_password="$PT_solaris_password"
aix_username="$PT_aix_username"
aix_password="$PT_aix_password"
hostname="$PT_hostname"
os_name="$PT_os_name"


if [[ "$os_name" == *"Linux Server"* ]]; then
        OS_Type="Linux"
elif [[ "$os_name" == *"AIX Server"* ]]; then
        OS_Type="AIX"
        if [[ "$aix_username" == "" ]]; then
     aix_username="$username"
     aix_password="$password"
    fi
elif [[ "$os_name" == *"Solaris Server"* ]]; then
        OS_Type="SunOS"
        if [[ "$solaris_username" == "" ]]; then
     solaris_username="$username"
     solaris_password="$password"
    fi
else
        OS_Type="Linux"
fi


read_line()
{
    into_loop="false"
    bulk_output="$1"
    bulk_output=$(echo "$bulk_output" | head -n-1)
    search_string="stdout:"
    for line in "$bulk_output"
    do
        if [[ "$line" == *"$search_string"* ]]; then
              into_loop="true"
              temp=${line#*$search_string}
              echo "$temp" | sed 's/"//g'
        elif [[ "$into_loop" == "true" && "$line" != *"succeeded:"* ]]; then
                into_loop="true"
                echo "$line" | sed 's/"//g'
        fi
    done
}

#OS_Type_out=$(st2 run core.remote cmd="uname" hosts="$hostname" username="$username" password="$password")
#OS_Type=$(read_line "$OS_Type_out")
#OS_Type=$(echo "$OS_Type" | sed 's/"//g' | sed 's/ //g')
#OS_Type=${OS_Type//$'\n'/}

##################################################################
#################### Linux/Unix Section ##########################
##################################################################


if [[ "$OS_Type" == "Linux" && "$status" != "-5" ]]; then

        for i in {1..2}; do
                memory_output=$(st2 run core.remote cmd="free -m | awk 'NR==2{printf \"%.2f%%\t\t\", \$3*100/\$2 }'" hosts="$hostname" username="$username" password="$password")                
                if [[ "$memory_output" == *"succeeded: true"* ]]; then
				    if [[  "$memory_output" == *"stderr: ''"* ]]; then
                        memory=$(read_line "$memory_output")
                        memory=${memory%.*}
						memory=${memory## }
			            memory=${memory%% } 
                        echo -e "Attempt $i : Current Time: `date`\n"
                        echo -e "Current Utilization:$memory \n";
                        sleep 300
					else
					    echo -e "Command to check memory utilization in remote host failed.\n"
						echo "$memory_output" | grep "stderr:"
                        exit 1
					fi
                else
                        echo -e "Connection to remote host failed."
                        exit 1
                fi

        done
		        echo -e "Total memory percentage utilized is:$memory \n";
                process_output=$(st2 run core.remote cmd="ps axo %mem,pid,euser,cmd | sort -nr | head -n 5" hosts="$hostname" username="$username" password="$password")
                process=$(read_line "$process_output")

                if [[ "$process" =~ "MEM" || "$process" =~ "PID" || "$process" =~ "EUSER" || "$process" =~ "CMD" ]]; then
                        owner=$(echo "$process" | awk 'NR==2'|awk '{print "Owner: " $3 " for Process ID: " $2 " using the command: " $4 " is consuming Highest Memory percentage: " $1}')
                else
                        owner=$(echo "$process" | awk 'NR==1'|awk '{print "Owner: " $3 " for Process ID: " $2 " using the command: " $4 " is consuming Highest Memory percentage: " $1}')
                fi

                echo "$owner"
                echo -e "Top five processes:\n$process"

fi


if [[ "$OS_Type" == "Linux" && "$status" == "-5" ]]; then
        memory_output=$(st2 run core.remote cmd="free -m | awk 'NR==2{printf \"%.2f%%\t\t\", \$3*100/\$2 }'" hosts="$hostname" username="$username" password="$password")

        if [[ "$memory_output" == *"succeeded: true"* ]]; then
                memory=$(read_line "$memory_output")
                memory=${memory%.*}
				memory=${memory## }
			    memory=${memory%% }
                echo -e "Current Time: `date`\n"
                echo -e "Total memory percentage utilized is:$memory \n"

                process_output=$(st2 run core.remote cmd="ps axo %mem,pid,euser,cmd | sort -nr | head -n 5" hosts="$hostname" username="$username" password="$password")
                process=$(read_line "$process_output")

                if [[ "$process" =~ "MEM" || "$process" =~ "PID" || "$process" =~ "EUSER" || "$process" =~ "CMD" ]]; then

                        owner=$(echo "$process" | awk 'NR==2'|awk '{print "Owner: " $3 " for Process ID: " $2 " using the command: " $4  " is consuming Highest Memory percentage: " $1}')
                else
                        owner=$(echo "$process" | awk 'NR==1'|awk '{print "Owner: " $3 " for Process ID: " $2 " using the command: " $4  " is consuming Highest Memory percentage: " $1}')
                fi
        echo "$owner"
                echo -e "Top five processes:\n$process"
    else
                echo "Connection to remote host failed."
                exit 1
        fi
fi




##################################################################
#################### Solaris Section #############################
##################################################################



if [[ "$OS_Type" == "SunOS" && "$status" != "-5" ]]; then
        for i in {1..2}; do

                free_mem_output=$(st2 run core.remote cmd="top|grep Memory| awk '{print \$5}'| cut -d 'G' -f 1" hosts="$hostname" username="$solaris_username" password="$solaris_password")
                total_mem_output=$(st2 run core.remote cmd="top|grep Memory| awk '{print \$2}'| cut -d 'G' -f 1" hosts="$hostname" username="$solaris_username" password="$solaris_password")
                if [[ "$free_mem_output" == *"succeeded: true"*  && "$total_mem_output" == *"succeeded: true"* ]]; then
                    if [[  "$free_mem_output" == *"stderr: ''"* && "$total_mem_output" == *"stderr: ''"* ]]; then
                        free_mem=$(read_line "$free_mem_output")
                        total_mem=$(read_line "$total_mem_output")
                   # echo "$free_mem"
                #       echo "$total_mem"
                        free_mem=${free_mem%.*}
						free_mem=${free_mem## }
			            free_mem=${free_mem%% }
                        total_mem=${total_mem%.*}
						total_mem=${total_mem## }
			            total_mem=${total_mem%% }
            #echo "$free_mem"
        #               echo "$total_mem"
                        percent_free=$(echo "scale=2;($free_mem/$total_mem)*100"|bc);
                        percent_used=$(echo "scale=2;(100-$percent_free)"|bc);
        #           echo "$percent_free"
        #               echo "$percent_used"
                        percent_used=${percent_used%.*}
						percent_used=${percent_used## }
			            percent_used=${percent_used%% }
         #   echo "$percent_used"
                        echo -e "Attempt $i : Current Time: `date`\n";						
                        echo -e "Current Utilization:$percent_used \n";
                        sleep 300
				    else
					    echo -e "Command to check memory utilization in remote host failed.\n" 
						echo "$free_mem_output" | grep "stderr"
						exit 1
					fi
                else
                        echo "Connection to remote host failed."
                        exit 1
                fi

        done
		        echo -e "Total memory percentage utilized is:$percent_used \n";
                process_output=$(st2 run core.remote cmd="ps -efo pmem,uid,pid,ppid,pcpu,comm| sort -r| head -5" hosts="$hostname" username="$solaris_username" password="$solaris_password")
                process=$(read_line "$process_output")

                owner=$(echo "$process" | awk 'NR==2' | awk '{print "Owner UID : " $2 " for Process ID: " $3 "  using the command: " $6 " consuming highest Memory%: " $1}')
                echo "$owner";
                echo -e "Top five processes:\n$process"

fi



if [[ "$OS_Type" == "SunOS" && "$status" == "-5" ]]; then


        free_mem_output=$(st2 run core.remote cmd="top|grep Memory| awk '{print \$4}'|cut -d 'G' -f 1" hosts="$hostname" username="$solaris_username" password="$solaris_password")

        total_mem_output=$(st2 run core.remote cmd="top|grep Memory| awk '{print \$2}'| cut -d 'G' -f 1" hosts="$hostname" username="$solaris_username" password="$solaris_password")

        if [[ "$free_mem_output" == *"succeeded: true"*  && "$total_mem_output" == *"succeeded: true"* ]]; then

                free_mem=$(read_line "$free_mem_output")
                total_mem=$(read_line "$total_mem_output")

                free_mem=${free_mem%.*}
				free_mem=${free_mem## }
			    free_mem=${free_mem%% }
                total_mem=${total_mem%.*}
				total_mem=${total_mem## }
			    total_mem=${total_mem%% }

                percent_free=$(echo "scale=2;($free_mem/$total_mem)*100"|bc);
                percent_used=$(echo "scale=2;(100-$percent_free)"|bc);

                percent_used=${percent_used%.*}
				percent_used=${percent_used## }
			    percent_used=${percent_used%% }

                echo -e "Current Time: `date`\n";
                echo -e "Total memory percentage utilized is:$percent_used \n";

                process_output=$(st2 run core.remote cmd="ps -efo pmem,uid,pid,ppid,pcpu,comm| sort -r| head -5" hosts="$hostname" username="$solaris_username" password="$solaris_password")
                process=$(read_line "$process_output")

                owner=$(echo "$process" | awk 'NR==2' | awk '{print "Owner UID : " $2 " for Process ID: " $3 "  using the command: " $6 " consuming highest Memory%: " $1}')
                echo "$owner";
                echo -e "Top five processes:\n$process"

        else
                echo "Connection to remote host failed."
                exit 1
        fi

fi



##################################################################
#################### AIX Section #################################
##################################################################


if [[ "$OS_Type" == "AIX" && "$status" != "-5" ]]; then

        for i in {1..2}; do

                memory_output=$(st2 run core.remote cmd="svmon -G| awk 'NR==2{printf \"%.2f%%\t\t\", \$6*100/\$2 }'" hosts="$hostname" username="$aix_username" password="$aix_password")

                if [[ "$memory_output" == *"succeeded: true"* ]]; then
                    if [[  "$memory_output" == *"stderr: ''"* ]]; then
                        memory=$(read_line "$memory_output")
                        memory=${memory%.*}
						memory=${memory## }
			            memory=${memory%% }
                        echo -e "Attempt $i : Current Time: `date`\n";						
                        echo -e "Current Utilization:$memory \n";
                        sleep 300
					else
					    echo -e "Command to check memory utilization in remote host failed.\n"
						echo "$memory_output" | grep "stderr:"
                        exit 1
					fi	
                else
                        echo "Connection to remote host failed."
                        exit 1
                fi

        done
		        echo -e "Total memory percentage utilized is:$memory \n";
                process_output=$(st2 run core.remote cmd="ps aux | head -1; ps aux | sort -rn +3 | head -5" hosts="$hostname" username="$aix_username" password="$aix_password")
                process=$(read_line "$process_output")

                owner=$(echo "$process" | awk 'NR==2' | awk '{print "Owner : " $1 " for Process ID: " $2 "  using the command: " $12 " consuming highest Memory%: " $4}')
        echo "$owner";
                echo -e "Top five processes:\n$process"

fi


if [[ "$OS_Type" == "AIX" && "$status" == "-5" ]]; then
        memory_output=$(st2 run core.remote cmd="svmon -G| awk 'NR==2{printf \"%.2f%%\t\t\", \$6*100/\$2 }'" hosts="$hostname" username="$aix_username" password="$aix_password")

        if [[ "$memory_output" == *"succeeded: true"* ]]; then

                memory=$(read_line "$memory_output")
                memory=${memory%.*}
				memory=${memory## }
			    memory=${memory%% }
                echo -e "Current Time: `date`\n";
                echo -e "Total memory percentage utilized is:$memory \n";

                process_output=$(st2 run core.remote cmd="ps aux | head -1; ps aux | sort -rn +3 | head -5" hosts="$hostname" username="$aix_username" password="$aix_password")
                process=$(read_line "$process_output")

                owner=$(echo "$process" | awk 'NR==2' | awk '{print "Owner : " $1 " for Process ID: " $2 "  using the command: " $12 " consuming highest Memory%: " $4}')
        echo "$owner";
                echo -e "Top five processes:\n$process"
        else
                echo "Connection to remote host failed."
                exit 1
        fi
fi


##########################################################################
#################### Os Type Not Implemented   ###########################
#########################################################################

if [[ "$OS_Type" != "Linux" && "$OS_Type" != "AIX" && "$OS_Type" != "SunOS" ]]; then
        echo "Command not found for OS $OS_Type"
fi

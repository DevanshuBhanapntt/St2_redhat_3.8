status="$PT_status"
threshold="$PT_threshold"
username="$PT_host_username"
password="$PT_host_password"
hostname="$PT_hostname"
solaris_username="$PT_solaris_username"
solaris_password="$PT_solaris_password"
os_name="$PT_os_name"

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

if [[ "$os_name" == *"Linux Server"* ]]; then
  OS_Type="Linux"
elif [[ "$os_name" == *"AIX Server"* ]]; then
  OS_Type="AIX"
elif [[ "$os_name" == *"Solaris Server"* ]]; then
  OS_Type="SunOS"
  if [[ "$solaris_username" != "" ]]; then
     username="$solaris_username"
     password="$solaris_password"
  fi
else
  OS_Type="Linux"
fi

#OS_Type_out=$(st2 run core.remote cmd="uname" hosts="$hostname" username="$username" password="$password")
#OS_Type=$(read_line "$OS_Type_out")
#OS_Type=$(echo "$OS_Type" | sed 's/"//g' | sed 's/ //g')
#OS_Type=${OS_Type//$'\n'/}


######  OS = Linux && Status = Open #########
if [[ "$OS_Type" == "Linux" && ("$status" != "-5") ]]; then
  for i in {1..2}; do 
    command_out=$(st2 run core.remote cmd="top -b -n 2 | grep -i 'cpu(s)' | awk 'FNR==2 {print}' | sed 's/[a-z]//g' | sed 's/,//g' | sed 's/%//g' | awk '{print \$2\" \"\$3\" \"\$4}' | awk '{print \$1+\$2+\$3}'" hosts="$hostname" username="$username" password="$password")       
	if [[ "$command_out" == *"succeeded: true"* ]]; then
	  if [[  "$command_out" == *"stderr: ''"* ]]; then
       cpu=$(read_line "$command_out")
	   cpu=${cpu//$'\n'/}
	   echo -e "Execution $i:"
	   echo -e "Current Time: `date`\n"
       echo -e "Current CPU Utilization:$cpu \n"
       sleep 300
	  else
	   echo -e "Command to check cpu utilization in remote host failed.\n"
	   echo "$command_out" | grep "stderr:"
	   exit 1
	  fi
	else
       echo "Connection to remote host failed."
	   exit 1
    fi
  done
     echo -e "sum of cpu is:$cpu \n"
	 cpu=${cpu%.*}
     threshold=${threshold%.*}
     process_output=$(st2 run core.remote cmd="top -b -n1 | awk 'NR>=8 && NR<=12'" hosts="$hostname" username="$username" password="$password")
	 process=$(read_line "$process_output")
     owner=$(echo "$process" | awk 'NR==1' | awk '{print "Owner : " $2 " and Process: " $12 " consuming highest CPU%: " $9}')
     echo "$owner"
	 echo -e "Top five processes:\n$process"   
fi
######  OS = Linux && Status = Pending #########
if [[ "$OS_Type" == "Linux" && ("$status" == "-5") ]]; then
   command_out=$(st2 run core.remote cmd="top -b -n 2 | grep -i 'cpu(s)' | awk 'FNR==2 {print}' | sed 's/[a-z]//g' | sed 's/,//g' | sed 's/%//g' | awk '{print \$2\" \"\$3\" \"\$4}' | awk '{print \$1+\$2+\$3}'" hosts="$hostname" username="$username" password="$password")
   cpu=$(read_line "$command_out")
   cpu=${cpu//$'\n'/}
   echo -e "Current Time: `date`\n"
   echo -e "sum of cpu is:$cpu \n"
   cpu=${cpu%.*}
   threshold=${threshold%.*}
   process_output=$(st2 run core.remote cmd="top -b -n1 | awk 'NR>=8 && NR<=12'" hosts="$hostname" username="$username" password="$password")
   process=$(read_line "$process_output")
   owner=$(echo "$process" | awk 'NR==1' | awk '{print "Owner : " $2 " and Process: " $12 " consuming highest CPU%: " $9}')
   echo "$owner"; echo -e "Top five processes:\n$process"
fi


######  OS = AIX && Status = Open #########
if [[ "$OS_Type" == "AIX" && ("$status" != "-5") ]]; then
  for i in {1..2}; do 
    command_out=$(st2 run core.remote cmd="iostat -t 2 3 | awk 'FNR==7 {print}' | sed 's/[a-z]//g' | sed 's/,//g' |sed 's/%//g' | awk '{print \$3\" \"\$4}' | awk '{print \$1+\$2}'" hosts="$hostname" username="$username" password="$password")
	if [[ "$command_out" == *"succeeded: true"* ]]; then
	  if [[  "$command_out" == *"stderr: ''"* ]]; then
       cpu=$(read_line "$command_out")
	   cpu=${cpu//$'\n'/}
	   echo -e "Execution $i:"
	   echo -e "Current Time: `date`\n"
	   echo -e "Current CPU Utilization:$cpu \n"      
       sleep 300
	  else
	   echo -e "Command to check cpu utilization in remote host failed.\n"
	   echo "$command_out" | grep "stderr:"
	   exit 1
	  fi
	else
      echo "Connection to remote host failed."
	  exit 1
    fi
  done
    echo -e "sum of cpu is:$cpu \n"
    cpu=${cpu%.*}
    threshold=${threshold%.*}
    process_output=$(st2 run core.remote cmd="ps aux | head -1; ps aux | sort -rn +3 | head -5" hosts="$hostname" username="$username" password="$password")
	process=$(read_line "$process_output")
    owner=$(echo "$process" | awk 'NR==2' | awk '{print "Owner : " $1 " and Process: " $12 " consuming highest CPU%: " $3}')
    echo "$owner"
	echo -e "Top five processes:\n$process"  
fi
######  OS = AIX && Status = Pending #########
if [[ "$OS_Type" == "AIX" && ("$status" == "-5") ]]; then
   command_out=$(st2 run core.remote cmd="iostat -t 2 3 | awk 'FNR==7 {print}' | sed 's/[a-z]//g' | sed 's/,//g' |sed 's/%//g' | awk '{print \$3\" \"\$4}'  | awk '{print \$1+\$2}'" hosts="$hostname" username="$username" password="$password")
   cpu=$(read_line "$command_out")
   cpu=${cpu//$'\n'/}
   echo -e "Current Time: `date`\n"
   echo -e "sum of cpu is:$cpu \n"
   cpu=${cpu%.*}
   threshold=${threshold%.*}
   process_output=$(st2 run core.remote cmd="ps aux | head -1; ps aux | sort -rn +3 | head -5" hosts="$hostname" username="$username" password="$password")
   process=$(read_line "$process_output")
   owner=$(echo "$process" | awk 'NR==2' | awk '{print "Owner : " $1 " and Process: " $12 " consuming highest CPU%: " $3}')
   echo "$owner"; echo -e "Top five processes:\n$process"
fi


######  OS = SunOS && Status = Open #########
if [[ "$OS_Type" == "SunOS" && ("$status" != "-5") ]]; then
   for i in {1..2}; do 
     command_out=$(st2 run core.remote cmd="iostat -c 2 2 | awk 'NR==4 {print}' | sed 's/[a-z]//g' | sed 's/,//g' |sed 's/%//g' | awk '{print \$1\" \"\$2}'  | awk '{print \$1+\$2}'" hosts="$hostname" username="$username" password="$password")
	 if [[ "$command_out" == *"succeeded: true"* ]]; then
	  if [[  "$command_out" == *"stderr: ''"* ]]; then
        cpu=$(read_line "$command_out")
		cpu=${cpu//$'\n'/}    	
		echo -e "Execution $i:"
		echo -e "Current Time: `date`\n"
		echo -e "Current CPU Utilization:$cpu \n"
        sleep 300
	  else
	   echo -e "Command to check cpu utilization in remote host failed.\n"
	   echo "$command_out" | grep "stderr:"
	   exit 1
	  fi
     else
       echo "Connection to remote host failed."
	   exit 1
     fi
   done
     echo -e "sum of cpu is:$cpu \n"
     cpu=${cpu%.*}
     threshold=${threshold%.*}
     process_output=$(st2 run core.remote cmd="prstat -s cpu -n 5 1 1" hosts="$hostname" username="$username" password="$password")
	 process=$(read_line "$process_output")
     owner=$(echo "$process" | awk 'NR==2' | awk '{print "Owner : " $2 " and Process: " $10 " consuming highest CPU%: " $9}')
     echo "$owner"; echo -e "Top five processes:\n$process"  
fi
######  OS = SunOS && Status = Pending #########
if [[ "$OS_Type" == "SunOS" && ("$status" == "-5") ]]; then
   command_out=$(st2 run core.remote cmd="iostat -c 2 2 | awk 'NR==4 {print}' | sed 's/[a-z]//g' | sed 's/,//g' | sed 's/%//g' | awk '{print \$1\" \"\$2}'  | awk '{print \$1+\$2}'" hosts="$hostname" username="$username" password="$password")
   cpu=$(read_line "$command_out")
   cpu=${cpu//$'\n'/}
   echo -e "Current Time: `date`\n"
   echo -e "sum of cpu is:$cpu \n"
   cpu=${cpu%.*}
   threshold=${threshold%.*}
   process_output=$(st2 run core.remote cmd="prstat -s cpu -n 5 1 1" hosts="$hostname" username="$username" password="$password")   
   process=$(read_line "$process_output")
   owner=$(echo "$process" | awk 'NR==2' | awk '{print "Owner : " $2 " and Process: " $10 " consuming highest CPU%: " $9}')
   echo "$owner"; echo -e "Top five processes:\n$process"
fi
####################
if [[ "$OS_Type" != "Linux" && "$OS_Type" != "AIX" && "$OS_Type" != "SunOS" ]]
then
        echo "Command not found for OS $OS_Type"
fi

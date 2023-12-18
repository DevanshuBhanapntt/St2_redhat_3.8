#(Router/Switch)
device=$1
clogin_script_path=$2
logfile=$3
device_username=$4
device_password=$5
cpu_threshold=$6
current_loop_count=$7
max_loop=$8
consecutive_fails=$9
max_failures=$10

#device_username="$PT_device_username"
#device_password="$PT_device_password" -- will be fetched from entuity from the .rc file by clogin script

## remove banner
read_output ()
{
  input="$1"
  command_success=$(echo "$input" | grep -w 'show' | wc -l)
  if [[ "$command_success" -ge 1 ]]; then
    echo "$input" | awk '/show/{p=1}p'
  else
    echo "$input"
  fi
}

echo "$clock_output" | awk '/show/{p=1}p'

# Get model type from show version command
version_output=$("$clogin_script_path" -enable -u "$device_username" -p "$device_password" -c "show version" $device)
IsCisco=`echo "$version_output" | grep -w 'cisco\|Cisco' | wc -l`
IsJunos=`echo "$version_output" | grep -w 'JUNOS' | wc -l`
if [[ $IsCisco -ge 1 ]]; then
   ISNexus=`echo "$version_output" | grep -c 'Nexus\|1000V' | wc -l`
   IsMDS=`echo "$version_output" | grep -w 'MDS' | wc -l`
   if [[ $ISNexus -ge 1 ]]; then
      model_type="Nexus"
      cpu_proc_command="show system resources | include CPU"
   elif [[ $IsMDS -ge 1 ]]; then
      model_type="MDS"
      cpu_proc_command="show system resources | include CPU"
   else
      model_type="Default"
      cpu_proc_command="show proc cpu sorted 5sec"
   fi
elif [[ $IsJunos -ge 1 ]]; then
      model_type="JUNOS"
      cpu_proc_command="show chassis routing-engine | no-more"
else
   escalate="true"
   echo -e "Automation not able to find the network device type from show version command (or) the show version command failed.\r\n"
   echo -e "---------------------------------------------\r\n"
   echo -e "command output - show version \r\n"
   echo -e "---------------------------------------------\r\n"
   read_output "$version_output"
   echo -e ""
   echo -e "Escalating the task. Manual Intervention Required."
fi

if [[ $escalate != 'true' ]]; then
  #get the time 
  clock_output=$("$clogin_script_path" -enable -u "$device_username" -p "$device_password" -c "show clock" $device)
  IsFail=`echo "$clock_output" | grep -w 'Unknown command\|Invalid input detected' | wc -l`
  if [[ $IsFail -ge 1 ]]; then
      clock_output=$("$clogin_script_path" -enable -u "$device_username" -p "$device_password" -c "show time" $device)
  fi
   
  echo -e "-------------------------------------------------\r\n"
  echo -e "command output - show time - in device $device \r\n"
  echo -e "-------------------------------------------------\r\n"
  read_output "$clock_output"
  cpu_out=$("$clogin_script_path" -enable -u "$device_username" -p "$device_password" -c "$cpu_proc_command" $device)
  IsFail=`echo "$cpu_out" | grep -w 'Unknown command\|Invalid syntax\|Invalid input detected\|Invalid\|Error' | wc -l`
  if [[ $IsFail -ge 1 ]]; then
     model_type="Default"
     cpu_out=$("$clogin_script_path" -enable -u "$device_username" -p "$device_password" -c "show processes cpu" $device)
  fi
  echo -e "-----------------------------------------------------\r\n"
  echo -e "command output - $cpu_proc_command/show processes cpu - in device $device\r\n"
  echo -e "-----------------------------------------------------\r\n"
  IsFail=`echo "$cpu_out" | grep -w 'Unknown command\|Invalid syntax\|Invalid input detected\|Invalid\|Error' | wc -l`
  if [[ $IsFail -ge 1 ]]; then
	     echo -e "Error while executing cpu utilization command \r\n"
	     read_output "$cpu_out"
		 echo -e "Escalating the task. Manual Intervention Required."
  else
	     if [[ $model_type == 'Default' ]]; then
			 CPU_Util=`echo "$cpu_out" | grep 'CPU utilization for five seconds:' | awk -F 'seconds:' '{print $2}' | cut -d'%' -f 1`
			 CPU_Util=${CPU_Util## }
			 CPU_Util=${CPU_Util%% }
	     elif [[ $model_type == 'JUNOS' ]]; then
		     #RBDU01ER02
			 CPU_Util_Free=`echo "$cpu_out" | grep 'Idle' | awk -F 'Idle' '{print $2}' | cut -d ' ' -f 2`
			 CPU_Util_Free=${CPU_Util_Free## }
			 CPU_Util_Free=${CPU_Util_Free%% }  
			 CPU_Util=`expr 100 - $CPU_Util_Free`
	     else
             #RBCD04MA01  
			 CPU_Util=`echo "$cpu_out" | grep 'CPU states' | awk -F 'kernel,' '{print $2}' | cut -d'%' -f 1`
			 CPU_Util=${CPU_Util## }
			 CPU_Util=${CPU_Util%% }    
		 fi
		 
		 if [[ $CPU_Util != "" ]]; then
		   if [[ $CPU_Util -lt $cpu_threshold ]]; then
			  if [[ "$current_loop_count" == "$max_loop" && "$max_failures" != "$consecutive_fails" ]]; then
		          echo -e "The current CPU Utilization $CPU_Util is less than threshold($cpu_threshold)."
				  echo ""
				  read_output "$cpu_out"
				  echo ""
			      echo -e "Completing the task."
		      elif [[ "$max_failures" == "$consecutive_fails" ]]; then
		          echo -e "The current CPU Utilization $CPU_Util is less than threshold($cpu_threshold)."
				  echo ""
				  read_output "$cpu_out"
				  echo ""
			      echo -e "Escalating the ticket."
			  else
			      echo -e "The current CPU Utilization $CPU_Util is less than threshold($cpu_threshold)."
				  echo ""
				  read_output "$cpu_out"
				  echo ""
			      echo -e "Suspending the ticket for 10 minutes."
		      fi
	       else
			  if [[ "$current_loop_count" == "$max_loop" || "$max_failures" == "$consecutive_fails" ]]; then
			      echo -e "The current CPU Utilization $CPU_Util is above threshold($cpu_threshold)."
				  echo ""
				  read_output "$cpu_out"
				  echo ""
			      echo -e "Escalating the ticket. Manual Intervention Required."
			  else
		          echo -e "The current CPU Utilization $CPU_Util is above threshold($cpu_threshold)."
				  echo ""
				  read_output "$cpu_out"
				  echo ""
			      echo -e "Suspending the ticket for 10 minutes."
			  fi
		   fi
		 else
		   echo -e "Automation not able to find the current CPU utilization from the output."
		   echo ""
		   read_output "$cpu_out"
		   echo ""
		   echo -e "Escalating the ticket. Manual Intervention Required."
		 fi
   fi
fi

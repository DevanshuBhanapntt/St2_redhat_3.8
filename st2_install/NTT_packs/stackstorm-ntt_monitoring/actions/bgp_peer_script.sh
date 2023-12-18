#!/bin/bash
device=$1
peerip=$2
logfile=$3
deviceUser=$4
devicePass=$5
clogin_path=$6
dt=$(date +'%b %d')
sleep 120
echo -e "Executing - sh ip bgp vpnv4 all summary | include $peerip - against $device to list peer in VRF "
echo -e "----------------------------------------------------------------------------------------------- "
VRF_Output=$($clogin_path -noenable -u "$deviceUser" -p "$devicePass" -c "sh ip bgp vpnv4 all summary | include $peerip" $device | sed '0,/terminal length 0/d' | sed -r '/^\s*$/d' | sed 's/"//g')
echo "$VRF_Output"
check_vrf_true=$(echo "$VRF_Output" | grep -w $peerip | grep -iv include | wc -l)
check_vrf_not_running=$(echo "$VRF_Output" | grep -w $peerip | egrep -ic "Active|Idle|connect")
read_line()
{
	bulk_output=$1
	search_string=$2
	while read line; do
		if [[ "${line}" == *"$search_string"* ]]; then	   
			echo "${line}"
		fi
	done < <(echo "$bulk_output")
}
if [ $check_vrf_true == 0 ]; then
	echo -e "$peerip not found in - sh ip bgp vpnv4 all summary - listing "
	echo -e "\n"
	echo -e "Executing - show ip bgp 0.0.0.0/0, show ip bgp summary, show ip route $peerip - against $device "
	echo -e "----------------------------------------------------------------------------------------------- "
	BGP_Output=$($clogin_path -noenable -u "$deviceUser" -p "$devicePass" -c "show ip bgp 0.0.0.0/0;show ip bgp summary;show ip route $peerip" $device | sed '0,/terminal length 0/d' | sed -r '/^\s*$/d' | sed 's/"//g')
	echo "$BGP_Output"
	echo -e "\n\n"
	check1=$(echo "$BGP_Output" | grep -c "directly connected, via")
	check2=$(echo "$BGP_Output" |grep -c "Last update from")
	check_NX=$(echo "$BGP_Output" | grep -c "*via $peerip,")
	check_time=$(read_line "$BGP_Output" "$peerip")
	check_time=$(echo "$check_time" | egrep -ic "Active|Idle|connect")
	if [ $check_time == 0 ]; then
		if [ $check1 != 0 ] || [ $check2 != 0 ] || [ $check_NX != 0 ]; then
			if [ $check1 != 0 ]; then
				get_interface=$(read_line "$BGP_Output" "directly connected, via")
				get_interface=$(echo "$get_interface" | awk '{print $5}')
				Output=$(echo "$get_interface" | awk -F "." '{print $1}')
			elif [ $check2 != 0 ]; then
				get_interface=$(read_line "$BGP_Output" "Last update from")
				get_interface=$(echo "$get_interface" | awk '{print $6}'| sed 's/,$//')
				Output=$(echo "$get_interface" | awk -F "." '{print $1}')
			else
				get_interface=$(read_line "$BGP_Output" "*via $peerip,")
				get_interface=$(echo "$get_interface" | awk '{print $3}'| sed 's/,$//')
				Output=$(echo "$get_interface" | awk -F "." '{print $1}')
			fi
			echo -e "Executing - show log - against $device "
			echo -e "-------------------------------------- "
			$clogin_path -noenable -u "$deviceUser" -p "$devicePass" -c "show log | include $dt" $device | egrep -i "$peerip|$Output"
			echo -e "-------------------------------------- "
			check3=$(echo "$Output" | grep -c "MIB-2_interface_not_found")
			if [ $check3 != 0 ]; then
				echo -e "\n"
				echo -e "MIB-2 interface not found "
				echo -e "\n"
			else
				echo -e "\n"
				echo "MIB Interface is = $Output"
				echo -e "\n"
				echo -e "---------- Current Date/Time ---------- "
				date
				echo -e "\n"
				echo -e "Executing - clear counters $Output, show interface $Output - against $device "
				echo -e "----------------------------------------------------------------------- "
				for i in {1..4}; do
					echo -e "Execution $i:"
					interface_result=$($clogin_path -noenable -u "$deviceUser" -p "$devicePass" -c "clear counters $Output;show interface $Output" $device | sed '0,/terminal length 0/d' | sed -r '/^\s*$/d' | sed 's/"//g')
					echo "$interface_result"
					interface_output+=$interface_result
					echo -e "\n"
					sleep 40
				done
				measure1=$(echo "$interface_output" | egrep -ic "input errors|CRC")
				if [ $measure1 -gt 0 ]; then
					task2=$(echo "$interface_output" | grep -c "0 input errors, 0 CRC")
					if [ $task2 -eq 4 ]; then
						echo -e "INPUT_AND_CRC_COUNTER_CHECK_SUCCESS "
						bgp_er_lin=$(echo "$interface_output" | grep "input errors," | tail -1)
						echo -e "$bgp_er_lin "
						echo -e "\n"
					else
						echo -e "PLEASE_CHECK_INPUT_AND_CRC_COUNTER "
						bgp_er_lin=$(echo "$interface_output" | grep "input errors," | tail -1)
						echo -e "Error found in last check : $bgp_er_lin "
						echo -e "\n"
					fi
				fi
				measure2=$(echo "$interface_output" | egrep -ic "output errors")
				if [ $measure2 -gt 0 ]; then
					task3=$(echo "$interface_output" | grep -c "0 output errors")
					if [ $task3 -eq 4 ]; then
						echo -e "OUTPUT_COUNTER_CHECK_SUCCESS "
						bgp_er_lin=$(echo "$interface_output" |grep "output errors," | tail -1)
						echo -e "$bgp_er_lin "
						echo -e "\n"
					else
						echo -e "PLEASE_CHECK_OUTPUT_COUNTER "
						bgp_er_lin=$(echo "$interface_output" | grep "output errors," | tail -1)
						echo -e "Error found in last check : $bgp_er_lin "
						echo -e "\n"
					fi
				fi
				measure3=$(echo "$interface_output" | egrep -ic "interface resets")
				if [ $measure3 -gt 0 ]; then
					task6=$(echo "$interface_output" | grep -c "0 interface resets")
					if [ $task6 -eq 4 ]; then
						echo -e "INTERFACE_RESET_COUNTER_CHECK_SUCCESS "
						bgp_er_lin=$(echo "$interface_output" | grep "interface resets" | tail -1)
						echo -e "$bgp_er_lin "
						echo -e "\n"
					else
						echo -e "PLEASE_CHECK_INTERFACE_RESET_COUNTER "
						bgp_er_lin=$(echo "$interface_output" | grep "interface resets"| tail -1)
						echo -e "Error found in last check : $bgp_er_lin "
						echo -e "\n"
					fi
				fi
				measure4=$(echo "$interface_output" | egrep -ic "output buffer failures|output buffers swapped out")
				if [ $measure4 -gt 0 ]; then
					task4=$(echo "$interface_output" | grep -c "0 output buffer failures, 0 output buffers swapped out")
					if [ $task4 -eq 4 ]; then
						echo -e "OUTPUT_BUFFER_AND_SWAPPED_COUNTER_CHECK_SUCCESS "
						bgp_er_lin=$(echo "$interface_output" | grep "output buffer failures," | tail -1)
						echo -e "$bgp_er_lin "
						echo -e "\n"
					else
						echo -e "PLEASE_CHECK_OUTPUT_BUFFER_AND_SWAPPED_COUNTER "
						bgp_er_lin=$(echo "$interface_output" | grep "output buffer failures," | tail -1)
						echo -e "Error found in last check : $bgp_er_lin "
						echo -e "\n"
					fi
				fi
				measure5=$(echo "$interface_output" | egrep -ic "carrier transitions")
				if [ $measure5 -gt 0 ]; then
					task5=$(echo "$interface_output" | grep -c "0 carrier transitions")
					if [ $task5 -eq 4 ]; then
						echo -e "CAREER_TRANSITION_COUNTER_CHECK_SUCCESS "
						bgp_er_lin=$(echo "$interface_output" | grep "carrier transitions" | tail -1)
						echo -e "$bgp_er_lin "
						echo -e "\n"
					else
						echo -e "PLEASE_CHECK_CAREER_TRANSITION_COUNTER "
						bgp_er_lin=$(echo "$interface_output" | grep "carrier transitions" | tail -1)
						echo -e "Error found in last check : $bgp_er_lin "
						echo -e "\n"
					fi
				fi
				measure_intup=$(echo "$interface_output" | egrep -ic "$Output is")
				if [ $measure_intup -gt 0 ]; then
					task_intup=$(echo "$interface_output" | grep -c "$Output is up")
					if [ $task_intup -eq 4 ]; then
						echo -e "INTERFACE_UP_CHECK_SUCCESS "
						echo -e "\n"
					else
						echo -e "INTERFACE_STATUS_DOWN_IN_ONE_OF_FOUR_CHECKS "
						echo -e "MIB-2_interface_not_found Functional"
						echo -e "\n"
					fi
				fi
				measure_lineprotocol=$(echo "$interface_output" | egrep -ic "line protocol")
				if [ $measure_lineprotocol -gt 0 ]; then
					task_lineprotocol=$(echo "$interface_output" | grep -c "line protocol is up")
					if [ $task_lineprotocol -eq 4 ]; then
						echo -e "LINE_PROTOCOL_UP_CHECK_SUCCESS "
						echo -e "\n"
					else
						echo -e "LINE_PROTOCOL_DOWN_IN_ONE_OF_FOUR_CHECKS "
						echo -e "MIB-2_interface_not_found Functional"
						echo -e "\n"
					fi
				fi
			fi
		else
			echo -e "------------------------------------------------------- "
			echo -e "Error : Unable to locate $peerip in command output. Either command failed or unable to connect to device. "
			echo -e "\n"
			echo -e "------------------------------------------------------- "
			echo "$BGP_Output"
		fi
	else
		echo -e "ip_bgp_summary_not_ok "
		echo -e "\n"
		echo -e "$peerip UP-Down timer is not in expected state(Found Active|Idle|connect)"
		echo -e "------------------------------------------------------------- "
		read_line "$BGP_Output" "$peerip"
	fi
else
	if [ $check_vrf_not_running == 0 ]; then
		echo -e "\n"
		echo -e "Executing - show log $peerip - against $device "
		echo -e "----------------------------------------- "
		$clogin_path -noenable -u "$deviceUser" -p "$devicePass" -c "show log | include $dt" $device | egrep -i "$peerip"
		echo -e "-------------------------------------------------- "
		echo -e "\n"
		echo -e "Executing - sh ip bgp vpnv4 all summary | include $peerip - in loop against $device "
		echo -e "-------------------------------------------------- "
		for i in 1 2 3 4 5 6
		do
			sleep 20
			echo -e "---------- Date/Time ---------- "
			date
			echo -e "\n"
			echo -e "Loop Execution $i - sh ip bgp vpnv4 all summary | include $peerip - against $device "
			echo -e "-------------------------------------------------- "
			VRF_Check=$($clogin_path -noenable -u "$deviceUser" -p "$devicePass" -c "sh ip bgp vpnv4 all summary | include $peerip" $device | sed '0,/terminal length 0/d' | sed -r '/^\s*$/d')
			echo "$VRF_Check"
			echo -e "\n"
		done
		check_vrf_not_running_loop=$(read_line "$VRF_Check" "$peerip")
		check_vrf_not_running_loop=$(echo "$check_vrf_not_running_loop" | grep -iv include | egrep -ic "Active|Idle|connect")
		check_vrf_not_running_loop_count=$(read_line "$VRF_Check" "$peerip")
		check_vrf_not_running_loop_count=$(echo "$check_vrf_not_running_loop_count" | grep -iv include | wc -l)
		check_vrf_not_running_loop_count_div=$(( $check_vrf_not_running_loop_count % 6 ))
		if [ $check_vrf_not_running_loop == 0 ] && [ $check_vrf_not_running_loop_count_div == 0 ] && [ $check_vrf_not_running_loop_count -ge 6 ]; then
			echo -e "ip_bgp_summary_vrf verification success "
			echo -e "$peerip is in desired state "
		else
			echo -e "ip_bgp_summary_not_ok "
			echo -e "$peerip UP-Down timer is not in expected state(Found Active|Idle|connect) "
			echo -e "------------------------------------------------------------- "
		fi
	else
		echo -e "\n"
		echo -e "Executing - show log $peerip - against $device "
		echo -e "----------------------------------------- "
		$clogin_path -noenable -u "$deviceUser" -p "$devicePass" -c "show log | include $dt" $device | egrep -i "$peerip"
		echo -e "-------------------------------------------------- "
		echo -e "\n"
		echo -e "ip_bgp_summary_not_ok "
		echo -e "$peerip UP-Down timer is not in expected state "
		echo -e "------------------------------------------------------------- "
		read_line "$VRF_Check" "$peerip"
	fi
fi

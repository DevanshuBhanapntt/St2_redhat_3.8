#!/bin/bash
#Place this file in entuity server /home/bao_net_mon path
deviceIP=$1
device_username=$2
device_password=$3
version=$4
oid=$5
nw_clogin_path=$6
interface_ip=$7
community=$8
securityName=$9
authProtocol=${10}
authKey=${11}
privKey=${12}
privprotocol=${13}
acl_name='55'
acl_num='55'
SNMPWalk_status='false'
host_ip=`hostname -i` 

 

device_walk_pc=''
##################SNMPWALK Check#####################
if [ "$version" = 'v2' ]; then
   echo -e "**** Automation executed SNMP Walk against the device ($deviceIP) ****"
   echo -e "SNMP Walk output is:"
   device_walk_pc=`snmpwalk --clientaddr=$interface_ip:161 -v 2c -c "$community" "$deviceIP" "$oid" 2>&1`
   device_walk_pc_result=`echo "$?"`
   if [[ $device_walk_pc_result = '0' && $device_walk_pc != *"Invalid privacy protocol"* && $device_walk_pc != *"Timeout"* && $device_walk_pc != *"No Response from"* ]]
   then
	   SNMPWalk_status='true'
	   echo -e "SNMPStatus:true"
       echo -e "SNMPWalk_Result:\n$device_walk_pc"
	   echo -e ""
	   echo -e "Automation verified that the Device ($deviceIP) is responding to SNMP Walk from the IP ($host_ip)"
   else
	   SNMPWalk_status='false'
	   echo -e "SNMPWalk_Result:\n$device_walk_pc"
   fi
elif [ "$version" = 'v3' ]; then
  echo -e "**** Automation executed SNMP Walk against the device ($deviceIP) ****"
  echo -e "SNMP Walk output is:"
  for i in $(echo $privprotocol | sed "s/,/ /g")
  do		 
		privprotocol_temp=$i
		#echo -e "privprotocol_temp:$privprotocol_temp"
		device_walk_pc=`snmpwalk --clientaddr=$interface_ip:161 -v3 -u "$securityName" -a "$authProtocol" -A "$authKey" -l authPriv -x "$privprotocol_temp" -X "$privKey" "$deviceIP" "$oid"  2>&1`
		device_walk_pc_result=`echo "$?"`   
		if [[ $device_walk_pc_result = '0' && $device_walk_pc != *"Invalid privacy protocol"* && $device_walk_pc != *"Timeout"* && $device_walk_pc != *"No Response from"* ]]
		then
		    privprotocol_connected=$privprotocol_temp
			break
		fi
  done  
  if [ $device_walk_pc_result = '0' ]; then
	   SNMPWalk_status='true'
       echo -e "SNMPStatus:true"
       echo -e "SNMPWalk_Result:$device_walk_pc"
       echo -e "privprotocol_connected:$privprotocol_connected"
	   echo -e ""
	   echo -e "Automation verified that the Device ($deviceIP) is responding to SNMP Walk from the IP ($host_ip)"
  else
	   SNMPWalk_status='false'
	   echo -e "SNMPWalk_Result:$device_walk_pc"
  fi
fi
##################SNMPWALK Check#####################

#################SNMP FAIL##################
if [ "$SNMPWalk_status" != 'true' ]; then
  echo -e ""
  echo -e "Automation verified that the Device ($deviceIP) is not responding to SNMP Walk from the IP ($host_ip)"
  echo -e ""
  echo -e "**** Automation executed ping against Device ($deviceIP) from the Poller IP ($host_ip). ****"
  ping -c 4 $deviceIP
  echo -e ""
  echo -e "**** SNMP Version ****"
  snmp_version_out=`$nw_clogin_path/clogin -noenable -b $interface_ip -u "$device_username" -p "$device_password" -c "show version" $deviceIP 2>&1`
  echo -e "$snmp_version_out"
  echo -e ""
  snmp_version_out_lower=`echo "$snmp_version_out" | tr '[:upper:]' '[:lower:]'`
  if [[ "$snmp_version_out_lower" == *"nexus"* || "$snmp_version_out_lower" == *"cisco"* || "$snmp_version_out_lower" == *"1000v"* ]]; then
    echo -e "**** Automation executed command to verify SNMP Agent status on device ($deviceIP) ****"
	show_run_out=`$nw_clogin_path/clogin -noenable -b $interface_ip -u "$device_username" -p "$device_password" -c "show snmp" $deviceIP 2>&1`
	echo -e "$show_run_out"
	if [[ "$show_run_out" == *"SNMP agent enabled"* ]]; then
	  if [[ "$show_run_out" == *"$host_ip"* ]]; then
	     echo -e "Automation found that the status of the SNMP Agent is in desired state on Device($deviceIP)."
	     echo ""
	     show_acl_out=`$nw_clogin_path/clogin -noenable -b $interface_ip -u "$device_username" -p "$device_password" -c "sh ip access-list 55" $deviceIP 2>&1`
		 if [[ "$show_run_out" == *"$host_ip"* ]]; then
		   echo -e "SNMPStatus:true"
		   echo -e "Automation verified that SNMP is correctly configured on the Device($deviceIP)."
		 else
		   echo -e "SNMPStatus:false"
		   echo -e "Automation unable to find the entry of stackstorm server ip($host_ip) in device($deviceIP) ACL"
		 fi
	  else
	    echo -e "SNMPStatus:false"
	    echo -e "Automation found that the status of the SNMP Agent is in desired state on Device($deviceIP), but automation unable to find the entry of stackstorm server ip($host_ip) in device snmp output."
	  fi	  
	else
	  echo -e "SNMPStatus:false"
	  echo -e "Automation found that the status of the SNMP Agent is not in desired state on Device($deviceIP) or unable to check the snmp agent status of the device."
	fi
  else
    echo -e "SNMPStatus:false"
    echo -e "Automation unable to find the Device manufacturer and model. Either the Device ($deviceIP) is not reachable or its a non-Cisco or ASA device"
  fi
else
 exit 0
fi
#################SNMP FAIL##################

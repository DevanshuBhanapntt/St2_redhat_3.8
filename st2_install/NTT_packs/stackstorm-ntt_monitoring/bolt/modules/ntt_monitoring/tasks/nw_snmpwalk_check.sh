#!/bin/bash
deviceIP=$PT_deviceIP
version=$PT_version
community=$PT_community
nms_ip=$PT_nms_ip
oid=$PT_oid
securityName=$PT_securityname
authProtocol=$PT_authprotocol
authKey=$PT_authkey
privKey=$PT_privkeya
privprotocol=$PT_privprotocol


device_walk_pc =''
if [ "$version" = 'v2' ] ;then
   VAR_LENGTH=${#nms_ip}
   if [ $VAR_LENGTH -gt 1 ]; then
      device_walk_pc=`/usr/bin/snmpwalk --clientaddr="$nms_ip":161 -v 2c -c "$community" "$deviceIP" "$oid"  2>&1` 
   else	
      device_walk_pc=`/usr/bin/snmpwalk -v 2c -c "$community" "$deviceIP" "$oid"  2>&1`
   fi
elif [ "$version" = 'v3' ] ; then
	VAR_LENGTH=${#nms_ip}
	for i in $(echo $privprotocol | sed "s/,/ /g")
	do		 
		privprotocol_temp=$i
		#echo -e "privprotocol_temp:$privprotocol_temp"
		if [ $VAR_LENGTH -gt 1 ]; then
			device_walk_pc=`/usr/bin/snmpwalk --clientaddr="$nms_ip":161 -v3 -u "$securityName" -a "$authProtocol" -A "$authKey" -l authPriv -x "$privprotocol_temp" -X "$privKey" "$deviceIP" "$oid"  2>&1`
		else
			device_walk_pc=`/usr/bin/snmpwalk -v3 -u "$securityName" -a "$authProtocol" -A "$authKey" -l authPriv -x "$privprotocol_temp" -X "$privKey" "$deviceIP" "$oid"  2>&1`
		fi		
		device_walk_pc_result=`echo "$?"`
		#echo -e $device_walk_pc_result	    
		if [[ $device_walk_pc_result = '0' && $device_walk_pc != *"Invalid privacy protocol"* && $device_walk_pc != *"Timeout"* && $device_walk_pc != *"No Response from"* ]]
		then
		    privprotocol_connected=$privprotocol_temp
			break
		fi
	done	
fi

if [ $device_walk_pc_result = '0' ]; then
   echo -e "SNMPWalk:true"
   echo -e "SNMPWalk_Result:$device_walk_pc"
   echo -e "privprotocol_connected:$privprotocol_connected"
else
   echo -e "SNMPWalk:false"
   echo -e "SNMPWalk_Result:$device_walk_pc"
   echo -e "privprotocol_connected:$privprotocol_connected"
fi

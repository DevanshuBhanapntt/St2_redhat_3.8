#!/bin/bash
entuity_username=$1
entuity_password=$2
entuity_ip=$3
entuity_interface_ip=$4
device_ip=$5
device_user=$6
device_pass=$7
cmd="show version | include cisco"



output=`sudo st2 run core.remote cmd="/home/bao_net_mon/nw_clogin.sh -noenable -b $entuity_interface_ip -u $device_user -p $device_pass -c '$cmd' $device_ip"  hosts="$entuity_ip" username="$entuity_username" password="$entuity_password"`
if echo "$output" | grep "Couldn't login:"; 
then	
   echo "Unable to login to remote device"  	
else
   echo "Login to remote device succesfully"
   if echo "$output" | grep "cisco";
   then
       echo "Cisco device"
   else
       echo "not a cisco device"
   fi    
fi



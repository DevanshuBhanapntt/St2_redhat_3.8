#!/bin/bash
deviceip=$PT_device_ip
deviceusername=$PT_device_username
devicepassword=$PT_device_password
devicecommand=$PT_commands
clogin_script_path=$PT_clogin_script_path
nms_ip=$PT_nms_ip

# run the shell script file
device_login_check=''
VAR_LENGTH=${#nms_ip}
if [ $VAR_LENGTH -gt 1 ]; then
   device_login_check=`$clogin_script_path -noenable -b "$nms_ip" -u "$deviceusername" -p "$devicepassword" -c "$devicecommand" "$deviceip" 2>&1`
else
   device_login_check=`$clogin_script_path -noenable -u "$deviceusername" -p "$devicepassword" -c "$devicecommand" "$deviceip" 2>&1`  
fi
device_login_check_result=`echo "$?"`
if [ $device_login_check_result = '0' ]; then
   echo -e "DeviceLogin:true"
   echo -e "DeviceCommand_Result:$device_login_check"
else
  echo -e "DeviceLogin:false"
  echo -e "DeviceCommand_Result:$device_login_check"
fi

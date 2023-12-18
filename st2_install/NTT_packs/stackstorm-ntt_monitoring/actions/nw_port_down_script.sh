#!/bin/bash
device=$1
Ifindex=$2
mib=$3
logfile=$4
snmpstring=$5
WorkflowType=$6
snmpver=$7
securityName=$8
authProtocol=$9
authKey=${10}
privProtocolList=${11}
privKey=${12}


if [[ "$mib" != "" ]];then
  if [[ "$mib" == *"Se"* ]];then
     int=`echo "$mib" | sed -E 's/.*?Se//'`
	 mib="Serial"${int}
  elif [[ "$mib" == *"Gi"* ]];then
     int=`echo "$mib" | sed -E 's/.*?Gi//'`
	 mib="GigabitEthernet"${int}
  elif [[ "$mib" == *"Tu"* ]];then
     int=`echo "$mib" | sed -E 's/.*?Tu//'`
	 mib="Tunnel"${int}
  elif [[ "$mib" == *"AT"* ]];then
     int=`echo "$mib" | sed -E 's/.*?AT//'`
	 mib="ATM"${int}
  elif [[ "$mib" == *"Vi"* ]];then
     int=`echo "$mib" | sed -E 's/.*?Vi//'`
	 mib="Virtual-Access"${int}
  elif [[ "$mib" == *"Te"* ]];then
     int=`echo "$mib" | sed -E 's/.*?Te//'`
	 mib="TenGigabitEthernet"${int}
  elif [[ "$mib" == *"Fa"* ]];then
     int=`echo "$mib" | sed -E 's/.*?Fa//'`
	 mib="FastEthernet"${int}
  elif [[ "$mib" == *"Mu"* ]];then
     int=`echo "$mib" | sed -E 's/.*?Mu//'`
	 mib="Multilink"${int}
  else
     mib="$mib"
  fi
fi

if [[ "$snmpver" == "v2" ]]; then
  if [[ "$WorkflowType" == *"PortLink"* ]]; then
   cmd2="==================================================================================="
   cmd3="Integer/Status Mapping - INTEGER: 1 (UP), INTEGER: 2 (DOWN), INTEGER: 3 (TESTING)"
   cmd5="date"
   output=$(for i in 1 2 3 4 5 6;do (sleep 10;date;
     echo "Command: snmpwalk -v 2c -c $snmpstring $device 1.3.6.1.2.1.2.2.1.2.$Ifindex";
	 echo "Command Response:"
     out1=`snmpwalk -v 2c -c $snmpstring $device 1.3.6.1.2.1.2.2.1.2.$Ifindex 2>&1`;
     echo "$out1";
	 echo ""
	 echo "Command: snmpwalk -v 2c -c $snmpstring $device .1.3.6.1.2.1.2.2.1.8.$Ifindex";
	 echo "Command Response:"
     out2=`snmpwalk -v 2c -c $snmpstring $device .1.3.6.1.2.1.2.2.1.8.$Ifindex 2>&1`;
	 check_success=`echo "$out2" | grep "= INTEGER: 1\|= INTEGER: up" | wc -l`
	 if [[ "$check_success" -ge 1 ]]; then sleep 10; else sleep 230; fi
     echo "$out2";
     echo "$cmd3";
     echo "$cmd2";
     echo ""); done)
   echo "$output" 
   snmp_success_count=$(echo "$output" | grep -e "= INTEGER: 1\|= INTEGER: up" | wc -l)
   if [[ $snmp_success_count < 6 ]]; then
     echo "Automation found the port is down (or) unable to check port status for 6 iterations. Please Refer worknotes."
     echo "SNMP_SUCCESS_COUNT=$snmp_success_count"	 
   else
     echo "SNMP_SUCCESS_COUNT=$snmp_success_count"
   fi   
  fi
  
  if [[ "$WorkflowType" == *"PortOper"* ]]; then
   echo "Interface name: $mib"
   echo ""
   Ifindex=''
   for i in 1 2 3 4 5 6
   do
     date;
      echo "Command: snmpwalk -v 2c -c "$snmpstring" "$device" 1.3.6.1.2.1.2.2.1.2"
	  echo "Command Response:"
      out1=`snmpwalk -v 2c -c "$snmpstring" "$device" 1.3.6.1.2.1.2.2.1.2 | grep "$mib" 2>&1`
	  if [[ "$out1" == *"Timeout"* || "$out1" == *"No Response"* ]]; then
	        echo "$out1"
			sleep 230
	  elif [[ "$out1" == "" ]]; then
		    echo 'No Response from $device'
			sleep 230
	  else
		  mibout="$out1"
		  if [[ "$mibout" == *"IF-MIB::ifDescr"* ]]; then
			  echo "$mibout"
              int=`echo "$mibout" | sed -E 's/.*?ifDescr.//'`
              Ifindex=`echo "$int" | awk '{print $1}'`						 
			  break
		  elif [[ "$mibout" == "" ]]; then
			  echo "IfindexNo for $mib not found"
			  Ifindex=""
		      sleep 230
          else
              Ifindex=`echo "$mibout" | awk '{print $1}' | sed -e 's#.*2.2.1.2.\(\)#\1#'`;
			  echo "$mibout";
			  if [[ "$Ifindex" == "" ]]; then
			    sleep 230
			  else
			    break
			  fi			  
		  fi
	  fi
	done
   if [[ "$Ifindex" == "" ]]; then
      echo "Automation not able to find the IfindexNo for $mib. Please refer the worknotes."
	  echo "SNMP_SUCCESS_COUNT=0"
   else
	  echo ""
      echo "IfindexNo for $mib=$Ifindex"
	  echo ""
      cmd2="==================================================================================="
      cmd3="Integer/Status Mapping - INTEGER: 1 (UP), INTEGER: 2 (DOWN), INTEGER: 3 (TESTING)"
      cmd4="date"
	  output=$(for i in 1 2 3 4 5 6;do (sleep 10;date; 
	     echo "Command: snmpwalk -v 2c -c $snmpstring $device .1.3.6.1.2.1.2.2.1.8.$Ifindex";
		 echo "Command Response:"
         out2=`snmpwalk -v 2c -c $snmpstring $device .1.3.6.1.2.1.2.2.1.8.$Ifindex 2>&1`;
		 check_success=`echo "$out2" | grep "= INTEGER: 1\|= INTEGER: up" | wc -l`
		 if [[ "$check_success" -ge 1 ]]; then sleep 10; else sleep 230; fi
         echo "$out2";
         echo "$cmd3";
         echo "$cmd2";
         echo ""); done)
      echo "$output" 
	  snmp_success_count=$(echo "$output" | grep "= INTEGER: 1\|= INTEGER: up" | wc -l)
	  if [[ $snmp_success_count < 6 ]]; then
	    echo "Automation found the port is down (or) unable to check port status for 6 iterations. Please Refer worknotes."
	    echo "SNMP_SUCCESS_COUNT=$snmp_success_count"
      else
        echo "SNMP_SUCCESS_COUNT=$snmp_success_count"
      fi 
   fi   
  fi  
else
  privProtocol=''
  echo "Automation executing snmpwalk to find the private protocol of the device."
  echo "Command: snmpwalk -$snmpver -u $securityName -a $authProtocol -A authKey -l authPriv -x privProtocol -X privKey $device .1.3.6.1.2.1.1.1"
  for i in 1 2 3 4 5 6
   do
   date
    output=$(snmpwalk -"$snmpver" -u "$securityName" -a "$authProtocol" -A "$authKey" -l authPriv -x AES128 -X "$privKey" "$device" .1.3.6.1.2.1.1.1 2>&1)
    if [[ "$output" != *"snmpwalk: Decryption error"* && "$output" != *"Timeout"* && "$output" != *"timeout"* && "$output" != *"snmpget: Timeout"* ]]; then
	    privProtocol="AES128"
    fi
	echo "$output" | head -n 2
    output=$(snmpwalk -"$snmpver" -u "$securityName" -a "$authProtocol" -A "$authKey" -l authPriv -x AES256 -X "$privKey" "$device" .1.3.6.1.2.1.1.1 2>&1)
    if [[ "$output" != *"snmpwalk: Decryption error"* && "$output" != *"Timeout"* && "$output" != *"timeout"* && "$output" != *"snmpget: Timeout"* ]]; then
	    privProtocol="AES256"
    fi
	echo "$output" | head -n 2
    output=$(snmpwalk -"$snmpver" -u "$securityName" -a "$authProtocol" -A "$authKey" -l authPriv -x DES -X "$privKey" "$device" .1.3.6.1.2.1.1.1 2>&1)
    if [[ "$output" != *"snmpwalk: Decryption error"* && "$output" != *"Timeout"* && "$output" != *"timeout"* && "$output" != *"snmpget: Timeout"* ]]; then
	    privProtocol="DES"
    fi
	echo "$output" | head -n 2
	if [[ "$privProtocol" == "" ]]; then
	   sleep 230
	else
	   break
	fi
  done
  if [[ "$privProtocol" == "" ]];then
      echo "Automation not able to find the privProtocol for device $device"	  
	  echo "SNMP_SUCCESS_COUNT=0"
  else
     if [[ "$WorkflowType" == *"PortLink"* ]]; then
      cmd2="==================================================================================="
      cmd3="Integer/Status Mapping - INTEGER: 1 (UP), INTEGER: 2 (DOWN), INTEGER: 3 (TESTING)"
      cmd5="date"
	  output=$(for i in 1 2 3 4 5 6;do (sleep 10;date;
         echo "Command: snmpwalk -$snmpver -u $securityName -a $authProtocol -A authKey -l authPriv -x $privProtocol -X privKey $device 1.3.6.1.2.1.2.2.1.2.$Ifindex";
	     echo "Command Response:"
         out1=`snmpwalk -$snmpver -u $securityName -a $authProtocol -A $authKey -l authPriv -x $privProtocol -X $privKey $device 1.3.6.1.2.1.2.2.1.2.$Ifindex 2>&1`;
         echo "$out1";
	     echo "Command: snmpwalk -$snmpver -u $securityName -a $authProtocol -A authKey -l authPriv -x $privProtocol -X privKey $device .1.3.6.1.2.1.2.2.1.8.$Ifindex";
	     echo "Command Response:"
         out2=`snmpwalk -$snmpver -u $securityName -a $authProtocol -A $authKey -l authPriv -x $privProtocol -X $privKey $device .1.3.6.1.2.1.2.2.1.8.$Ifindex 2>&1`;
		 check_success=`echo "$out2" | grep "= INTEGER: 1\|= INTEGER: up" | wc -l`
		 if [[ "$check_success" -ge 1 ]]; then sleep 10; else sleep 230; fi
         echo "$out2";
         echo "$cmd3";
         echo "$cmd2";
         echo ""); done)
      echo "$output"
      snmp_success_count=$(echo "$output" | grep "= INTEGER: 1\|= INTEGER: up" | wc -l)
      if [[ $snmp_success_count < 6 ]]; then
	      echo "Automation found the port is down (or) unable to check port status for 6 iterations. Please Refer worknotes:"
	      echo "SNMP_SUCCESS_COUNT=$snmp_success_count"
      else
          echo "SNMP_SUCCESS_COUNT=$snmp_success_count"
      fi 
	fi
	  
   if [[ "$WorkflowType" == *"PortOper"* ]]; then
    echo "Interface name: $mib"
	echo ""
	Ifindex=''
   for i in 1 2 3 4 5 6
   do
      date
      echo "Command: snmpwalk -$snmpver -u $securityName -a authProtocol -A authKey -l authPriv -x $privProtocol -X privKey $device"
	  echo "Command Response:"
      out1=`snmpwalk -"$snmpver" -u "$securityName" -a "$authProtocol" -A "$authKey" -l authPriv -x "$privProtocol" -X "$privKey" "$device" 1.3.6.1.2.1.2.2.1.2 | grep "$mib" 2>&1`
	  if [[ "$out1" == *"Timeout"* || "$out1" == *"No Response"* ]]; then
	        echo "$out1"
			sleep 230
	  elif [[ "$out1" == "" ]]; then
		    echo 'No Response from $device'
			sleep 230
	  else
		  mibout="$out1";
		  if [[ "$mibout" == *"IF-MIB::ifDescr"* ]]; then
			  echo "$mibout"
              int=`echo "$mibout" | sed -E 's/.*?ifDescr.//'`
              Ifindex=`echo "$int" | awk '{print $1}'`						 
			  break
		  elif [[ "$mibout" == "" ]]; then
			  echo "IfindexNo for $mib not found"
			  Ifindex=""
		      sleep 230
          else
              Ifindex=`echo "$mibout" | awk '{print $1}' | sed -e 's#.*2.2.1.2.\(\)#\1#'`;
			  echo "$mibout";
			  if [[ "$Ifindex" == "" ]]; then
			     sleep 230
			  else
			     break
			  fi
		  fi
	  fi
	done
	if [[ "$Ifindex" == "" ]]; then
      echo "Automation not able to find the IfindexNo for $mib. Please refer worknotes."
	  echo "SNMP_SUCCESS_COUNT=0"
    else
	 echo ""
     echo "IfindexNo for $mib = $Ifindex"
	 echo ""
     cmd2="==================================================================================="
     cmd3="Integer/Status Mapping - INTEGER: 1 (UP), INTEGER: 2 (DOWN), INTEGER: 3 (TESTING)"
     cmd4="date"
     output=$(for i in 1 2 3 4 5 6;do (sleep 10;date; 
	     echo "Command: snmpwalk -$snmpver -u $securityName -a $authProtocol -A authKey -l authPriv -x $privProtocol -X privKey $device .1.3.6.1.2.1.2.2.1.8.$Ifindex";
		 echo "Command Response:"
         out2=`snmpwalk -$snmpver -u $securityName -a $authProtocol -A $authKey -l authPriv -x $privProtocol -X $privKey $device .1.3.6.1.2.1.2.2.1.8.$Ifindex 2>&1`;
		 check_success=`echo "$out2" | grep "= INTEGER: 1\|= INTEGER: up" | wc -l`
		 if [[ "$check_success" -ge 1 ]]; then sleep 10; else sleep 230; fi
         echo "$out2";
         echo "$cmd3";
         echo "$cmd2";
         echo ""); done)
      echo "$output" 
	  snmp_success_count=$(echo "$output" | grep "= INTEGER: 1\|= INTEGER: up" | wc -l)
	  if [[ $snmp_success_count < 6 ]]; then
	    echo "Automation found the port is down (or) unable to check port status for 6 iterations. Please Refer worknotes:"
	    echo "SNMP_SUCCESS_COUNT=$snmp_success_count"
      else
        echo "SNMP_SUCCESS_COUNT=$snmp_success_count"
      fi 
    fi  	  
   fi
  fi
fi

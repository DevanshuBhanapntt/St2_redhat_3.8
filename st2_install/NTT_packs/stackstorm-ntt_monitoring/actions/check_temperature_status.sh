#!/bin/bash
entuity_username=$1
entuity_password=$2
entuity_ip=$3
entuity_interface_ip=$4
device_ip=$5
device_user=$6
device_pass=$7
cmd="show version"


#output="cisco WS-C3750X-48P (PowerPC405) processor (revision A0) with 262144K bytes of memory."
output=`sudo st2 run core.remote cmd="/home/bao_net_mon/nw_clogin.sh -noenable -b $entuity_interface_ip -u $device_user -p $device_pass -c '$cmd' $device_ip"  hosts="$entuity_ip" username="$entuity_username" password="$entuity_password"`
#echo "$output"
#Get model number
if [[ $output == *"Nexus7000"* ]];
then
   #echo "Nexus7000"
   model_output=`echo "$output" | grep "Nexus7000" | tail -1 |cut -d' ' -f3 `
   #echo "$model_output" 
elif [[ $output == *"Nexus"* ]];
then
    #echo "Nexus"
    model_output=`echo "$output" | grep "Nexus" | tail -1`
    #echo "$model_output"
elif [[ $output == *"cisco"* ]];
then
    #echo "cisco"
    model_output=`echo "$output" | grep "cisco" | cut -d' ' -f2`
    #echo "$model_output"
elif [[ $output == *"Cisco"* ]];
then
    #echo "cisco"
    model_output=`echo "$output" | grep "Cisco" | cut -d' ' -f2`
    #echo "$model_output"    
elif [[ $output == *"ASR"* ]];
then
    #echo "ASR"
    model_output="ASR"
    #echo "$model_output"
elif [[ $output == *"AIR"* ]];
then
    #echo "AIR"
    model_output="AIR"
    #echo "$model_output"   
else
   echo "Model is not matching with the required condition."
fi

#Get temperature command along with model number
#if [[ $model_output == *"3750"* ]] || [[ $model_output == *"2960"* ]];
if [[ $model_output == *"3750"*  ]] || [[ $model_output == *"3850"*  ]] || [[ $model_output == *"2960"* ]] || [[ $model_output == *"4507"* ]] || [[ $model_output == *"3560"* ]] || [[ $model_output == *"3650"* ]] || [[ $model_output == *"3550"* ]] || [[ $model_output == *"4948"* ]] || [[ $model_output == *"5548"* ]] || [[ $model_output == *"7009"* ]] || [[ $model_output == *"7010"* ]] || [[ $model_output == *"7018"* ]] || [[ $model_output == *"5020"* ]] || [[ $model_output == *"4510"* ]] || [[ $model_output == *"5596"* ]] || [[ $model_output == *"5612"* ]] || [[ $model_output == *"5624"* ]] || [[ $model_output == *"7004"* ]] || [[ $model_output == *"9300"* ]];
then
    temperature_cmd="sh env temperature"
    #echo "$temperature_cmd"
elif [[ $model_output == *"6513"*  ]] || [[ $model_output == *"6504"* ]] || [[ $model_output == *"6506"* ]] || [[ $model_output == *"4506"* ]] || [[ $model_output == *"4500"* ]];
then
     temperature_cmd="show env alarm"
     #echo "$temperature_cmd"	
elif [[ $model_output == *"2951"*  ]] || [[ $model_output == *"2911"* ]] || [[ $model_output == *"2921"* ]] || [[ $model_output == *"2948"* ]];
then
    temperature_commnad="show env all"	
    #echo "$temperature_cmd"
elif [[ $model_output == *"5548"*  ]] || [[ $model_output == *"5020"* ]] || [[ $model_output == *"5596"* ]];
then
    temperature_commnad="show environment fex"
    #echo "$temperature_cmd"
elif [[ $model_output == *"6880"*  ]];
then
    temperature_commnad="show environment alarm status"
    #echo "$temperature_cmd"    
elif [[ $model_output == *"ASR"*  ]]
then
    temperature_commnad="show environment all"
    echo "$temperature_cmd"	
elif [[ $model_output == *"AIR"*  ]];
then
    temperature_commnad="show environment"
    #echo "$temperature_cmd"	
else
    echo "Not able to find Temperature command."

fi   

#sudo touch /opt/stackstorm/packs/ntt_monitoring/temperature_alarm.txt
#sudo chmod 777 /opt/stackstorm/packs/ntt_monitoring/temperature_alarm.txt

#Get Temperature Status
temperature_output=`sudo st2 run core.remote cmd="/home/bao_net_mon/nw_clogin.sh -noenable -b $entuity_interface_ip -u $device_user -p $device_pass -c '$temperature_cmd' $device_ip"  hosts="$entuity_ip" username="$entuity_username" password="$entuity_password"`
#echo "$temperature_output"
temperature_string=`echo "$temperature_output" |sed '/spawn/d' | sed '/password/d' | sed '/exit/d' | sed '/true/d' | sed '/action.ref/d'| sed '/RSA/d' | sed '/yes/d' | sed '/pass/d'| sed '/ONLY/d' | sed '/computer/d' | sed '/unauthor/d' | sed '/civil/d' | sed '/true/d' | sed '/Inlet/d' | sed '/Outlet/d' | sed '/Hotspot/d' | sed '/Temperature State:/d' | sed '/Celsius/d' | sed '/#/d' |  sed '/---/d' | sed '/Matthews/d' |  sed '/CCCC/d' | sed '/|/d' | sed '/*/d' | sed '/device/d' | sed '/security/d' | sed "/$device_ip/d" | sed '/^[[:space:]]*$/d' |  sed '/result/d' | sed '/false/d' |  sed '/return/d' |  sed '/stdout/d' |  sed '/context.user/d' | sed '/username/d' | sed '/hosts/d' | sed '/parameters/d' | sed '/end/d' | sed '/start/d' | sed '/status/d' | sed '/true/d' | sed "/$entuity_ip/d" | sed '/stderr/d' | sed '/Sensor/d' |sed "/$temperature_cmd/d" | sed '/environmental alarms/d' |sed '/===/d' | sed '/=/d' | sed '/Password/d' | sed '/Bad/d' | sed '/Operating/d' | sed '/support/d' | sed '/Systems/d' | sed '/license/d' | sed '/support/d' | sed '/GNU/d' | sed '/parties/d' |sed '/copyrights/d' | sed '/LGPL/d' |  sed '/Temperature/d' `

if [[ $temperature_output == *"Invalid input detected at"*  ]];
then
    echo "Invalid input"	
else    
    if [[ $temperature_output == *"temperature is at"* ]]  ;
    then
	temperature_output1=`echo "$temperature_output" | grep "temperature is at" | sed 's/[^0-9]*//g'`
        if [ "$temperature_output1" -lt "37" ];
        then
             echo "$temperature_output" |sed '/spawn/d' | sed '/password/d' | sed '/exit/d' | sed '/true/d' | sed '/RSA/d' | sed '/yes/d' | sed '/pass/d'| sed '/ONLY/d' | sed '/computer/d' | sed '/unauthor/d' | sed '/civil/d' | sed '/true/d' | sed '/Hotspot/d' |  sed '/---/d' | sed '/Matthews/d' |  sed '/CCCC/d' | sed '/|/d' | sed '/*/d' | sed '/device/d' | sed '/security/d' | sed '/true/d' |sed '/===/d' | sed '/=/d' | sed '/Password/d' | sed '/Bad/d' | sed '/Operating/d' | sed '/support/d' | sed '/Systems/d' | sed '/license/d' | sed '/support/d' | sed '/GNU/d' | sed '/parties/d' |sed '/copyrights/d' | sed '/LGPL/d' |  sed "/$device_ip/d" | sed '/context.user/d' | sed '/action.ref/d' | sed '/parameters/d' | sed '/hosts/d' | sed '/username/d' | sed '/start/d' | sed '/end/d' | sed '/failed/d' | sed '/return_code/d' | sed '/stderr/d' |  sed "/$entuity_ip/d"
            echo "Temperature is lesser than threshold value."
        else 
            echo "$temperature_output" |sed '/spawn/d' | sed '/password/d' | sed '/exit/d' | sed '/true/d' | sed '/RSA/d' | sed '/yes/d' | sed '/pass/d'| sed '/ONLY/d' | sed '/computer/d' | sed '/unauthor/d' | sed '/civil/d' | sed '/true/d' | sed '/Hotspot/d' |  sed '/---/d' | sed '/Matthews/d' |  sed '/CCCC/d' | sed '/|/d' | sed '/*/d' | sed '/device/d' | sed '/security/d' | sed '/true/d' |sed '/===/d' | sed '/=/d' | sed '/Password/d' | sed '/Bad/d' | sed '/Operating/d' | sed '/support/d' | sed '/Systems/d' | sed '/license/d' | sed '/support/d' | sed '/GNU/d' | sed '/parties/d' |sed '/copyrights/d' | sed '/LGPL/d' |  sed "/$device_ip/d" | sed '/context.user/d' | sed '/action.ref/d' | sed '/parameters/d' | sed '/hosts/d' | sed '/username/d' | sed '/start/d' | sed '/end/d' | sed '/failed/d' | sed '/return_code/d' | sed '/stderr/d' |  sed "/$entuity_ip/d"
            echo "Temperature is greater than threshold value."		
        fi    
    else  
        while read -r line
        do
          if [[ $line == *"OK"*  ]] || [[ $line == *"ok"*  ]] || [[ $line == *"Normal"*  ]] || [[ $line == *"no alarms"*  ]] || [[ $line == *"no temperature alarms"*  ]]
          then
              status+="OK "
          elif [[ $line == *"..."*  ]] || [[ $line == *"id"*  ]];
          then
              status+="dotline "	  
          else
               status+="notok "
          fi
        done < <(printf '%s\n' "$temperature_string")

        #echo $status
        if [[ $status == *"notok"* ]]; 
        then
            temp_status="Fail"
            echo "$temperature_output" |sed '/spawn/d' | sed '/password/d' | sed '/exit/d' | sed '/true/d' | sed '/RSA/d' | sed '/yes/d' | sed '/pass/d'| sed '/ONLY/d' | sed '/computer/d' | sed '/unauthor/d' | sed '/civil/d' | sed '/true/d' | sed '/Hotspot/d' |  sed '/---/d' | sed '/Matthews/d' |  sed '/CCCC/d' | sed '/|/d' | sed '/*/d' | sed '/device/d' | sed '/security/d' | sed '/true/d' |sed '/===/d' | sed '/=/d' | sed '/Password/d' | sed '/Bad/d' | sed '/Operating/d' | sed '/support/d' | sed '/Systems/d' | sed '/license/d' | sed '/support/d' | sed '/GNU/d' | sed '/parties/d' |sed '/copyrights/d' | sed '/LGPL/d' |  sed "/$device_ip/d" | sed '/context.user/d' | sed '/action.ref/d' | sed '/parameters/d' | sed '/hosts/d' | sed '/username/d' | sed '/start/d' | sed '/end/d' | sed '/failed/d' | sed '/return_code/d' | sed '/stderr/d' |  sed "/$entuity_ip/d"
            echo "$temp_status"
        else
            temp_status="Success"
	    echo "$temperature_output" |sed '/spawn/d' | sed '/password/d' | sed '/exit/d' | sed '/true/d' | sed '/RSA/d' | sed '/yes/d' | sed '/pass/d'| sed '/ONLY/d' | sed '/computer/d' | sed '/unauthor/d' | sed '/civil/d' | sed '/true/d' | sed '/Hotspot/d' |  sed '/---/d' | sed '/Matthews/d' |  sed '/CCCC/d' | sed '/|/d' | sed '/*/d' | sed '/device/d' | sed '/security/d' | sed '/true/d' |sed '/===/d' | sed '/=/d' | sed '/Password/d' | sed '/Bad/d' | sed '/Operating/d' | sed '/support/d' | sed '/Systems/d' | sed '/license/d' | sed '/support/d' | sed '/GNU/d' | sed '/parties/d' |sed '/copyrights/d' | sed '/LGPL/d' | sed "/$device_ip/d" | sed '/context.user/d' | sed '/action.ref/d' | sed '/parameters/d' | sed '/hosts/d' | sed '/username/d' | sed '/start/d' | sed '/end/d' | sed '/false/d' | sed '/return/d' | sed '/stderr/d' |  sed "/$entuity_ip/d" 
            echo "$temp_status"
        fi      
        
    fi
fi    


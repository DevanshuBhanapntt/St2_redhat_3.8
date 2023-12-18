param($ip_address,$ci_name,$affected_drive,$username,$password)
try
{
function Get-Ping($ip_address,$ci_name) {
   $host_name = ""
   $IsIP = $ip_address -match '(\d+).(\d+).(\d+).(\d+)'
   if($IsIP)
   {
     $PingHostResponse=ping -a $ip_address
     if($PingHostResponse -match "\(0% loss\)"){ $host_name = "$ip_address" }
     else { write-output " Ping Failed:`n"
		  write-output " $PingHostResponse"
		  exit 1
  		  }
   }
   else{
	  $IPPingResponse=ping $ci_name
    if($IPPingResponse -match "\(0% loss\)")
    { 
       $IPPingResponse=$IPPingResponse | out-string
       $start=$IPPingResponse.indexOf("[")
       $end=$IPPingResponse.indexOf("]")
       $value=$end - $start
       $IP=$IPPingResponse.substring($start+1,$value-1)
       if($IP -eq $ip_address)
       {
	      $PingHostResponse=ping -a $ip_address
          if($PingHostResponse -match "\(0% loss\)"){ $host_name = "$ip_address" }
	      else{ $host_name = "$ci_name" }
	   }
	   else{ $host_name = "$ci_name" }
    }
    else
    {
       $PingHostResponse=ping -a $ip_address
       if($PingHostResponse -match "\(0% loss\)"){ $host_name = "$ip_address" }
       else{ 
	      write-output " Ping Failed:`n"
		  write-output " $PingHostResponse"
		  exit 1
	    }
    }     
   }   
   return $host_name
}

function Get-systemInfo($ip_address,$affected_drive,$ci_name) {
	$global:SystemDrive = ""
	$systeminfoout = Get-WmiObject Win32_OperatingSystem -ComputerName $ip_address -credential $Cred -ErrorAction SilentlyContinue -ErrorVariable systeminfoerror | Select-Object * -excludeproperty "_*","Properties","SystemProperties","Qualifiers","Scope" 
	$systeminfoerror = $systeminfoerror | Out-String
	if ($systeminfoerror.Trim() -eq "") 
	{
		$global:SystemDrive = $systeminfoout.SystemDrive | Out-String
		$global:SystemDrive = $SystemDrive.replace(":",'')
	    write-output " Checking drive ${affected_drive} in ${ip_address}"
        $systeminfoout  = get-wmiobject -query "select * from win32_logicaldisk where Deviceid='${affected_drive}:'" -computername $ip_address -credential $Cred -ErrorAction SilentlyContinue -ErrorVariable systeminfoerror
		if ($systeminfoerror)
		{
			write-output " Unable to connect to the machine and determine the system drive, Escalating the incident.`n"
		    exit 1
		}
		else
		{
			write-output " $ci_name is reachable and the System Drive has been identified as $SystemDrive `n"
		}

	} else {
		write-output " Unable to connect to the machine and determine the system drive, Escalating the incident.`n"
		write-output " $systeminfoerror`n"
		exit 1
	}
	return
}

function parse-dsm-content($ip_address,$ESM_Name,$DriveLetter) {
	$DriveLetter = $DriveLetter.replace(":",'')
	$path = "\\$ip_address\${DriveLetter}$\program files\tivoli\tsm\baclient"
	write-output " ---------------------------------------`n"
	write-output " TSM dsm.opt configuration verification:`n"
	write-output " ---------------------------------------`n"
    write-output " path=$path"
	if (New-PSDrive -Name X -PSProvider FileSystem -Root $path -Credential $Cred )
    {
		$Node = "NodeName[ `t]*$ESM_Name"
        write-output " Node=$Node`n"		
        #The location of the DSMSCHED.log and DSMERROR.log files should be, by default, in the installation folder of the Tivoli product
        $SchedLog = Get-Content X:\dsm.opt | Select-String "^[ `t]*Schedlogname"
        write-output " SchedLog=$SchedLog"
        $ErrorLog = Get-Content X:\dsm.opt | Select-String "^[ `t]*Errorlogname"
        write-output " ErrorLog=$ErrorLog"
        $passwordGenerate = Get-Content X:\dsm.opt | Select-String "^[ `t]*passwordACCESS[ `t]*GENERATE"
        $SchedLogRetention = Get-Content X:\dsm.opt | Select-String "^[ `t]*SCHEDLOGRETENTION[ `t][ `t]*"
        $ErrorLogRetention = Get-Content X:\dsm.opt | Select-String "^[ `t]*ERRORLOGRETENTION[ `t][ `t]*"
        $Domain = Get-Content X:\dsm.opt | Select-String "^[ `t]*DOMAIN[ `t][ `t]*"
        write-output " Domain=$Domain"
        $Nodename = Get-Content X:\dsm.opt | Select-String "^[ `t]*Nodename[ `t][ `t]*"
        $TCPAddress = Get-Content X:\dsm.opt | Select-String "^[ `t]*Tcpserveraddress[ `t][ `t]*"
        $NodenameCheck = $Nodename -imatch $Node
        write-output " TCPAddress=$TCPAddress"
        if ([bool]$passwordGenerate)
        { write-output " $? password Generate is defined in the DSM.opt file`n" }
        else
        { echo "False"
        echo "password Generate option is not defined in the DSM.opt file`n"}
        if ([bool]$SchedLogRetention)
        { write-output " $? SchedLog retention is defined in the DSM.opt file`n" }
        else
        { echo "False"
        echo "SchedLog Retention option is not defined in the DSM.opt file`n"}
        if ([bool]$ErrorLogRetention)
        { write-output " $? ErrorLog retention is defined in the DSM.opt file`n" }
        else
        { echo "False"
        echo "ErrorLog Retention option is not defined in the DSM.opt file`n"}
        if ([bool]$Domain)
        { write-output " $? Domain is defined in the DSM.opt file`n" }
        else
        { echo "False"
        echo "Domain option is not defined in the DSM.opt file`n"}
        if ([bool]$Nodename)
        { write-output " $? Nodename option is defined in the DSM.opt file`n" }
        else
        { echo "False"
        echo "Nodename option is not defined in the DSM.opt file`n"}
        if ([bool]$TCPAddress)
        { write-output " $? TSM Server Address is defined in the DSM.opt file`n" }
        else
        { echo "False"
        echo "TSM Server Address is not defined in the DSM.opt file`n"}
        if ($NodenameCheck)
        {write-output " $? Nodename ($Nodename) defined in the DSM.opt matches ESM Name ($ESM_Name) in this incident`n"}
        else
        {echo "False"
         echo "Nodename ($Nodename) in DSM.opt file does not match the Name of the machine listed in the incident ($ESM_Name)`n"}
	Remove-PSDrive -Name X	 
    }
	else
	{
		write-output " TSM dsm.opt configuration did not pass the health checks.`n"		
	}
	return
}

function get-tsm-services($ip_address){
	write-output " ---------------------------------------`n"
	write-output " TSM Services:`n"
	write-output " ---------------------------------------`n"
	$getservice = Get-WmiObject -Class Win32_Service -Computer $ip_address -credential $Cred | where { $_.Name -like "TSM*"}
    if ($getservice)
    {
		if ($getservice.Name -match "Acceptor") 
		{ 
		   write-output " These TSM Client Acceptor Registry Key properties have been validated:`n"
		   $ClientAcceptorService = $getservice.Name -match "Acceptor"
		   $output=TSMClientAcceptorKey $ip_address $ClientAcceptorService
		   $output | Out-String
		}
		else
		{
			write-output " TSM Acceptor services not found in $ip_address"
		}
		if ($getservice.Name -match "Scheduler") 
		{ 
		   write-output " These TSM Client Scheduler Registry Key properties have been validated:`n"
		   $ClientSchedulerService = "TSM Client Scheduler"
		   $output=TSMClientSchedulerKey $ip_address $ClientSchedulerService
		   $output | Out-String
		}
		else
		{
			write-output " TSM Scheduler services not found in $ip_address`n"			
		}		
    }
	else
	{
		write-output " TSM services not found in $ip_address`n"
	}
	return
}

function TSMClientAcceptorKey($ip_address,$ClientAcceptorService)
  {
	  $TSMClientAcceptorPath = "HKLM:\SYSTEM\CurrentControlSet\Services\$ClientAcceptorService\Parameters"
      $Acceptorproperty = "*"
     if($TSMClientAcceptorPath -match "^HKLM:\\(.*)")
       {$baseKeyAcceptor = [Microsoft.Win32.RegistryKey]::OpenRemoteBaseKey("LocalMachine", $ip_address)}
     elseif($TSMClientAcceptorPath -match "^HKCU:\\(.*)")
       {$baseKeyAcceptor = [Microsoft.Win32.RegistryKey]::OpenRemoteBaseKey("CurrentUser", $ip_address)}
     else
       {Write-Error ("Please specify a fully-qualified registry path " + "(i.e.: HKLM:\Software) of the registry key to open.`n")
     return}
     $Acceptorkey = $baseKeyAcceptor.OpenSubKey($matches[1])
     $returnObjectAcceptor = New-Object PsObject
     foreach($keyPropertyAcceptor in $Acceptorkey.GetValueNames())
     {if($keyPropertyAcceptor -like $Acceptorproperty)
       {$returnObjectAcceptor | Add-Member NoteProperty $keyPropertyAcceptor $Acceptorkey.GetValue($keyPropertyAcceptor)}
     }
     $returnObjectAcceptor
     $Acceptorkey.Close()
     $baseKeyAcceptor.Close()
	 return
}

function TSMClientSchedulerKey($ip_address, $ClientSchedulerService)
{
	$TSMClientSchedulerPath = "HKLM:\SYSTEM\CurrentControlSet\Services\$ClientSchedulerService\Parameters"
    $Schedulerproperty = "*"
    if($TSMClientSchedulerPath -match "^HKLM:\\(.*)")
      {$baseKeyScheduler = [Microsoft.Win32.RegistryKey]::OpenRemoteBaseKey("LocalMachine", $ip_address)}
    elseif($TSMClientSchedulerPath -match "^HKCU:\\(.*)")
      {$baseKeyScheduler = [Microsoft.Win32.RegistryKey]::OpenRemoteBaseKey("CurrentUser", $ip_address)}
    else
     {Write-Error ("Please specify a fully-qualified registry path " + "(i.e.: HKLM:\Software) of the registry key to open.`n")
    return}
    $Schedulerkey = $baseKeyScheduler.OpenSubKey($matches[1])
    $returnObjectScheduler = New-Object PsObject
    foreach($keyPropertyScheduler in $Schedulerkey.GetValueNames())
    {if($keyPropertyScheduler -like $Schedulerproperty)
        {$returnObjectScheduler | Add-Member NoteProperty $keyPropertyScheduler $Schedulerkey.GetValue($keyPropertyScheduler)}
    }
    $returnObjectScheduler
    $Schedulerkey.Close()
    $baseKeyScheduler.Close()
	return
}

function tsm-session-check($ip_address)
{
	    write-output " ---------------------------------------`n"
	    write-output " Starting to check the port`n"
		write-output " ---------------------------------------`n"
        $port=1500
        $timeout=300
	    #$ErrorActionPreference = "SilentlyContinue"
	    $tcpclient = new-Object system.Net.Sockets.TcpClient
	    $iar = $tcpclient.BeginConnect($ip_address,$port,$null,$null)
        #write-output " iar=$iar"
        $wait = $iar.AsyncWaitHandle.WaitOne($timeout,$false)
	    if(!$wait)
	    {
	        $tcpclient.Close()
	        write-output " TSM Server is accepting sessions.`n"
	    }
	    else
	    {
	        $error.Clear()
	        $tcpclient.EndConnect($iar) | out-Null
			write-output " TSM Server is not accepting sessions.`n"
	        $tcpclient.Close()
	    }
		return
}

#Main
write-output " TSM Health Checks:`n"
$pass = ConvertTo-SecureString -AsPlainText $password -Force
$global:Cred = New-Object System.Management.Automation.PSCredential -ArgumentList $username,$pass
$hostName = Get-Ping $ip_address $ci_name
Get-systemInfo $hostName $affected_drive $ci_name
$DriveLetter = $global:SystemDrive
parse-dsm-content $hostName $ci_name $DriveLetter.Trim()
write-output " `n"
get-tsm-services $hostName
tsm-session-check $hostName
write-output " `n"
write-output " All TSM Basic HealthChecks have been completed.`n"
}
catch
{
   write-output " Exception Occurred: $_.Exception"	
   exit 1
}

param($ip_address,$ci_name,$affected_drive,$username,$password,$is_eighthour_ci,$service_window_check,$dignity_healthservers)
try
{
  $pass = ConvertTo-SecureString -AsPlainText $password -Force
  $global:Cred = New-Object System.Management.Automation.PSCredential -ArgumentList $username,$pass
  
 function get-dsmc-process($ip_address){
    $exist = "false"
    $ProcessName = "dsmc.exe"
    $getprocess = get-wmiobject -query "select name from win32_process" -computername $ip_address -Credential $Cred
	$dsmc_found = "false"
    if($?)
    {
      if($getprocess)
      {
        $getprocess | ForEach-Object {
        $a=$_.Name
        if ($a.ToUpper() -eq $ProcessName.ToUpper())
        {
           $dsmc_found = "true"
        }}
      }
      else
      { 
         $dsmc_found = "false"
      }
	 $dsmc_found
    }
    else
    {
       write-output " Unable to connect to server to see if Dsmc.exe process is already running.`n"
       exit 1
    }	
    return
  }
  
  function tsm-service-window-check($ip_address,$affected_drive) {
	  $path = "\\$ip_address\${affected_drive}$\program files\tivoli\tsm\baclient"
	if ($is_eighthour_ci -eq "false")
	{
      if (New-PSDrive -Name X -PSProvider FileSystem -Root $path -Credential $Cred) {
         $processing_time=get-content X:\dsmsched.log|select-string "^*Elapsed processing time*"|select-object -last 1
		 if($processing_time){
			 $ElapsedProcessingTime = $processing_time | select-string "Elapsed processing time:"
			 $ElapsedProcessingTime = $ElapsedProcessingTime.split(":")[1]
			 $ElapsedProcessingTime = $ElapsedProcessingTime.Trim()
			 $ElapsedProcessingTimeMins = $ElapsedProcessingTime.split(":")[1]
			 $ElapsedProcessingTimeHours = $ElapsedProcessingTime.split(":")[0]
			 $ElapsedProcessingTimeMins = $ElapsedProcessingTimeMins -as [int]
			 $ElapsedProcessingTimeHours = $ElapsedProcessingTimeHours -as [int]
			 $BackupProcessingTimeMinutes = $ElapsedProcessingTimeHours + 0.5
			 $BackupProcessingTimeMinutes = $BackupProcessingTimeMinutes * 60
			 $BackupProcessingTimeMinutes
		 }
		 else
		 {
			 $BackupProcessingTimeMinutes = 300
			 $BackupProcessingTimeMinutes
		 }
      }
	}
	else
	{
		$BackupProcessingTimeMinutes = 480
		$BackupProcessingTimeMinutes
	}
	
     return
  } 
 
  function Arizona-validate ([datetime]$time = (get-date))
  {  
  
     [System.TimeZoneinfo]::GetSystemTimeZones() |  where { $_.StandardName -eq 'US Mountain Standard Time' } | select @{n='Time';e={[System.TimeZoneinfo]::ConvertTime($time,$_).tostring('hh:mm tt')}},id,@{n='DST';e={$_.IsDaylightSavingTime($time)}},DisplayName | ft -a -HideTableHeaders | Out-String	 
     $arizonatime = $arizonatime.Substring(0,10)
	 $arizonatime = $arizonatime.Trim()
	 if($arizonatime -match "PM") { 
	     $arizonatime.replace("PM", '')
		 $arizonatime = $arizonatime.Trim()
		 $arizonatimehours = $arizonatime.split[0]
		 $arizonatimehours = $arizonatimehours -as [int]
		 $arizonatimehours = $arizonatimehours + 12
		 $arizonatimehours = $arizonatimehours * 60
		 $arizonatimemins = $arizonatime.split[1]
		 $arizonatimemins = $arizonatimemins -as [int]
		 $arizonatimetotalmins = $arizonatimehours + $arizonatimemins
		 $arizonatimetotalmins
	   }
	 else
	 {
		 $arizonatime.replace("AM", '')
		 $arizonatime = $arizonatime.Trim()
		 $arizonatimehours = $arizonatime.split[0]
		 $arizonatimehours = $arizonatimehours -as [int]
		 $arizonatimehours = $arizonatimehours * 60
		 $arizonatimemins = $arizonatime.split[1]
		 $arizonatimemins = $arizonatimemins -as [int]
		 $arizonatimetotalmins = $arizonatimehours + $arizonatimemins
		 $arizonatimetotalmins
	 }
  }

  
  
#Main
$pass = ConvertTo-SecureString -AsPlainText $password -Force
$global:Cred = New-Object System.Management.Automation.PSCredential -ArgumentList $username,$pass
$intofunction = 0
$IsProcessRunning = get-dsmc-process $ip_address
if ($IsProcessRunning -eq "false"){	
    $intofunction = 1
	$BackupProcessingTimeMinutes = tsm-service-window-check $ip_address $affected_drive
	if ($service_window_check -eq "true")
	{
		$arizonatimetotalmins = Arizona-validate
		if ($arizonatimetotalmins -ge 540 -and $arizonatimetotalmins -le 545)
		{
			write-output " Processing the manual backup on this machine would extend within the Dignity Health Service Window (between 9:00 AM and 6:00 PM Phoenix, Arizona time). Escalating for further action.`n"
			exit 1
		}
		else
		{
		  if ($dignity_healthservers -match $ci_name)
		  {
			  write-output " This Server is part of the Servers that run the Allscripts application. Before proceeding with the backup, the application owner needs to be contacted. Escalating for further processing.`n"
			  exit 1
		  }
		  else
		  {
			  $BackupProcessingTimeMinutes = $BackupProcessingTimeMinutes
		  }
		}
	}
	else
	{
		write-output "ServiceWindowCheck is not required for this customer.`n"
		$BackupProcessingTimeMinutes = $BackupProcessingTimeMinutes
	}
	
	write-output " Automation found the backup processing time for $ci_name CI = $BackupProcessingTimeMinutes minutes `n"

}
else
{
   write-output " Unable to start backup.  Dsmc.exe process already running OR unable to start new instance.`n"
   exit 1
}


}
catch
{
  if ($intofunction -eq 0){
   write-output " Automation could not get the local time and will not be able to calculate Backup Process Time so we are going to escalate this incident.`n"
   write-output " Exception Occurred: $_.Exception"
   exit 1
  }
  elseif ($intofunction -eq 1){
   write-output " Automation could not get the last Elapsed Processing Time from the dsmsched.log file so we are going to escalate this incident.`n"
   write-output " Exception Occurred: $_.Exception"
   exit 1
  }
  else
  {
   write-output " Exception Occurred: $_.Exception"	
   exit 1
}
}

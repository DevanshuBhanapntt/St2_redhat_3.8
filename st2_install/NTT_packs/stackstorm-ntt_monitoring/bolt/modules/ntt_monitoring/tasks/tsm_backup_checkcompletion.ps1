param($ip_address,$ci_name,$system_drive_letter,$username,$password,$file_name_string,$process_id,$last_iteration,$incident_state)

$system_drive_letter = $system_drive_letter.trim()
try
{
  $pass = ConvertTo-SecureString -AsPlainText $password -Force
  $global:Cred = New-Object System.Management.Automation.PSCredential -ArgumentList $username,$pass
  $BackupStatus = ""
  $BatchFileName = "tsm-$file_name_string.bat"
  $ResultFileName = "result-$file_name_string.bat"
 function get-dsmc-process($ip_address){
    $exist = "false"
    $ProcessName = "dsmc.exe"
	$dsmc_found="false"
    $getprocess = get-wmiobject -query "select name from win32_process" -computername $ip_address -Credential $Cred
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

#Main  
$IsProcessRunning = get-dsmc-process $ip_address
if ($IsProcessRunning -eq "false" -and "$incident_state" -eq "2" ){	
   write-output "Backup stalled, dsmc.exe process not running after initiating backup`n"
   exit 1
}
elseif ($IsProcessRunning -eq "false" -and "$incident_state" -eq "-5" ){	
   $path="\\$ip_address\${system_drive_letter}$\Windows\Temp"
    write-output "path=$path`n"
   if (New-PSDrive -Name X -PSProvider FileSystem -Root $path -Credential $Cred)
   {
     $bkp_output = Get-Content X:\$ResultFileName
	 if ($bkp_output -match "finished with" -and $bkp_output -match "failure")
	 {
		 $BackupStatus = "failure"
		 write-output "Backup finished with failure."
		 write-output "BACKUP STATUS : $BackupStatus "
	 }
	 elseif ($bkp_output -match "Elapsed" -and $bkp_output -match "completed successfully")
	 {
	     $BackupStatus = "success"
		 write-output "BACKUP STATUS : $BackupStatus "
	 }
	 else
	 {
		 write-output "Backup stalled, backup has stopped unsuccessfully."
		 $BackupStatus = "dsmc failure `n"
		 write-output "BACKUP STATUS : $BackupStatus "
	 }
   Remove-PSDrive -Name X
   }
   else
   {
	   write-output "Escalating Incident:`n
       The backup batch file  $system_drive_letter\Windows\temp\$BatchFileName was executed but automation could not check the status.`n"
	   exit 1}
}
elseif ($IsProcessRunning -eq "true")
{
    $path="\\$ip_address\${system_drive_letter}$\Windows\Temp"
    write-output "path=$path`n"
   if (New-PSDrive -Name X -PSProvider FileSystem -Root $path -Credential $Cred)
   {
     $bkp_output = Get-Content X:\$ResultFileName
	 if ($bkp_output -match "finished with" -and $bkp_output -match "failure")
	 {
		 $BackupStatus = "failure"
		 write-output "BACKUP STATUS : $BackupStatus "
	 }
	 elseif ($bkp_output -match "Elapsed" -and $bkp_output -match "completed successfully")
	 {
	     $BackupStatus = "success"
		 write-output "BACKUP STATUS : $BackupStatus "
	 }
	 else
	 {
		 if ($last_iteration -eq "true")
		 {
			 $BackupStatus = "suspend failure `n"
		     write-output "BACKUP STATUS : $BackupStatus "
		 }
		 else
		 {
		    $BackupStatus = "suspend"
		    write-output "BACKUP STATUS : $BackupStatus "
		 }
	 }
   }
   else
   {
	   write-output "Escalating Incident:`n
       The backup batch file  $system_drive_letter\Windows\temp\$BatchFileName was executed but automation could not check the status.`n"
	   exit 1}
}
else
{
	write-output "Escalating Incident:`n
Automation could not check the status of the dsmc.exe process so we will escalate this incident.   The backup batch file  $system_drive_letter\Windows\temp\$BatchFileName was executed but automation could not check the status."
    Write-Host $_
   exit 1
}
}
catch
{
	write-output "TSM Backup completion Failed.`n"
	Write-Host $_
	exit 1
	
}

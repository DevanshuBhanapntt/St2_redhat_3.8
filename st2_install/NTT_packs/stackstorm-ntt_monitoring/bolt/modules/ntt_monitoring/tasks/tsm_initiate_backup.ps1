param($ip_address,$ci_name,$system_drive_letter,$username,$password)

$system_drive_letter = $system_drive_letter.trim()
$system_drive_letter_path = "$system_drive_letter"+":"
$system_drive_letter_value = "$system_drive_letter"+"$"
try
{
$pass = ConvertTo-SecureString -AsPlainText $password -Force
$global:Cred = New-Object System.Management.Automation.PSCredential -ArgumentList $username,$pass
$datetime = Get-Date -UFormat %s
$datetime = $datetime.split(".")
$datetime = $datetime[0]
$BatchFileName = "tsm-$datetime.bat"
$ResultFileName = "result-$datetime.bat"
$bkp_command = "cmd /c $system_drive_letter_path\Windows\temp\$BatchFileName"
$path="\\$ip_address\$system_drive_letter_value\Windows\Temp"
write-output "BatchFile $BatchFileName created in path $path"
write-output "path=$path`n"
if (New-PSDrive -Name X -PSProvider FileSystem -Root $path -Credential $Cred)
{
write-output "cd ${system_drive_letter_path}\Program Files\Tivoli\TSM\baclient" | add-content $path\$BatchFileName
write-output "dsmc i>>${system_drive_letter_path}\WINDOWS\Temp\$ResultFileName" | add-content $path\$BatchFileName
write-output "@echo Command has finished running >>${system_drive_letter_path}\WINDOWS\Temp\$ResultFileName" | add-content $path\$BatchFileName
write-output ""
$PSBatchFilePath = "$path\$BatchFileName"
Remove-PSDrive -Name X

write-output "PSBatchFilePath=$PSBatchFilePath`n"
$BatchFilePath = ${PSBatchFilePath}.Replace("`"","")
$BatchFilePath2 = ${BatchFilePath}.Replace("`'","")
write-output "Executing $BatchFilePath2 on $ip_address`n"
#Start-Sleep -s 4
$bkp_out = invoke-wmimethod -ComputerName $ip_address -Credential $Cred -path win32_process -name create -argumentlist "$BatchFilePath2"
$ProcessId = $bkp_out.ProcessId
write-output "Process ID : $ProcessId `n"
}
else
{
	write-output "Automation failed to initiate TSM Backup`n"
	exit 1
}
}
catch
{
	write-output "Automation failed to initiate TSM Backup.`n"
	Write-Host $_
	exit 1
}

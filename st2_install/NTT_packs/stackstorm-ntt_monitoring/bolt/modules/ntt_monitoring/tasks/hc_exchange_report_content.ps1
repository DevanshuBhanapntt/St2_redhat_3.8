param([String]$filepath,
      [String]$filematchstring,
	  [String]$username,
      [String]$password)
	  
$date = (Get-Date).adddays(-1)

$pass = ConvertTo-SecureString -AsPlainText $password -Force
$Cred = New-Object System.Management.Automation.PSCredential -ArgumentList $username,$pass

New-PSDrive -Name X -PSProvider FileSystem -Root $filepath -Credential $Cred
$file = Get-ChildItem -path X:\Log | Where-Object { ($_.name -like "$filematchstring") -and ($_.LastWriteTime -gt $date) } | select -last 1
Remove-PSDrive -Name X

Write-Output "Hello this is the path's content."
$file

if($file.Fullname -eq $null) {

  Write-Output "SCRIPT ERROR: No file found.  NULL value returned from Get-ChildItem cmdlet."

} else {

  $filename = $file.FullName

  $data = Get-Content $filename

  Write-Output $data

}

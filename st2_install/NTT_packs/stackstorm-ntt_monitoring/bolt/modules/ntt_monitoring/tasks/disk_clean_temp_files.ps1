###################################################################################################################################
# Remove all files from given temp folders if remove_temp_files is passed
#
###################################################################################################################################
Param(
  [String]  $ci_address,
  [String]  $disk_name,
  [Boolean] $remove_temp_files,
  [Boolean] $remove_temp_ie_files
)
Try {
  # Save the number of files that were deleted to return later
  $dCount = 0

  $path="\\"+$ci_address+"\"+$disk_name+"$"

  $ErrorActionPreference="Continue"

  $OSName = (gwmi win32_operatingsystem -computername $ci_address).caption
  if ($OSName -match "2003")
  {
    $ProfilesPath = $path+"\Documents and Settings"
    $TempIEFiles = "\Local Settings\Temporary Internet Files\Content.IE5"
    $TempFiles="\Local Settings\Temp"
  }
  else
  {
    $ProfilesPath = $path+"\Users"
    if ($OSName -match "2012" -and -not ($OSName -match "2012 R2")) {$TempIEFiles = "\AppData\Local\Microsoft\Windows\Temporary Internet Files\Content.IE5"} #For 2012 with IE 10
    #else {$TempIEFiles = "\AppData\Local\Microsoft\Windows\INetCache"} #For OS with IE 11, base directory, lots of symlinks may reduce effectiveness
    #else {$TempIEFiles = "\AppData\Local\Microsoft\Windows\INetCache\Low\IE"} #For OS with IE 11, this is effective
    else {$TempIEFiles = "\AppData\Local\Microsoft\Windows\INetCache\IE"} #For OS with IE 11, this is effective
    #AppData\Local\Packages\Microsoft.MicrosoftEdge_8wekyb3d8bbwe\AC\MicrosoftEdge\Cache     Path for Edge Browser Windows 10 and later?
    $TempFiles="\AppData\Local\Temp"
  }
  $ProfileCount=0
  $TempIEFilesSize=0
  $TempFilesSize=0
  $Profiles=get-childitem $ProfilesPath -ErrorAction SilentlyContinue|where {$_.PSIsContainer}

  #------------------------------Added Arul -29-July-2020 Getting the Process ID & Print------------------------------------------------
  $Process_ID = (Get-Process -Id $PID).Id
  Write-output "Process ID:       $Process_ID"
  $CurrentUser = $(whoami)
  Write-Host "current user: $CurrentUser"
  $CheckHost=$env:COMPUTERNAME
  $CheckHostIP = [System.Net.Dns]::GetHostAddresses($CheckHost)|?{$_.scopeid -eq $null}|%{$_.ipaddresstostring}
  write-output "Script executed at automation server Name : $CheckHost"
  $CheckHostIP = $CheckHostIP.split(" ")
  if ($CheckHostIP.length -gt 0 )
  {
      $CheckHostIP =$CheckHostIP[0].Trim()
  }
  else
  {
      $CheckHostIP =""
  }
  write-output "Script executed at automation server IP : $CheckHostIP"

  write-output "IP Address: $ci_address"
  write-output "Drive: $disk_name"+":"
  write-output "Function: Delete User Profile Temp Files"


  if ($Profiles)
  {
    if($remove_temp_files -eq "true" -and $remove_temp_ie_files -eq "true")
    {
      write-output "Deleting temp files and cached IE browser files in profiles"
    }
    elseif($remove_temp_ie_files -eq "true")
    {
      write-output "Deleting cached IE browser files in profiles"
    }
    elseif($remove_temp_files -eq "true")
    {
      write-output "Deleting temp files in profiles"
    }

    foreach($p in $Profiles)
    {
      $ProfileCount=$ProfileCount+1

      if($remove_temp_ie_files -eq "true")
      {
        $TempIEFilesPath = $ProfilesPath+"\"+$p.Name+$TempIEFiles
        if (test-path $TempIEFilesPath)
        {
          $TempIECleanup=get-childitem $TempIEFilesPath -force
          foreach($T in $TempIECleanup)
          {
            $delete=$TempIEFilesPath+"\"+$T
            $Error.Clear()
            remove-item $delete -recurse -force -ErrorAction SilentlyContinue -ErrorVariable deleteissue
            if ($deleteissue)
            {
              write-output "Unable to delete: $delete"
            }
            else {
              write-output "Deleted: $delete"
              $dCount += 1
            }
          } #foreach
          $currentIESize=(get-childitem $TempIEFilesPath -recurse -force -ErrorAction SilentlyContinue| where {!$_.PSIsContainer} | Measure-Object -Sum Length).Sum
          if($currentIESize){$TempIEFilesSize=$TempIEFilesSize+$currentIESize}
        } #if (test-path $TempIEFilesPath)
     } #if($remove_temp_ie_files -eq "true")

     if($remove_temp_files -eq "true")
     {
        $TempFilesPath = $ProfilesPath+"\"+$p.Name+$TempFiles
        if (Test-Path $TempFilesPath)
        {
          $TempCleanup=get-childitem $TempFilesPath -force
          foreach($T in $TempCleanup)
          {
            $delete=$TempFilesPath+"\"+$T
            $Error.Clear()
            remove-item $delete -recurse -force -ErrorAction SilentlyContinue -ErrorVariable deleteissue

            if ($deleteissue)
            {
              $message=$deleteissue.errordetails.message
              write-output "Unable to delete: $delete"
            }#if
            else {
              write-output "Deleted: $delete"
              $dCount += 1
            }
          } #foreach
         $currentTempSize=(get-childitem $TempFilesPath -recurse -force -ErrorAction SilentlyContinue| where {!$_.PSIsContainer} | Measure-Object -Sum Length).Sum
         if($currentTempSize){$TempFilesSize=$TempFilesSize+$currentTempSize}
        } #if (Test-Path $TempFilesPath)
     } #if($remove_temp_files -eq "true")
    } #foreach($p in $Profiles)

    write-output "Sizes of temporary files remaining in $ProfileCount profiles"


    if($remove_temp_ie_files -eq "true"){"Remaining cached IE browser files(KB) : "+$TempIEFilesSize}
    if($remove_temp_files -eq "true"){"Remaining temporary files(KB) : "+$TempFilesSize}
  } #if ($Profiles)
  else
  {
    $disk_name=$disk_name+":"
    Write-Output "No profile directories found on drive $disk_name of $ci_address"
  }

  Write-Output "Total deleted files: $dCount"

  exit 0

} Catch {
  $errortext = $error | Out-string
  $errortext = $errortext.substring(0, $errortext.indexof("At "))
  $errortext = $errortext.substring($errortext.indexof(":") + 2, $errortext.length - $errortext.indexof(":") - 3)
  $errortext
  exit 1
}
###################################################################################################################################
# Remove user profiles that are older than the given age to clear disk space
#
###################################################################################################################################
Param(
  [String] $ci_address,
  [String] $disk_name,
  [Int]    $profile_age_days
)
Function RemoveProfiles2008($IPAddress, $AffectedDrive, $Profiles) {
  Write-Host "Function RemoveProfiles2008"
  # Initialize counter variables...
  $dCount = 0

  ForEach ($ProfileToDelete in $Profiles) {
    $pName = $ProfileToDelete.Name.Replace("\","\\")
    $query = "select * from Win32_UserProfile where LocalPath = '" + $pName + "'"
    $ProfileObject = Get-WmiObject -query $query -ComputerName $IPAddress

    If ($ProfileObject.Loaded -eq $false) {
      # Write-Host "Would have ${ProfileObject}.Delete()"
      $ProfileObject.Delete()
      $ReturnValue = $?
    } # If

    If ($ReturnValue) {
      $dCount += 1
      Write-Host -NoNewline "Deleted Profile:  "
      Write-Host $ProfileObject.LocalPath
    } Else {
      Write-Host -NoNewline "Could not delete: "
      Write-Host $ProfileObject.LocalPath
    } # If
  } # ForEach

  Return $dCount
} # Function RemoveProfiles2008

Function RemoveProfiles2003($IPAddress, $AffectedDrive, $Profiles, $ProfilePrefix) {
  Write-Host "Function RemoveProfiles2003"

  # Initialize counter variables...
  $dCount = 0

  # Define TEMP path...
  $tempPath = "\\$IPAddress\" + $AffectedDrive.Replace(":", "$") + "\\TEMP"
  If ((Test-Path $tempPath) -eq $false) {
    New-Item -Path $tempPath -ItemType Directory > $null 2> $null
    If ($? -eq $false) {
      Write-Host "Could not access or create $tempPath. Cannot continue removing profiles."
      Return
    } Else {
      Write-Host "Created directory $tempPath."
    } # If
  } # If

  ForEach ($ProfileToDelete in $Profiles) {
    $pNameUNC = "\\$IPAddress\" + $ProfileToDelete.Name.Replace(":", "$")
    $pBaseName = Split-Path $ProfileToDelete.Name -Leaf
    $pDirName = Split-Path $ProfileToDelete.Name
    $pDirUNC = "\\$IPAddress\" + $pDirName.Replace(":", "$")
    $pName = $ProfileToDelete.Name.Replace("\", "\\")
    $query = "Select * From CIM_LogicalFile Where Name = '" + $pName + "'"
    $ProfileObject = Get-WmiObject -Query $query -ComputerName $IPAddress

    $dPath = "\\$IPAddress\root\cimv2:CIM_LogicalFile.Name=`"" + $ProfileObject.Name.Replace("\", "\\") + "`""

    # Can $dPath be moved?
    # Write-Host "Would have Move-Item $pNameUNC $tempPath 2"
    Move-Item $pNameUNC $tempPath 2> $null
    If ($?) {
      # Yes it can, so move it back before deletion...
      # Write-Host "Would have Move-Item $tempPath\\$pBaseName $pDirUNC"
      Move-Item "$tempPath\\$pBaseName" "$pDirUNC"
    } Else {
      # No, it can't, so there must be files locked.  Say so and move on...
      Write-Host -NoNewline "Skipped:           "
      Write-Host -NoNewline $ProfileToDelete.Name
      Write-Host " (Contains locked files.)"
      Continue
    } # If

    # Write-Host "Would have Invoke-WmiMethod -Path $dPath -Name delete"
    $ReturnValue = Invoke-WmiMethod -Path "$dPath" -Name delete
    $ReturnValue = 0

    $rVal = $ReturnValue.ReturnValue
    If ($rVal -eq 0) {
      $dCount += 1
      Write-Host -NoNewline "Deleted Profile: "
      Write-Host $ProfileObject.Name
    } Else {
      Write-Host -NoNewline "Could not delete: "
      Write-Host $ProfileObject.Name
    } # If
  } # ForEach

  Return $dCount
} # Function RemoveProfiles2003

# Main:
Try {
  # Establish cut-off date for profiles too old to retain...
  $OldestProfileDateAllowed = (Get-Date).AddDays(-$profile_age_days).ToString('yyyyMMddHHmmss.ffffff')

  # Determine Server OS, as Windows 2008's profiles are located differently from older systems...
  $OSVersion = [environment]::OSVersion.Version.Major

  # Define Profile Root directory:
  # OS version numbers can be found here: https://www.gaijin.at/en/infos/windows-version-numbers
  # Windows Server 2008 corresponds with OS major version 6.0
  Switch ($OSVersion) {
    {($_ -gt 5)} `
            {$ProfilePrefix = "\\Users\\"}
    default {$ProfilePrefix = "\\Documents and Settings\\"}
  } # Switch

  # Check if just the disk name was given instead of the path
  if ($disk_name.length -eq 1) {
    $disk_name += ':'
  }

  # List Profiles on Server:
  $Profiles = Get-WmiObject -Query "Select * From CIM_LogicalFile Where Drive = '$disk_name' And Path = '$ProfilePrefix'" `
    -ComputerName $ci_address |
    Where-Object {$_.Hidden -eq $false} |
    Where-Object {$_.FileType -eq "File Folder"} |          # To ensure only folders are removed...
    Where-Object {$_.FileName -ne "Administrator"} |        # To leave Administrator profiles in place...
    Where-Object {$_.FileName -ne "All Users"} |            # Windows 2003-...
    Where-Object {$_.FileName -ne "Public"} |               # Windows 2008+...
    Where-Object {$_.FileName.contains("Adm") -eq $false} |         # To leave Adm profiles
    Where-Object {$_.LastModified.Replace("\-...$", "") -le $OldestProfileDateAllowed}

  Write-Host "Maximum age for profiles (days): $profile_age_days"
  Write-Host "Oldest Profile Allowed: $OldestProfileDateAllowed"
  Write-Host "Server OS Version: $OSVersion"
  Write-Host "Profile root: $disk_name$ProfilePrefix"

  If ($Profiles -ne $null) {
    Switch ($OSVersion) {
      {($_ -gt 5)} `
              { $dCount = RemoveProfiles2008 $ci_address $disk_name $Profiles }
      default { $dCount = RemoveProfiles2003 $ci_address $disk_name $Profiles $ProfilePrefix }
    } # Switch

    $count = If ($Profiles.Length) { $Profiles.Length } Else { 1 }
  } Else {
    Write-Host "No eligible profiles found on server [$ci_address] at path [$disk_name$ProfilePrefix]."
    $dCount = 0
    $count = 0
  } # If

  Write-Host "Total deleted profiles: $dCount"
  Write-Host "Total profiles: $count"

  exit 0

} Catch {
  $errortext = $error | Out-string
  $errortext = $errortext.substring(0, $errortext.indexof("At "))
  $errortext = $errortext.substring($errortext.indexof(":") + 2, $errortext.length - $errortext.indexof(":") - 3)
  $errortext
  exit 1
}

###################################################################################################################################
# Try to clear space for the given hard drive by running cleanmgr tasks (empty recycle bin)
#
###################################################################################################################################
Param(
  [String] $ci_address,
  [String] $disk_name
)
Try {
  # Define recycle bin path for different OS version...
  $Recycler2003 = 'RECYCLER'
  $Recycler2008 = '$Recycle.Bin'

  # Determine Server OS, as Windows 2008's profiles are located differently from older systems...
  $OSVersion = [environment]::OSVersion.Version.Major

  # OS version numbers can be found here: https://www.gaijin.at/en/infos/windows-version-numbers
  # Windows Server 2008 corresponds with OS major version 6.0
  If ($OSVersion -gt 5) {$Recycler = $Recycler2008}
  Else { $Recycler = $Recycler2003 } # If

  # Initialize counter variables...
  $count = 0
  $dCount = 0
  $dSize = 0
  $tSize = 0

  # Check if just the disk name was given instead of the path
  if ($disk_name.length -eq 1) {
    $disk_name += ':\'
  }

  $Path = '\\' + $ci_address + '\' + $disk_name.Replace(":", "$") + '\' + $Recycler + '\*\*\'

  [array]$FileList = Get-ChildItem $Path -Force -Recurse -ErrorAction SilentlyContinue  |
    Where-Object { ! $_.PSIsContainer } |
    Select-Object *
  [array]$DirList = Get-ChildItem $Path -Force -Recurse -ErrorAction SilentlyContinue  |
    Where-Object { $_.PSIsContainer } |
    Select-Object * |
    Sort-Object FullName -Descending
  If (($DirList -ne $null ) -and ($FileList -ne $null)) {
    $FileList = $FileList + $DirList
  }
  If ($?) {
    If ($FileList -eq $null) {
      # Directory is empty. Say so and move on.
      Write-Output "No files found in Recycle Bin."
      Write-Output "Total deleted files: 0"
      Continue
    }
    ForEach ($_ in $FileList) {
      $count += 1
      $fPath = $_.FullName
      If (Test-Path -LiteralPath $fPath) {
        Write-Output "Would have Remove-Item $fPath -Force -Recurse -ErrorAction SilentlyContinue."
        Remove-Item $fPath -Force -Recurse -ErrorAction SilentlyContinue
        If($?) {
          Write-Output $fPath
          $dCount += 1
          $dSize += $_.Length
        } Else {
          $tSize += $_.Length
        } # If
      } Else {
        Write-Output "$fPath not found on $ci_address."
      }
    } # ForEach
  } # If

  Write-Output "Total files: $count"
  Write-Output "Total deleted files: $dCount"
  Write-Output "Total size of deleted files: $dSize"

  exit 0

} Catch {
  $errortext = $error | Out-string
  $errortext = $errortext.substring(0, $errortext.indexof("At "))
  $errortext = $errortext.substring($errortext.indexof(":") + 2, $errortext.length - $errortext.indexof(":") - 3)
  $errortext
  exit 1
}

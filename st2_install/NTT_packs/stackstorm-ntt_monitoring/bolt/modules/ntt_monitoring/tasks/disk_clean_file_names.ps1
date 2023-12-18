###################################################################################################################################
# Remove all files with the given names(s) on the given disk and folder path. Folder paths should be included with the file name
# if there is any. Example file_names: ["\text.txt", "\opt\file.txt"]
###################################################################################################################################
Param(
  [String] $ci_address,
  [String] $disk_name,
  [Array]  $file_names
)
Try {

  $names = $file_names -join ', '

  Write-Host "Starting DeleteFilesByName using $file_names ..."

  # Check if just the disk name was given instead of the path
  if ($disk_name.length -eq 1) {
    $disk_name += ':\'
  }

  #Initialize counter variables...
  $count = 0
  $fnamecount = 0
  $dCount = 0
  $dSize = 0
  $filterlist=""

  ForEach ($_ in $file_names ) {
    $FName=$_
    $FilePart =  Split-Path -Path "$FName" -NoQualifier
    $FileName = $FilePart.Replace("\","\\")
    $FilePath = Join-Path -Path $disk_name -ChildPath "$FileName"
    If ($fnamecount -eq 0) {
      $filterlist = "name='$FilePath'"
    } Else {
      $filterlist = "$filterlist OR name='$FilePath'"
    } #If
    $fnamecount += 1
  } #ForEach
  write-output "Found $fnamecount filenames configured for deletion"
  #write-output "Executing command: Get-wmiobject CIM_DataFile -ComputerName $ci_address -filter \"$filterlist\" to find the specified files"
  if ("$filterlist" -ne "") {
      $FilesToDelete = Get-wmiobject CIM_DataFile -ComputerName $ci_address -filter "$filterlist"
  }
  else
  {
      $FilesToDelete = @()
  }
  Write-Output "We have the list of files $FilesToDelete"
  if ($FilesToDelete.count) {
    "Found $($FilesToDelete.count) files meeting the deletion criteria"
    $deleteflag = 0
  }
  elseif ($FilesToDelete) {
    "Found 1 file meeting the deletion criteria"
    $deleteflag = 0
  }
  else {
    "Found 0 files meeting the deletion criteria"
    $deleteflag = 1
  } #if

  if ($deleteflag -eq 0){
    foreach ($f in $FilesToDelete){
      $filename = $f.name.Substring(2, $f.name.length - 2)
      $driveletter = $f.name.Substring(0, 1)
      $filename = '\\' + $ci_address + '\' + $driveletter + "$" + $filename
      $filesize = [math]::ceiling($f.filesize / 1024)
      remove-item $filename -ErrorVariable errortext -ErrorAction SilentlyContinue
      if ($errortext){
        $errortext = $errortext.errordetails.message
        "ERROR : $errortext"
      }
      else{
        Write-Output "Deleted: $filename Size: $filesize"
        $dCount += 1
        $dSize += $filesize
      } #if
    } #foreach
  } #if

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

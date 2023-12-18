###################################################################################################################################
# Queries Win32_LogicalDisk ($AffectedDrive) to determine how much space is being used and returns the disk size and free space
#
###################################################################################################################################
Param(
  [String]$ci_address,
  [String]$disk_name
)
Try {
  $disk = get-wmiobject -query "select * from win32_logicaldisk where Deviceid='${disk_name}:'" -computername $ci_address
  # verify that the command succeeded
  if ($?) {
    # Verify that the given disk was found
    if (-Not $disk){
      throw "ERROR : Disk $disk_name not found on $ci_address!"
    }
    $Obj = @{}
    $Obj.free_space = $disk.FreeSpace
    $Obj.size = $disk.Size
    ConvertTo-Json -Depth 100 $Obj
    exit 0
  } else {
    exit 1
  }
} Catch {
  $errortext = $error | Out-string
  $errortext = $errortext.substring(0, $errortext.indexof("At "))
  $errortext = $errortext.substring($errortext.indexof(":") + 2, $errortext.length-$errortext.indexof(":") - 3)
  $errortext
  exit 1
}

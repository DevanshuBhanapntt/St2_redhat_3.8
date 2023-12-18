###################################################################################################################################
# Remove all files with the given extension(s) on the given disk and folder path. file_exts for this should be in the form of
# colon asterisk period extension [":*.TMP", ":opt:*.LOG"]
###################################################################################################################################
Param(
  $ci_address,
  $disk_name,
  $file_exts
)
Try {

  Write-Host "Starting DeleteFilesByExtension..."

  # Check if just the disk name was given instead of the path
  if ($disk_name.length -eq 1) {
    $disk_name += ':'
  }

  #Initialize counter variables...
  $extcount = 0
  $count = 0
  $dCount = 0
  $dSize = 0

  ForEach ($ext in $file_exts) {
    $ext.GetEnumerator() | ForEach-Object {
      $Extension = $_.Name -replace "^..*\*\.", "" #Removes all before the extension
      $max_age = $_.Value

      # Ignore all executable/script file types: .COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC;.CPL
      # Configuration and manifest file types: .INI;.CONFIG;.INF_LOC;.MUI;.INF
      # Resource Files: .OCX;.DLL;.NLS
      # Drivers: .SYS
      If ( $Extension -eq "COM" -OR $Extension -eq "EXE" -OR $Extension -eq "BAT" -OR $Extension -eq "CMD" -OR $Extension -eq "VBS" -OR $Extension -eq "VBE" -OR $Extension -eq "JS" -OR $Extension -eq "JSE" -OR $Extension -eq "WSF" -OR $Extension -eq "WSH" -OR $Extension -eq "MSC" -OR $Extension -eq "CPL" -OR $Extension -eq "INI" -OR $Extension -eq "CONFIG" -OR $Extension -eq "INF_LOC" -OR $Extension -eq "MUI" -OR $Extension -eq "INF" -OR $Extension -eq "OCX" -OR $Extension -eq "DLL" -OR $Extension -eq "NLS" -OR $Extension -eq "SYS" ) {
        Write-Output "Files with extension=$Extension not allowed to be deleted on $ci_address."
        Continue
      }
      # Removes all after the path and convert colons to backslashes for folder paths
      $delPath = $_.Name -replace "\*..*$", ""
      $delPath = $delPath -replace ":", "\"
      $dPath = '\\' + $ci_address + '\' + $disk_name.Replace(":", "$") + $delPath

      If (!(Test-Path -LiteralPath "$dPath" -PathType Container)) {
        Write-Output "Directory $dPath not found on $ci_address."
        Continue
      }
      Write-Output "Completed test-path for $dPath on $ci_address"

      $filterlist = "( Drive='$disk_name' ) AND extension='$Extension'"
      $filelist = Get-wmiobject CIM_DataFile -ComputerName $ci_address -filter "( $filterlist )"
      foreach ($f in $filelist){
        $limit_date = (Get-Date).AddDays(-$max_age)
        $file_date = ([WMI] '').ConvertToDateTime($f.LastModified)
        if ($file_date -le $limit_date) {
          $count += 1
          $filename = $f.name.Substring(2, $f.name.length-2)
          $driveletter = $f.name.Substring(0, 1)
          $filename = '\\' + ${ci_address} + '\' + $driveletter + "$" + $filename
          $filesize = [math]::ceiling($f.filesize / 1024)
          Remove-Item -Path $filename -ErrorVariable errortext -ErrorAction SilentlyContinue
          if ($errortext){
            Write-Host $errortext
            $errortext = $errortext.errordetails.message
            "ERROR : $errortext"
          }
          else{
            Write-Output "Deleted: $filename Size: $filesize"
            $dCount += 1
            $dSize += $filesize
          } # if
        }
      } # foreach

    } # ForEach file_exts
  }

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

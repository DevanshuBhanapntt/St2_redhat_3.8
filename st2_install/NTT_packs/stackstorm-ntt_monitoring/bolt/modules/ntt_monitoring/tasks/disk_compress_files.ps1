###################################################################################################################################
# Uses WMI to connect to a remote server and search for files to compress based on supplied criteria.
# Example extensions: (assuming $disk_name="C")
#   :*.txt      - results in searching "c:\" recursively for files with extension "txt"
#   :temp:*.old - results in searching "c:\temp" recursively for files with extension "old"
###################################################################################################################################
Param(
  [String] $ci_address,
  [String] $disk_name,
  [Int]    $file_age_days,
  [Array]  $file_extensions,
  [Int]    $file_min_size_mb
)
Try {
  $extensions = $file_extensions -replace(':', '\')
  $extensions = $extensions.split("|")

  # Setup calculations and substitutions for WMI queries
  $modifieddays = (get-date).adddays($file_age_days * -1)
  $minfilesize = $file_min_size_mb * 1024 * 1024

  # some WMI object is needed to convert time formats, this local one will do
  $wmiobject = Get-WmiObject -Class Win32_OperatingSystem
  $testdate = $wmiobject.ConvertFromDateTime($modifieddays)

  # output standard header
  $Process_ID = (Get-Process -Id $PID).Id
  Write-Output "Process ID: $Process_ID"
  $CurrentUser = $(whoami)
  Write-Host "current user: $CurrentUser"
  $CheckHost=$env:COMPUTERNAME
  $CheckHostIP = [System.Net.Dns]::GetHostAddresses($CheckHost) | ?{$_.scopeid -eq $null} | %{$_.ipaddresstostring}
  Write-Output "Script executed at automation server Name : $CheckHost"
  $CheckHostIP = $CheckHostIP.split(" ")
  if ($CheckHostIP.length -gt 0 )
  {
      $CheckHostIP = $CheckHostIP[0].Trim() 
  }
  else
  {
      $CheckHostIP = ""
  }
  Write-Output "Script executed at automation server IP : $CheckHostIP"

  # Getting the Process ID & Print
  "IP Address: $ci_address"
  "Drive: $disk_name" + ":"
  "Function: Compress Files Using NTFS"
  if (!($extensions)) 
  {
   Write-Output "No extensions passed to script.  Exiting."
   break
  }
  else { "Extensions: " + $extensions }

  $compresscount = 0
  $compresserror = 0
  # main processing loop
  ForEach ($e in $extensions) 
  {
    $Extension = $e -replace "^..*\*\.", "" # Removes all before the extension
    # Exclduing File types from compression
    # Probably all executable/script file types: .COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC;.CPL
    # Configuration and manifest file types: .INI;.CONFIG;.INF_LOC;.MUI;.INF
    # Resource Files: .OCX;.DLL;.NLS
    # Drivers: .SYS
    If ( $Extension -eq "COM" -OR $Extension -eq "EXE" -OR $Extension -eq "BAT" -OR $Extension -eq "CMD" -OR $Extension -eq "VBS" -OR $Extension -eq "VBE" -OR $Extension -eq "JS" -OR $Extension -eq "JSE" -OR $Extension -eq "WSF" -OR $Extension -eq "WSH" -OR $Extension -eq "MSC" -OR $Extension -eq "CPL" -OR $Extension -eq "INI" -OR $Extension -eq "CONFIG" -OR $Extension -eq "INF_LOC" -OR $Extension -eq "MUI" -OR $Extension -eq "INF" -OR $Extension -eq "OCX" -OR $Extension -eq "DLL" -OR $Extension -eq "NLS" -OR $Extension -eq "SYS" ) 
    {
      " "
      Write-Output "Files with extension=$Extension not allowed to be compressed on $ci_address."
      Continue
    }
    # Removes all after the path
    $extcomppath = $e -replace "\*..*$", ""
    $extcomppath=$extcomppath
    $comppath = '\\' + $ci_address + '\' + $disk_name + "$" + $extcomppath
    If ($extcomppath.length -gt 1) { $searchpath = $disk_name + ":" + $extcomppath }

    If (!(Test-Path -LiteralPath "$comppath" -PathType Container)) 
    {
      Write-Output "Directory $comppath not found on $ci_address."
      Continue
    }

    $filter = "Drive='$disk_name" + ":' AND extension='$extension' and Compressed='False' and FileSize > $minfilesize and LastModified < '$testdate'"
    if ($extcomppath.length -gt 1)
    {
      $searchpath = $searchpath.replace("\", "\\")
      $filter = $filter + " and Name LIKE '$searchpath" + "%'"
    }
    $extcount += 1
    " "
    "Searching for files on $ci_address meeting the following criteria for compression (filesize is in bytes):"
    $displayfilter = $filter.replace(">", "greater than")
    $displayfilter = $displayfilter.replace("<", "less than")
    "  $displayfilter"
    " "

    $filelist = Get-wmiobject CIM_DataFile -ComputerName $ci_address -filter $filter

    if ($filelist.count) 
    {
      "Found $($filelist.count) files meeting the compression criteria"
      $compressflag = 0
    }
    elseif ($filelist) 
    {
      "Found 1 file meeting the compression criteria"
      $compressflag = 0
    }
    else 
    {
      "Found 0 files meeting the compression criteria"
      $compressflag = 1
    }

    Write-Host $filelist

    if ($compressflag -eq 0)
    {
      "Compressing file(s) not modified since $modifieddays.\n"

      foreach ($f in $filelist)
      {
        " Compressing : $($f.Name)" 
        $FileFullName = $f.Name.Replace("\", "\\")
        $compressfile = Get-wmiobject CIM_DataFile -ComputerName $ci_address -filter "Name='$FileFullName'"
        $compressfile = $compressfile.Compress()

        if ($compressfile.ReturnValue -eq 0) { $compresscount += 1 }
        else { $compresserror += 1 }

        switch ($compressfile.ReturnValue)
        { 
          0 {"  Result: Success"}
          2 {"  Result: Access Denied"}
          8 {"  Result: Unspecified Failure"}
          9 {"  Result: Invalid Object"}
          10 {"  Result: Object Already Exists"}
          11 {"  Result: File system not NTFS"}
          12 {"  Result: Platform not Windows"}
          13 {"  Result: Drive not the same"}
          14 {"  Result: Directory not Empty"}
          15 {"  Result: Sharing violation"}
          16 {"  Result: Invalid start file"}
          17 {"  Result: Privilege not held"}
          21 {"  Result: Invalid parameter"}
        } # switch
      } # foreach ($f in $filelist)
    } # if ($compressflag -eq 0)
  } # ForEach ($e in $extensions)
  "  "
  "Files Compressed: $compresscount"
  "Compression issues: $compresserror"

  exit 0

} Catch {
  $errortext = $error | Out-string
  $errortext = $errortext.substring(0, $errortext.indexof("At "))
  $errortext = $errortext.substring($errortext.indexof(":") + 2, $errortext.length - $errortext.indexof(":") - 3)
  $errortext
  exit 1
}

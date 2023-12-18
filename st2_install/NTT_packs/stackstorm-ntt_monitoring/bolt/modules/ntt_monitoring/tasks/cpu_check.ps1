# Check whether the given CPU on a VM is above the threshold
Param(
  [String]$cpu_name,
  [String]$cpu_type,
  [String]$dns_domain,
  [String]$threshold_percent,
  [Int]$top_process_limit
)

function get-UserTime($ServerName,$CPUName) {
  #Determine CPU User Time Usage
  $Samples=get-counter -counter "\Processor($CPUName)\% User Time" -ErrorVariable errortext -ErrorAction SilentlyContinue
  if ($?)
  {
    # There should only be one sample returned but it gets returned in a array
    $samplecount=0
    $totalusage=0
    foreach ($S in $Samples)
    {
      $samplecount=$samplecount+1
      $usage=[double]$S.Readings.substring($S.Readings.IndexOf(":")+2,$S.Readings.Length-$S.Readings.IndexOf(":")-2)
      $totalusage=$totalusage+$usage
    } #foreach
    $totalaverage=$totalusage/$samplecount
    write-output "CPU User Time% : $totalaverage"
    "(\Processor($CPUName)\% User time)`n"
  }
}

function get-QueueLength($ServerName,$CPUName) {
  #Determine Average Queue Length
  $Samples=get-counter -counter "\System\Processor Queue Length" -ErrorVariable errortext -ErrorAction SilentlyContinue
  if ($?)
  {
    # There should only be one sample returned but it gets returned in a array
    $samplecount=0
    $totalusage=0
    foreach ($S in $Samples)
    {
      $samplecount=$samplecount+1
      $usage=[double]$S.Readings.substring($S.Readings.IndexOf(":")+2,$S.Readings.Length-$S.Readings.IndexOf(":")-2)
      $totalusage=$totalusage+$usage
    } #foreach
    $totalaverage=$totalusage/$samplecount
    write-output "\System\Processor Queue Length% : $totalaverage"
    "(\System\Processor Queue Length)`n"
  }
}

#Function gets the app pool information for IIS for a specific process ID from a remote computer
#$name is the name of the app pool to be returned, to return any App Pool name supply *
#based on code from http://odetocode.com/Blogs/scott/archive/2006/07/18/powershell-and-apppool-names.aspx
function get-w3wp([string]$Servername,$ID,[string]$name)
  {
    $list = get-process -Id $ID -ComputerName $ServerName -erroraction silentlycontinue
    if($list)
    {
      foreach($p in $list)
      {
        ### Forcibly suppress errors from process lookups, will fail if a process terminates during lookups
        $ErrorActionPreference = 'SilentlyContinue'
        $filter = "Handle='" + $p.Id + "'"
        $wmip = get-WmiObject Win32_Process -ComputerName $ServerName -filter $filter
        if($wmip.CommandLine -match "-ap `"(.+)`"")
        {
          $appName=$matches[1].Substring(0,$matches[1].IndexOf('"'))
          $p | add-member NoteProperty AppPoolName $appName
        } #if
        $ErrorActionPreference = 'Continue'
        ### Return to normal error handling
      } #foreach
      $list | where { $_.AppPoolName -like $name }
    } #if($list)
  } #function get-w3wp

  $hostname = hostname

  if ($dns_domain)
  {
    $Servername = $hostname + '.' + $dns_domain
  }
  else
  {
    $Servername = $hostname
  }

  $CheckHost = $env:COMPUTERNAME
  $CheckHostIP = [System.Net.Dns]::GetHostAddresses($hostname)|?{$_.scopeid -eq $null}|%{$_.ipaddresstostring}
  $error.clear()

#main process starts here
try
{
  $svchostIDs=""
  $IISIDs=""

  #Determine Average CPU Usage
  $Samples=get-counter -counter "\Processor($cpu_name)\% processor time" -ErrorVariable errortext -ErrorAction SilentlyContinue
  if ($?)
  {
    # There should only be one sample returned but it gets returned in a array
    $samplecount=0
    $totalusage=0
    foreach ($S in $Samples)
    {
      $samplecount=$samplecount+1
      $usage=[double]$S.Readings.substring($S.Readings.IndexOf(":")+2,$S.Readings.Length-$S.Readings.IndexOf(":")-2)
      $totalusage=$totalusage+$usage
    } #foreach
    $totalaverage=$totalusage/$samplecount
    write-output "CPU% Utilization : $totalaverage% Threshold : $threshold_percent%"
    "(\Processor($cpu_name)\% processor time)`n"

    if ($cpu_type -match "ProcessorTotalUserTime")
    {
      get-UserTime $ServerName $cpu_name
    }
    elseif ($cpu_type -match "ProcessorQueueLength")
    {
      get-QueueLength $ServerName $cpu_name
    }

    #Attempt to collect additional system information, verifies wmi access
    $numberofprocessor=(Get-WmiObject Win32_Processor -computername $ServerName -ErrorVariable badwmi -ErrorAction SilentlyContinue| select-object -Property "NumberOfLogicalProcessors" | measure-object NumberOfLogicalProcessors -sum).sum

    #bypass additional diagnostic data collection if there are WMI issues
    if($badwmi)
    {
      "SNAPSHOTSTART`n"
      "No additional diagnostic data could be collected due to issues with Windows Management Instrumentation on $servername`n"
      $badwmi=$badwmi|Out-String
      $badwmi=$badwmi.substring(0,$badwmi.indexof("At "))
      $badwmi=$badwmi.substring($badwmi.indexof(":")+2,$badwmi.length-$badwmi.indexof(":")-3)
      "Issue : $badwmi"
      "`nSNAPSHOTEND`n"
    } #if
    else
    #collect additional diagnostic data if WMI works
    {
      $CpuInfo = Get-WmiObject Win32_PerfFormattedData_PerfOS_Processor -ComputerName $ServerName -ErrorAction SilentlyContinue
      #better method of determining number of CPUs
      $numberofprocessor=$CpuInfo.count-1
      $MemInfo = Get-WmiObject Win32_PerfFormattedData_PerfOS_Memory -ComputerName $ServerName -ErrorAction SilentlyContinue
      $lastboot= Get-WmiObject -Query "SELECT LastBootUpTime FROM Win32_OperatingSystem" -ComputerName $ServerName -ErrorAction SilentlyContinue

      "SNAPSHOTSTART`n"
      "Quick system resource snapshot"
      "------------------------------"
      "Last Boot Time  ($ServerName Timezone) : $($lastboot.ConvertToDateTime($lastboot.LastBootUpTime))"
      "Total Memory             (MB) : $(Get-WmiObject Win32_ComputerSystem -ComputerName $ServerName -ErrorAction SilentlyContinue| foreach {[math]::round($_.TotalPhysicalMemory/(1024*1024),0)})"
      "Available Memory         (MB) : $([math]::round($MemInfo.AvailableMBytes,0))"
      "Committed Memory         (MB) : $([math]::round($MemInfo.CommittedBytes/(1024*1024),0))"
      "Cache Memory             (MB) : $([math]::round($MemInfo.CacheBytes/(1024*1024),0))"
      "Logical Processors            : $numberofprocessor"
      "PercentIdleTime       (CPU:%) : $($CpuInfo | foreach {"CPU"+$_.__RELPATH.substring(47,$_.__RELPATH.length-48)+":"+[string]$_.PercentIdleTime+"%"})"
      "PercentProcessorTime  (CPU:%) : $($CpuInfo | foreach {"CPU"+$_.__RELPATH.substring(47,$_.__RELPATH.length-48)+":"+[string]$_.PercentProcessorTime+"%"})"
      "PercentInterruptTime  (CPU:%) : $($CpuInfo | foreach {"CPU"+$_.__RELPATH.substring(47,$_.__RELPATH.length-48)+":"+[string]$_.PercentPrivilegedTime+"%"})"
      "PercentPrivilegedTime (CPU:%) : $($CpuInfo | foreach {"CPU"+$_.__RELPATH.substring(47,$_.__RELPATH.length-48)+":"+[string]$_.PercentPrivilegedTime+"%"})"
      "PercentUserTime       (CPU:%) : $($CpuInfo | foreach {"CPU"+$_.__RELPATH.substring(47,$_.__RELPATH.length-48)+":"+[string]$_.PercentUserTime+"%"})"
      "PercentSystemTime     (CPU:%) : $($CpuInfo | foreach {"CPU"+$_.__RELPATH.substring(47,$_.__RELPATH.length-48)+":"+[string]$_.PercentSystemTime+"%"})"
      "`nSNAPSHOTEND`n"

      #Gather information on the processes with the highest CPU utilization
      $proc=Get-counter "\Process(*)\% processor time" -ErrorAction SilentlyContinue -ErrorVariable countererror
      #System was being excluded here, System is ntoskrnl.exe, this was exluded in AO but not IPSoft version, added status to avoid pulling incompelte data, status!=0 typically means a terminated process still in the process list
      $procresult = $Proc.CounterSamples | where {$_.instanceName -ne "idle" -and $_.instanceName -ne "_total" -and $_.status -eq 0 -and $_.cookedvalue -gt 0}| sort-object -property cookedvalue -descending | select -First $top_process_limit # -and $_.instanceName -ne "system"
      $pList = New-Object 'object[,]' $procresult.length,4
      $count=0
      foreach ($f in $procresult)
      {
        $count=$count+1
        $ProcessName = $f.Path
        $percentProc = $f.cookedvalue
        $ProcessName = $ProcessName.Substring($ProcessName.IndexOf('(') +1)
        $ProcessName = $ProcessName.Substring(0,$ProcessName.IndexOf(')'))
        $ProcessCPUUsage=[math]::round($percentProc/$numberofprocessor)
        #list highest usage process separately
        if ($count -eq 1)
        {
          "Highest Usage Process : $ProcessName"
          "Highest Process CPU%  : $ProcessCPUUsage"
          "`n"
        } #if
        ### Forcibly suppress errors from process lookups, will fail if a process terminates during lookups
        $ErrorActionPreference = 'SilentlyContinue'
        $id = Get-Counter "\Process($ProcessName)\ID Process" -ErrorAction SilentlyContinue
        $idr = $id.CounterSamples |where {$_.cookedvalue -ne $null}
        $id = $idr.cookedvalue
        $process1 = gwmi win32_process -ComputerName $ServerName -filter "ProcessID = '$($idr.cookedvalue)'"
        $owner = $process1.GetOwner()
        $uName = $owner.domain + "\" + $owner.user
        if ($ProcessName -match "svchost"){$svchostIDs=$svchostIDs+","+$id}
        elseif ($ProcessName -match "w3wp"){$IISIDs=$IISIDs+","+$id}
        $object = new-object PSObject -Property @{
          'ProcessName' = $ProcessName
          'CPU_Usage_%' = $ProcessCPUUsage
          'ProcessID' = $id
          'Domain\Username' = $uName
        }
        $pList += $object
        $ErrorActionPreference = 'Continue'
        ### Return to normal error handling
      } #foreach

      "PROCESSDATASTART`n"
      if ($pList.Length -gt 0) {
        write-output "The $top_process_limit processes with the highest CPU usage on $ServerName are below"
        $pList | format-table -auto
      }
      else {
        write-output "The $top_process_limit processes list is empty due to inactivity at the moment"
      }
      "PROCESSDATAEND`n"

      #list services running as children for any svchost processes in the top usage list
      if ($svchostIDs.Length -gt 0)
      {
        "SVCDATASTART`n"
        "Service Host Processes in top $top_process_limit entries of CPU utilization list`n"
        $svchostIDs=$svchostIDs.TrimStart(",")
        $ProcessIDs=$svchostIDs.split(",")
        $count=0
        foreach($P in $ProcessIDs)
        {
          $count=$count+1
          "  Svchost count : $count"
          "  ProcessId($count) : " + $P
          ### Forcibly suppress errors from service lookups, will fail if a process terminates during lookups
          $ErrorActionPreference = 'SilentlyContinue'
          $data=gwmi win32_service -ComputerName $ServerName| where {$_.ProcessId -eq $P} | Group ProcessId
          $namelist=""
          foreach ($d in $data.group){$namelist=$namelist+","+$d.name}
          $namelist=$namelist.TrimStart(",")
          "  Services($count) : " + $namelist + "`n"
          $ErrorActionPreference = 'Continue'
          ### Return to normal error handling
        } #foreach
        "`nSVCDATAEND`n"
      } #if

      #list web app pools for IIS for any w3wp processes in the top usage list
      if ($IISIDs.Length -gt 0)
      {
        "W3WPDATASTART`n"
        "IIS App Pool Processes in top $top_process_limit entries of CPU utilization list`n"
        $IISIDs=$IISIDs.TrimStart(",")
        $ProcessIDs=$IISIDs.split(",")
        $count=0
        foreach($P in $ProcessIDs){
          $count=$count+1
          $IISprocesses=get-w3wp $ServerName $P *
          if ($IISprocesses)
          {
            $IISprocesses| foreach{
              "  w3wp count : $count"
              "  w3wp ID($count) : "+$_.Id
              "  AppPoolName($count) : "+$_.AppPoolName+"`n"
            } #foreach
          } #if
        } #foreach
        "`nW3WPDATAEND`n"
      } #if ($IISIDs.Length -gt 0)

      #If performance counters were returned with an invalid status, list them
      #Informational only does not affect processing, this happens for recently terminated processes
      #This aborted the previous version of the testing script
      if ($countererror)
      {
        "`nISSUEDATASTART`n"
        $errortext=$countererror.errordetails.message
        "Non-Critical ISSUE : $errortext"
        "Invalid counter status returned for the following"
        $invalidproc = $Proc.CounterSamples | where {$_.status -ne 0}| sort-object -property cookedvalue -descending
        $invalidproc
        "`nISSUEDATAEND`n"
      } #if

    } #else
    exit 0
  } #if ($?)
  else {
    throw "ERROR : No information found for CPU: $cpu_name!"
  }
  exit 0
} #try
catch
{
  #There is an issue with the WMI service on the LAP
  $errortext=$error|Out-string
  "Issue with Windows Management Instrumentation on $CheckHost"
  $errortext=$errortext.substring(0,$errortext.indexof("At "))
  $errortext=$errortext.substring($errortext.indexof(":")+2,$errortext.length-$errortext.indexof(":")-3)
  "ERROR : $errortext"
  exit 1
} #catch

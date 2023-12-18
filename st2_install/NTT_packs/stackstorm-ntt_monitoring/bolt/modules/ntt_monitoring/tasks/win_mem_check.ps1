Param(   
  [String]$dns_domain 
)

#This script gathers information relevant to diagnosing high memory usage
#  1. Verifies the server pings, or reports probable cause of ping failure
#  2. Reports top 10 processes with the highest memory usage
#  3. Reports Physical Memory Information
#  4. Reports Virtual Memory Information
#  5. Reports Page File information
#  6. Reports Pages per second
#  7. Reports general information on boot time, memory utilization, and per CPU utilization

$TopMemoryList=10
if ($MaxSamples -eq $null)
  {$MaxSamples=30}
if ($SampleInterval -eq $null)
  {$SampleInterval=2}
  
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
 "CHECKDETAILSSTART`n"
 "Server performing checks (IP) : $CheckHost ($CheckHostIP)"
 $result = Get-WmiObject -Query "SELECT * FROM Win32_PingStatus WHERE Address = '$ServerName'" -ErrorAction Stop
 $hostinfo = Get-WmiObject -Query "SELECT * FROM Win32_PingStatus WHERE Address = '$ServerName'" -ErrorAction Stop
 #evaluate ping response
 if ($result.statuscode -eq 0){
  #server pinged successfully
  Try {
   If ($result.IPV4Address.Address){$IP=$result.IPV4Address}
   else{$IP=$result.IPV6Address}
   write-output "Server name being checked : $ServerName"
   write-output "Pingable : true"
   write-output "Pinged IP : $IP"
   "`nCHECKDETAILSEND`n"
   $svchostIDs=""
   $IISIDs=""

   "MEMSTART`n"
   write-output "The $TopMemoryList processes with the highest Memory usage on $ServerName are below"
   #$ResultTesting=Get-WmiObject -Class win32_process -ComputerName $ServerName -ErrorVariable errortext -ErrorAction SilentlyContinue | sort WS -desc | select @{Label="Process ID";Expression={[int]($_.ProcessId)}},Name,@{Label="Memory(M)";Expression={[int]($_.WS/1048576)}},@{n="Owner";e={$_.getowner().user}},@{n="Domain";e={$_.getowner().domain}} | select -first $TopMemoryList #| ft -auto
   $ResultTesting=Get-WmiObject -Class win32_process -ErrorVariable errortext -ErrorAction SilentlyContinue | sort WS -desc | select @{Label="Process ID";Expression={[int]($_.ProcessId)}},Name,@{Label="Memory(M)";Expression={[int]($_.WS/1048576)}},@{n="Owner";e={$_.getowner().user}},@{n="Domain";e={$_.getowner().domain}} | select -first $TopMemoryList #| ft -auto
   if (($ResultTesting) -and (-not( $ResultTesting -match ".*Get-W.*" )) -and (-not($ResultTesting -match ".*RPC.*" )))
   {
     $ResultTesting | format-table -auto
     #Write the single highest usage process to be used by ARC
     "`nHighest Usage Process :"
     $ResultTesting |  select-object -first 1 |format-table -auto
     $os = Get-WmiObject win32_OperatingSystem -ErrorAction SilentlyContinue	 
	 #$os = Get-WmiObject win32_OperatingSystem -ComputerName $ServerName -ErrorAction SilentlyContinue
     if ($?)
     {
       "`nPHYSICALMEMORYSTART"
       $TotalMemory = $([math]::round($os.TotalVisibleMemorySize/(1024*1024),3))
       $FreePhysMemory = $([math]::round($os.FreePhysicalMemory / (1024*1024),3))
       $UsedPhysMemory = $([math]::round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory)/(1024*1024),3))
       $PctFree = (($os.FreePhysicalMemory) / $os.TotalVisibleMemorySize).ToString("P")
       $PctUsed = (($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / $os.TotalVisibleMemorySize).ToString("P")
       write-output "Physical Memory Total : $TotalMemory (GB)"
       write-output "Physical Memory Used : $UsedPhysMemory (GB)"
       write-output "Physical Memory Free : $FreePhysMemory (GB)"
       write-output "Physical Memory Pct Free : $PctFree"
       write-Output "Physical Memory Usage : $PctUsed"
       "PHYSICALMEMORYEND"
       #
       "`nVIRTUALMEMORYSTART"
       $TotVirtMemory = $([math]::round($os.TotalVirtualMemorySize / (1024*1024),3))
       $FreeVirtMemory =$([math]::round($os.FreeVirtualMemory / (1024*1024),3))
       $UsedVirtMemory = $([math]::round(($os.TotalVirtualMemorySize - $os.FreeVirtualMemory)/(1024*1024),3))
       $PctVirtMemFree = (($os.FreeVirtualMemory) / $os.TotalVirtualMemorySize).ToString("P")
       $PctVirtMemUsed = (($os.TotalVirtualMemorySize - $os.FreeVirtualMemory) / $os.TotalVirtualMemorySize).ToString("P")
       write-output "Virtual Memory Total: $TotVirtMemory (GB)"
       write-output "Virtual Memory Used : $UsedVirtMemory (GB)"
       write-output "Virtual Memory Free : $FreeVirtMemory (GB)"
       write-output "Virtual Memory Pct Free: $PctVirtMemFree"
       write-output "Virtual Memory Usage : $PctVirtMemUsed"
       write-output "VIRTUALMEMORYEND"
       #
       "`nPAGINGFILESTART"
       #$PagingFileMemory = (Get-WmiObject Win32_PageFileusage -computername $ServerName)
	   $PagingFileMemory = (Get-WmiObject Win32_PageFileusage)
       $PagingFile = ($PagingFileMemory.Name)
       $PagingFileStatus = ($PagingFileMemory.Status)
       $PagingFilesize = ($PagingFileMemory.AllocatedBaseSize | Measure-Object -sum |   % { $_.sum })
       $PagingFilePeak = ($PagingFileMemory.PeakUsage | Measure-Object -sum |   % { $_.sum })
       $PagingFileUsage = ($PagingFileMemory.CurrentUsage | Measure-Object -sum |   % { $_.sum })
       $PagingFileFree = $AllocatedBaseSize - $CurrentUsage
       $PagingFilePercentFree = (($PagingFilesize-$PagingFileUsage)/$PagingFilesize).ToString("P")
       $PagingFilePercentUsed = ($PagingFileUsage/$PagingFilesize).ToString("P")
       write-output "PagingFile : $PagingFile"
       #write-output "PagingFileStatus : $PagingFileStatus"
       write-output "PagingFilesize : $PagingFilesize"
       write-output "PagingFilePeak : $PagingFilePeak"
       write-output "PagingFileFree : $PagingFileFree"
       write-output "PagingFileUsage : $PagingFileUsage"
       write-output "PagingFilePercentFree : $PagingFilePercentFree"
       write-output "PagingFilePercentUsed : $PagingFilePercentUsed"
       write-output "PAGINGFILEEND"
       #
       write-output "`nPAGESPERSECSTART"
       $Samples=""
       $Samples=Get-Counter -Counter "\Memory\Pages/sec" -sampleinterval $SampleInterval -MaxSamples $MaxSamples -ErrorVariable errortext -ErrorAction SilentlyContinue
       $samplecount=0
       $totalusage=0
       foreach ($S in $Samples)
       {
         $samplecount=$samplecount+1
         $usage=[double]$S.Readings.substring($S.Readings.IndexOf(":")+2,$S.Readings.Length-$S.Readings.IndexOf(":")-2)
         #write-output "usage=$usage"
         $totalusage=$totalusage+$usage
       } #foreach       
	   if ($samplecount -gt 0 )
	   {	   
		 $totalaverage=$totalusage/$samplecount
	   }
	   else
	   {
		   $totalaverage=0
	   }
       write-output "Average pages per second : $totalaverage"
       #$Samples | Format-Table -AutoSize
       $Samples | where {$_.cookedvalue -gt 0} |Format-Table -AutoSize
       "PAGESPERSECEND"
       write-output "`nCOMMITTEDBYTESINUSESTART"
       $Samples=""
       $Samples=Get-Counter -Counter "\Memory\% Committed Bytes in Use" -sampleinterval $SampleInterval -MaxSamples $MaxSamples -ErrorVariable errortext -ErrorAction SilentlyContinue
       $samplecount=0
       $totalusage=0
       foreach ($S in $Samples)
       {
         $samplecount=$samplecount+1
         $usage=[double]$S.Readings.substring($S.Readings.IndexOf(":")+2,$S.Readings.Length-$S.Readings.IndexOf(":")-2)
         #write-output "usage=$usage"
         $totalusage=$totalusage+$usage
       } #foreach
	   if ($samplecount -gt 0 )
	   {	   
		 $totalaverage=$totalusage/$samplecount
	   }
	   else
	   {
		   $totalaverage=0
	   }
       write-output "Average % Committed Bytes in Use : $totalaverage"
       #$Samples | Format-Table -AutoSize
       "COMMITTEDBYTESINUSEEND"

       "MEMEND"
       #Attempt to collect additional system information, verifies wmi access
       $numberofprocessor=(Get-WmiObject Win32_Processor -ErrorVariable badwmi -ErrorAction SilentlyContinue| select-object -Property "NumberOfLogicalProcessors" | measure-object NumberOfLogicalProcessors -sum).sum
       #$numberofprocessor=(Get-WmiObject Win32_Processor -computername $ServerName -ErrorVariable badwmi -ErrorAction SilentlyContinue| select-object -Property "NumberOfLogicalProcessors" | measure-object NumberOfLogicalProcessors -sum).sum
       #bypass additional diagnostic data collection if there are WMI issues
       if($badwmi)
       {
        "`nSNAPSHOTSTART`n"
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
        $CpuInfo = Get-WmiObject Win32_PerfFormattedData_PerfOS_Processor -ErrorAction SilentlyContinue
		#$CpuInfo = Get-WmiObject Win32_PerfFormattedData_PerfOS_Processor -ComputerName $ServerName -ErrorAction SilentlyContinue
        #better method of determining number of CPUs
        $numberofprocessor=$CpuInfo.count-1
        $MemInfo = Get-WmiObject Win32_PerfFormattedData_PerfOS_Memory -ErrorAction SilentlyContinue
		#$MemInfo = Get-WmiObject Win32_PerfFormattedData_PerfOS_Memory -ComputerName $ServerName -ErrorAction SilentlyContinue
        $lastboot= Get-WmiObject -Query "SELECT LastBootUpTime FROM Win32_OperatingSystem" -ErrorAction SilentlyContinue
		#$lastboot= Get-WmiObject -Query "SELECT LastBootUpTime FROM Win32_OperatingSystem" -ComputerName $ServerName -ErrorAction SilentlyContinue
        "SNAPSHOTSTART`n"
        "Quick system resource snapshot"
        "------------------------------"
        "Last Boot Time  ($ServerName Timezone) : $($lastboot.ConvertToDateTime($lastboot.LastBootUpTime))"
        #"Total Memory             (MB) : $(Get-WmiObject Win32_ComputerSystem -ComputerName $ServerName -ErrorAction SilentlyContinue| foreach {[math]::round($_.TotalPhysicalMemory/(1024*1024),0)})"
		"Total Memory             (MB) : $(Get-WmiObject Win32_ComputerSystem -ErrorAction SilentlyContinue| foreach {[math]::round($_.TotalPhysicalMemory/(1024*1024),0)})"
        "Available Memory         (MB) : $([math]::round($MemInfo.AvailableMBytes,0))"
        "Committed Memory         (MB) : $([math]::round($MemInfo.CommittedBytes/(1024*1024),0))"
        "Committed Memory      (Bytes) : $([math]::round($MemInfo.CommittedBytes,0))"
        "Commit Limit             (MB) : $([math]::round($MemInfo.CommitLimit/(1024*1024),0))"
        "Cache Memory             (MB) : $([math]::round($MemInfo.CacheBytes/(1024*1024),0))"
        "Free page table entries  (MB) : $([math]::round($MemInfo.freesystempagetableentries/(1024*1024),0))"
        "Pool Paged Resident      (MB) : $([math]::round($MemInfo.poolpagedresidentbytes/(1024*1024),0))"
        "Logical Processors            : $numberofprocessor"
        "PercentIdleTime       (CPU:%) : $($CpuInfo | foreach {"CPU"+$_.__RELPATH.substring(47,$_.__RELPATH.length-48)+":"+[string]$_.PercentIdleTime+"%  "})"
        "PercentProcessorTime  (CPU:%) : $($CpuInfo | foreach {"CPU"+$_.__RELPATH.substring(47,$_.__RELPATH.length-48)+":"+[string]$_.PercentProcessorTime+"%  "})"
        "PercentInterruptTime  (CPU:%) : $($CpuInfo | foreach {"CPU"+$_.__RELPATH.substring(47,$_.__RELPATH.length-48)+":"+[string]$_.PercentPrivilegedTime+"%  "})"
        "PercentPrivilegedTime (CPU:%) : $($CpuInfo | foreach {"CPU"+$_.__RELPATH.substring(47,$_.__RELPATH.length-48)+":"+[string]$_.PercentPrivilegedTime+"%  "})"
        "PercentUserTime       (CPU:%) : $($CpuInfo | foreach {"CPU"+$_.__RELPATH.substring(47,$_.__RELPATH.length-48)+":"+[string]$_.PercentUserTime+"%  "})"
        "`nSNAPSHOTEND`n"

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
      #An error was returned for a query with graceful error handling in place
     else{
      $errortext=$errortext|Out-String
      $errortext=$errortext.substring(0,$errortext.indexof("At "))
      $errortext=$errortext.substring($errortext.indexof(":")+2,$errortext.length-$errortext.indexof(":")-3)
      "ERROR : $errortext"
      exit 9999
     } #else
   } #if ResultTesting
   else
   {
     "ERROR : $errortext"
     "`n$ResultTesting"
     "MEMEND`n"
   } #if ResultTesting
  } #try
  Catch
  {
   if($totalaverage)
   {
    "SNAPSHOTSTART`n"
    "An issue collecting additional diagnostic data occurred on $servername`n"
    $errortext=$error|Out-string
    $errortext=$errortext.substring(0,$errortext.indexof("At ")) #remove extraneous info, but leave command details
    "ISSUE : $errortext"
    "`nSNAPSHOTEND`n"
    exit 0
   }#if
   else
   {
    #Some other unanticpated error occurred in the PowerShell script that was not encountered during testing
    $errortext=$error|Out-string
    $errortext=$errortext.substring(0,$errortext.indexof("At ")) #remove extraneous info, but leave command details
    "ERROR : $errortext"
    write-output "MEMEND"
    exit 9999
   }#else
  } #Catch
 } #if ($result.statuscode -eq 0)
 else
 {
  #Handling and dianosis of the issue for a server that did not ping
   write-output "Server name being checked : $ServerName"
   write-output "Pingable : false"
  If ($result.IPV4Address.Address)
  {
   "Pinged IP  : "+$result.IPV4Address
   "`nCHECKDETAILSEND`n"
   "ERROR : $ServerName at $($result.IPV4Address) cannot be pinged from $CheckHost"
  } #if
  else
  {
     If ($result.IPV6Address.Address){
      "Pinged IP  : "+$result.IPV6Address
      "`nCHECKDETAILSEND`n"
      "ERROR : $ServerName at $($result.IPV6Address) cannot be pinged from $CheckHost"
     } #if
     else
     {
      "`nCHECKDETAILSEND`n"
      "ERROR : $ServerName cannot be resolved to an IP address from $CheckHost"
     } #else result.IPV6
   } #else result.IPV4
  } #else result.statuscode
} #try
catch
{
  #There is an issue with the WMI service on the LAP
  $errortext=$error|Out-string
  "Issue with Windows Management Instrumentation on $CheckHost"
  $errortext=$errortext.substring(0,$errortext.indexof("At "))
  $errortext=$errortext.substring($errortext.indexof(":")+2,$errortext.length-$errortext.indexof(":")-3)
  "ERROR : $errortext"
  "`nCHECKDETAILSEND`n"
  exit 9999
} #catch

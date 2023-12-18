param ($dns_domain,$sleepsec, $servicename)

$SleepSec = 7
$ServiceName = $servicename

$hostname = hostname
if ($dns_domain)
  {
    $Computer = $hostname + '.' + $dns_domain
  }
  else
  {
    $Computer = $hostname
  }

$ServiceNameRetrieved="${ServiceName}"

$CheckHost=$env:COMPUTERNAME
$CheckHostIP = [System.Net.Dns]::GetHostAddresses($hostname)|?{$_.scopeid -eq $null}|%{$_.ipaddresstostring}
$error.clear()
$count=0

function force-start-service($ServerName,$ServiceN)
{
  #Force start a service using Stop-Service and Start-Service
  write-output "########################### Proceeding to Terminate $ServiceN on $Computer ##########################"
  #$StopIt=Get-Service -Name $ServiceN -ComputerName $ServerName | Stop-service -Force # -Confirm  #Remove -Confirm before production

   $StopIt=(Get-WmiObject Win32_Process -ComputerName $ServerName | ?{ $_.ProcessName -match "$ServiceN" }).Terminate()
  if ($?) #if
  {
     Start-Sleep -s 10
     $SvcName2 = get-wmiobject Win32_Service -computername $ServerName -ErrorAction SilentlyContinue| where-object {($_.Name -eq $ServiceN) -or ($_.DisplayName -eq $ServiceN)}
     $Svcstartmode2=$SvcName2.StartMode
     if( $SvcName2)  #if $SvcName2
     {
        if ($SvcName2.state -eq "Stopped" )
        {
           write-output "########################### $ServiceN Stopped Path=$SvcName2 ##########################"
           write-output "########################### Proceeding to Start-Service on $ServiceN ##########################"
           #Get-Service -Name $ServiceN -ComputerName $ServerName | Start-service
           $StartIt=$SvcName2.StartService()
           if ($?)
           {
             Start-Sleep -s 10
             $SvcName3 = get-wmiobject Win32_Service -computername $ServerName -ErrorAction SilentlyContinue| where-object {($_.Name -eq $ServiceN) -or ($_.DisplayName -eq $ServiceN)}
             $Svcstartmode3=$SvcName3.StartMode
             if( $SvcName3)  #if $SvcName3
             {
                $SvcName3State=$SvcName3.state
                if ($SvcName3.state -eq "Running" -and $Svcstartmode3 -ne "Disabled")
                {
                      Write-output "Service state : successfully_started on server $Computer"
                }
                else
                {
                     Write-output "Service state : fail_to_start on server $Computer"
                } #if $SvcName3.state
             } #if $SvcName3
         } #if $?
        }
        else
        {
        write-output "########################### $ServiceN NotStopped State=$SvcName2State ##########################"
        } #if $SvcName2.state
     } #if $SvcName2

  } #if $?
}


write-output "CHECKDETAILSSTART"
write-output ""
write-output "Server performing checks (IP) : $CheckHost ($CheckHostIP)"

$result = Get-WmiObject -Query "SELECT * FROM Win32_PingStatus WHERE Address = '$Computer'" -ErrorAction Stop
if ($result.statuscode -eq 0)
{
  If ($result.IPV4Address.Address){$IP=$result.IPV4Address}
  else{$IP=$result.IPV6Address} #If-else
  write-output "Server name being checked : $Computer"
  write-output "Pingable : true"
  write-output "Pinged IP : $IP"
  write-output "$Computer is pingable from $CheckHost"
  write-output "Service being checked : $ServiceName"
  write-output ""
  write-output "CHECKDETAILSEND"

  Try {
    $SvcName = get-wmiobject Win32_Service -computername $Computer -ErrorVariable badwmi -ErrorAction SilentlyContinue| where-object {($_.Name -eq $ServiceNameRetrieved) -or ($_.DisplayName -eq $ServiceNameRetrieved)}
        if($badwmi)
        {
            $badwmi=$badwmi|Out-String
            $badwmi=$badwmi.substring(0,$badwmi.indexof("At "))
            $badwmi=$badwmi.substring($badwmi.indexof(":")+2,$badwmi.length-$badwmi.indexof(":")-3)
            "Issue : $badwmi"
        }
        else {
        if ($?) {
        write-output ""
        write-output "SERVICE RESTART SCRIPT BEGIN"
        $SvcName = get-wmiobject Win32_Service -computername $Computer -ErrorAction SilentlyContinue| where-object {($_.Name -eq $ServiceNameRetrieved) -or ($_.DisplayName -eq $ServiceNameRetrieved)}
        $ServiceName = $SvcName.Name
        $Svcstartmode=$SvcName.StartMode
        $SvcDisplayName=$SvcName.DisplayName
        $SvcStartName=$SvcName.StartName
        #Name, DisplayName, State, StartMode, StartName
        if( $SvcName) {
                if ($SvcName.state -ne "Running" -and $Svcstartmode -ne "Disabled")
                {
                   $depends = Get-Service -computername $Computer | Where-Object { $_.name -eq $ServiceName} |
                   ForEach-Object {
                                if($_.RequiredServices) {
                                        foreach($r in $_.RequiredServices)
                                        { $r.name } #foreach
                                } #if RequiredServices
                   } #ForEach-Object
                if($depends){
                        $temp = 0
                        foreach ($element in $depends) { $temp=$temp+1} #foreach
                        if($temp -gt 1){
                                [array]::Reverse($depends)
                                $depends+=$ServiceName
                                write-output "########################### Array of required services are below ###########################"
                                write-output "                                                                                                                                          "
                                foreach ($depend in $depends) { if($depend.Length -gt 0){ write-output "$depend" }} #foreach
                        } #if
                        if($temp -eq 1){
                                $depends=($depends,$ServiceName)
                                write-output "########################### Array of required services are below ###########################"
                                write-output "                                                                                                                                                         "
                                foreach ($depend in $depends) {if($depend.Length -gt 0){ write-output "$depend" }} #foreach
                        } #if
                } #if depends
        else{
                $depends=$ServiceName
                write-output "######## Service name: $ServiceNameRetrieved does not have any required service ########"
                                "                                                                                                                                                         "
        } #if SVcName

  $UnabletoStart="false"
  $startmodedisable="false"
  write-output "                                                                                                                                          "
  write-output "########################### Proceeding to start services ##########################"
  write-output "                                                                                                                                          "
  foreach ($depend in $depends )
  {
      $Service = gwmi Win32_Service -computername $Computer -ErrorAction SilentlyContinue| where-object {$_.Name -eq $depend}
      if($Service.state -ne "Running" -and $UnabletoStart -eq "false" -and $startmodedisable -eq "false") {
         $startmode=$Service.StartMode
         if($startmode -eq "Disabled") {
           $startmodedisable="true"
           $UnabletoStart="true"
           $displayname=$Service.DisplayName
           write-output "                                                                                                                                 "
           write-output "######################### $displayname service is disabled ########################"
           write-output "                                                                                                                                 "
         } #if
         $servicestarted = "false"
         $i=5
         do
         {
           if($servicestarted -eq "false" -and $UnabletoStart -eq "false" -and $startmodedisable -eq "false" ){
            $displayname=$Service.DisplayName
            if($displayname.Length -gt 0)
            {
                           Write-Output "Proceeding to start service name $displayname"}
            Else
            {
                           Write-Output "Proceeding to start service name $SvcName"}
            $ret = $SvcName.StartService()
           }; #if
           Start-Sleep -s 300
                   Write-Output "Sleep 300s"
           $i++
           $Servicestatus = gwmi Win32_Service -computername $Computer -ErrorAction SilentlyContinue| where-object {$_.Name -eq $depend}
           $state=$Servicestatus.State
           $serviceInstance=$Servicestatus.Name
           $retState=$ret.ReturnValue
          # $retState=1  #Just for testing remove before production
           if($retState -eq 0 -and $state -eq "Running" )
           {
            $i=$SleepSec
            if ($retState -eq 0 -and $ServiceName -ne $serviceInstance) {
              $displayname=$Service.DisplayName
                          $servicestarted = "true"
              Write-output "Service state : successfully_started on server $Computer"
            } #if
           }
           else
           {
             #write-output "displayname=$displayname depend=$depend and ServiceNameRetrieved=$ServiceNameRetrieved"
             #if ( $displayname -eq $ServiceNameRetrieved -and $displayname -notcontains "Print Spooler" -and $displayname -notcontains "Remote Procedure Call" -and $displayname -notcontains "HTTP" )
             if ( $displayname -contains "Citrix Print Manager Service" )
             {
                   $SvcNameLength=$depend.Length
                   if($depend.Length -gt 0 -and $count -lt 1)  #Change this before production - just for testing set to ne instead of eq
                   {
                         force-start-service $Computer $depend
                         $count=$count+1
                   }
             }
           } #if
         } #do
      while ($i -lt $SleepSec)
        $Ser=$Service.name
        if ("$servicestarted" -eq "false"){
           $UnabletoStart="true"
           $displayname=$Service.DisplayName
           write-output "                                                                                                                         "
           write-output "######## Either service in question or any dependent service, fail to start #######"
           write-output "                                                                                                                         "
           Write-output "Service state : fail_to_start on server $Computer"
                   write-output "                                                                                                                         "
           write-output "                                                                                                                         "
        } #if
      } #if Service.state
      else{
        $Ser=$Service.name
        if($ServiceName -ne $Ser -and $UnabletoStart -eq "false" -and $startmodedisable -eq "false"){
          $displayname=$Service.DisplayName
          write-output "Service name $displayname is already running"
        } #if
      } #if-else Service.state
   } #foreach depend
      $ServiceN=$SvcName.Name
      $ParentService = gwmi Win32_Service -computername $Computer -ErrorAction SilentlyContinue| where-object {$_.Name -eq $ServiceN}
      $ParentServiceState=$ParentService.state
      if($UnabletoStart -ne "true" -and $UnabletoStart -eq "false" -and $startmodedisable -eq "false" -and $ParentServiceState -eq "Running"){
        $displayname = $SvcName.DisplayName
        write-output "                                                                                                                                          "
        Write-output "Service state : successfully_started on server $Computer"
        write-output "                                                                                                                                          "
        Write-output "Status                    Name"
        Write-output "------                    ----"
        foreach ($depend in $depends )
        {
          $CheckService = gwmi Win32_Service -computername $Computer -ErrorAction SilentlyContinue| where-object {$_.Name -eq $depend}
          $Sname=$CheckService.DisplayName
          $Sstate=$CheckService.State
          if ($Sname.Length -gt 0) {Write-output "$Sstate                   $Sname"}
        } #foreach
        write-output "                                                                                                                                          "
        write-output "############################### End of service stats ##############################"
      } #if UnabletoStart
}
else
{
  if ($SvcName.state -eq "Running"){
    $displayname = $SvcName.DisplayName
    write-output "                                                                                                                                          "
    Write-output "Service state : running on server $Computer"
    write-output "                                                                                                                                          "
  } #if
  if($Svcstartmode -eq "Disabled"){
    $displayname=$SvcName.DisplayName
    write-output "                                                                                                                                          "
    Write-output "Service state : disabled on server $Computer"
    write-output "                                                                                                                                          "
  } #if
  } #Try
}# if-else result.statuscode
else{
  write-output "                                                                                                                                          "
  Write-output "Service state : not-found on server $Computer"
  write-output "                                                                                                                                          "
} #if-else
}
write-output "SERVICE RESTART SCRIPT END"
        exit 0
        } else {
                exit 9999
        }
} Catch {
        exit 9999
}
}
write-output "Server $Computer not pingable from $CheckHost"
write-output ""
write-output "CHECKDETAILSEND"
{
}

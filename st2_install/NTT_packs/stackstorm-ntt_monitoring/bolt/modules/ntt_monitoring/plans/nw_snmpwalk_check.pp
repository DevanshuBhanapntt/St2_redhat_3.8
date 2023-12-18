# This plan runs a script to get network device snmp walk details
plan ntt_monitoring::nw_snmpwalk_check (
  TargetSpec $targets,
  String[1] $deviceip,
  String[1] $version, 
  String[1] $community,
  String[1] $nms_ip,
  String[1] $oid,  
  String[1] $securityname,
  String[1] $authprotocol,
  String[1] $authkey,
  String[1] $privkey,
  String[1] $privprotocol,
  
) {
  # load in StackStorm vairables form the datastore (if specified)
  run_plan('ntt_monitoring::st2kv_env', $targets)

  # Run the snmp wals script
  $devicesnmpwalk = run_task('ntt_monitoring::nw_snmpwalk_check', $targets,
                     deviceip => $deviceip,
					 version => $version,
					 community => $community,
					 nms_ip => $nms_ip,
					 oid => $oid,
					 securityname => $securityname,
					 authprotocol => $authprotocol,
					 authkey => $authkey,
					 privkey => $privkey,
					 privprotocol => $privprotocol)

  $script_output = $devicesnmpwalk.first().value['_output']
  
  $snmpwalk_split = split($script_output, 'SNMPWalk:')[1]
  $snmpwalk_split_lstrip = $snmpwalk_split.lstrip()
  $snmpwalk_split_rstrip = $snmpwalk_split_lstrip.rstrip()   
  $result_hash = {"output" => $script_output, "SNMPWalk" => $snmpwalk_split_rstrip}

  return $result_hash
}

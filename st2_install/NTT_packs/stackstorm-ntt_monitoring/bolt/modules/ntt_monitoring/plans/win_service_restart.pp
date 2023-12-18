# Gather service information for the given VM 
plan ntt_monitoring::win_service_restart (
  TargetSpec $targets,   
  String $dns_domain,
  String[1] $servicename,
  Integer $sleepsec  
) {
  # load in StackStorm variables from the datastore (if specified)
  run_plan('ntt_monitoring::st2kv_env', $targets)

  $result = run_task('ntt_monitoring::win_service_restart', $targets,
                      dns_domain => $dns_domain,
                      servicename => $servicename,
					  sleepsec => $sleepsec)
			  
  $script_output = $result.first().value['_output']
  $server_service_status_split = split($script_output, 'Service state :')[1]
  $server_service_status = split($server_service_status_split, "on")[0]
  $server_service_status_lstrip = $server_service_status.lstrip()
  $server_service_status_rstrip = $server_service_status_lstrip.rstrip()  
  $result_hash = {"output" => $script_output, "server_service_status" => $server_service_status_rstrip}
  return $result_hash
}

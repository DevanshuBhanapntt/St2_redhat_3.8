# This plan runs a script to get network device details
plan ntt_monitoring::nw_invoke_clogin (
  TargetSpec $targets,
  String[1] $device_ip,
  String[1] $device_username,
  String[1] $device_password, 
  String[1] $commands,
  String[1] $clogin_script_path,
  String[1] $nms_ip,  
) {
  # load in StackStorm vairables form the datastore (if specified)
  run_plan('ntt_monitoring::st2kv_env', $targets)

  # Run the disk utilization script
  $deviceres = run_task('ntt_monitoring::nw_invoke_clogin', $targets,
                     device_ip => $device_ip,
                     device_username => $device_username,
					 device_password => $device_password,
					 commands => $commands,
					 clogin_script_path => $clogin_script_path,
					 nms_ip => $nms_ip)

  $script_output = $deviceres.first().value['_output']
  
  $device_access_split = split($script_output, 'DeviceLogin:')[1]
  $device_access_split_lstrip = $device_access_split.lstrip()
  $device_access_split_rstrip = $device_access_split_lstrip.rstrip()   
  $result_hash = {"output" => $script_output, "DeviceLogin" => $device_access_split_rstrip}
    
  return $result_hash
}

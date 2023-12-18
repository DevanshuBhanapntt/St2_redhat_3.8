# This plan runs a script to get cpu usage details
plan ntt_monitoring::cpu_check_unix (
  TargetSpec $targets,
  String $status,
  Integer $threshold,
  String $host_username,
  String $host_password,
  String $solaris_username,
  String $solaris_password,
  String $hostname,
  String $os_name
) {
  # load in StackStorm vairables form the datastore (if specified)
  run_plan('ntt_monitoring::st2kv_env', $targets)
# Run the cpu utilization script
  $cpu = run_task('ntt_monitoring::cpu_check_unix', $targets,
                   status    => $status,
                   threshold => $threshold,
				   host_username => $host_username,
				   host_password => $host_password,
				   solaris_username => $solaris_username,
				   solaris_password => $solaris_password,
				   hostname => $hostname,
				   os_name => $os_name)
				   
  $script_output = $cpu.first().value['_output']

# Extract the utilization percentage from script output
  
  $utilization_split = split($script_output, 'cpu is: ')[1]
  $utilization_string = split($utilization_split, ' ')[0]
  $utilization = $utilization_string

# Create hash to return the utilization value as well as the enire script output

$result_hash = {"utilization" => $utilization, "output" => $script_output}

return $result_hash

}

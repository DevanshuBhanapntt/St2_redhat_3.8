# This plan runs a script to get memory usage details
plan ntt_monitoring::mem_check (
  TargetSpec $targets,
  String $status,
  Integer $threshold,
  String $unix_username,
  String $unix_password,
  String $solaris_username,
  String $solaris_password,
  String $aix_username,
  String $aix_password,
  String $hostname,
  String $os_name

) {
  # load in StackStorm vairables form the datastore (if specified)
  run_plan('ntt_monitoring::st2kv_env', $targets)

  # Run the memory utilization script
  $memory = run_task('ntt_monitoring::mem_check', $targets,
                     status    => $status,
                     threshold => $threshold,
                     unix_username => $unix_username,
                     unix_password => $unix_password,
                     solaris_username => $solaris_username,
                     solaris_password => $solaris_password,
                     aix_username => $aix_username,
                     aix_password => $aix_password,
                     hostname => $hostname,
                     os_name => $os_name)

  $script_output = $memory.first().value['_output']

  # Extract the utilization percentage from script output
  $value = split($script_output, /\n/)[2]
  $regexp = '(\d+(\.\d+)?)'
  $result = split($value, $regexp)[1]
  $utilization = $result

  # Create hash to return the utilization value as well as the enire script output
  $result_hash = {"utilization" => $utilization, "output" => $script_output}

  return $result_hash
}

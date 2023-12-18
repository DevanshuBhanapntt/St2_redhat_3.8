# This plan runs a script to get service status details
plan ntt_monitoring::unix_process_alert (
  TargetSpec $targets,
  String[1] $service,
) {
  # load in StackStorm vairables form the datastore (if specified)
  run_plan('ntt_monitoring::st2kv_env', $targets)

  # Run the cpu utilization script
  $service_status = run_task('ntt_monitoring::unix_process_alert', $targets,
                     service => $service)

  $script_output = $service_status.first().value['_output']

  # Extract the utilization percentage from script output
  $value = split($script_output, /\n/)[2]
  $regexp = '(\d+(\.\d+)?)'
  $result = split($value, $regexp)[1]

  # Create hash to return the service status as well as the entire script output
  $result_hash = {"output" => strip($script_output)}

  return $result_hash
}

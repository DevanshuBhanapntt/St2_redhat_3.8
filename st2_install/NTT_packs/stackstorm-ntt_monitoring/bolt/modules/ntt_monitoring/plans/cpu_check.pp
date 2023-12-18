# Gather CPU utilization information for the given VM and CPU name
plan ntt_monitoring::cpu_check (
  TargetSpec $targets,
  String[1] $cpu_name,
  String[1] $cpu_type,
  String $dns_domain,
  String $threshold_percent,
  Integer $top_process_limit
) {
  # load in StackStorm variables from the datastore (if specified)
  run_plan('ntt_monitoring::st2kv_env', $targets)

  $result = run_task('ntt_monitoring::cpu_check', $targets,
                      cpu_name => $cpu_name,
                      cpu_type => $cpu_type,
                      dns_domain => $dns_domain,
                      threshold_percent => $threshold_percent,
                      top_process_limit => $top_process_limit)

  $script_output = $result.first().value['_output']

  # Parse the CPU utilization from the output
  $cpu_percent_usage_split = split($script_output, 'CPU% Utilization : ')[1]
  $cpu_percent_usage = split($cpu_percent_usage_split, "%")[0]

  $result_hash = {"output" => $script_output, "cpu_percent_usage" => $cpu_percent_usage}
  return $result_hash
}

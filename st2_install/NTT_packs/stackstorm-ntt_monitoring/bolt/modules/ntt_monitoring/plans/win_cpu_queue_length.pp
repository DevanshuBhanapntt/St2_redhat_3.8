# Gather cpu queue length information for the given VM 
plan ntt_monitoring::win_cpu_queue_length (
  TargetSpec $targets,   
  String $dns_domain,
  String[1] $cpu_type,
  String[1] $cpu_name
) {
  # load in StackStorm variables from the datastore (if specified)
  run_plan('ntt_monitoring::st2kv_env', $targets)

  $result = run_task('ntt_monitoring::win_cpu_queue_length', $targets,
                      dns_domain => $dns_domain,
                      cpu_type => $cpu_type,
					  cpu_name => $cpu_name )
					  
  $script_output = $result.first().value['_output']
  
  # Parse the CPU queue length from the output
  $cur_cpu_avg_queue_length_split = split($script_output, 'System Processor Queue Length% :')[1]
  $cur_cpu_avg_queue_length = split($cur_cpu_avg_queue_length_split, "on")[0] 
  $cur_cpu_avg_queue_length_lstrip = $cur_cpu_avg_queue_length.lstrip()
  $cur_cpu_avg_queue_length_rstrip = $cur_cpu_avg_queue_length_lstrip.rstrip()  
  
  $result_hash = {"output" => $script_output, "cur_cpu_avg_queue_length" => $cur_cpu_avg_queue_length_rstrip}
  return $result_hash
}

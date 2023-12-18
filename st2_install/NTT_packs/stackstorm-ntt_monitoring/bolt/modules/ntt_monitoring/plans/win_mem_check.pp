# Gather memory utilization information for the given VM 
plan ntt_monitoring::win_mem_check (
  TargetSpec $targets,   
  String $dns_domain,
  String[1] $memory_type,
  String $threshold_percent   
) {
  # load in StackStorm variables from the datastore (if specified)
  run_plan('ntt_monitoring::st2kv_env', $targets)

  $result = run_task('ntt_monitoring::win_mem_check', $targets,
                      dns_domain => $dns_domain,
                      threshold_percent => $threshold_percent)
					  
  $script_output = $result.first().value['_output']
  if $memory_type == 'Physical' 
  {
	$memory_percent_usage_split = split($script_output, 'Physical Memory Usage :')[1]
	$mem_percent_usage = split($memory_percent_usage_split, "%")[0]
  }
  elsif $memory_type == 'Virtual' 
  {
    $memory_percent_usage_split = split($script_output, 'Virtual Memory Usage :')[1]
	$mem_percent_usage = split($memory_percent_usage_split, "%")[0]
  }
  elsif $memory_type == 'PagesPerSec'
  {
    $memory_percent_usage_split = split($script_output, 'PagingFilePercentUsed :')[1]
	$mem_percent_usage = split($memory_percent_usage_split, "%")[0]
  }
  elsif $memory_type == 'PagingFile'
  {
    $memory_percent_usage_split = split($script_output, 'PagingFilePercentUsed :')[1]
	$mem_percent_usage = split($memory_percent_usage_split, "%")[0]
  }
  else
  {
	$memory_percent_usage_split = split($script_output, 'Physical Memory Usage :')[1]
	$mem_percent_usage = split($memory_percent_usage_split, "%")[0]
  }     
  $result_hash = {"output" => $script_output, "memory_percent_usage" => $mem_percent_usage}
  return $result_hash
}

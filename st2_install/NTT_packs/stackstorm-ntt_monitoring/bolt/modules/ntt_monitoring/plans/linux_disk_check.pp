# This plan runs a script to get disk usage details
plan ntt_monitoring::linux_disk_check (
  TargetSpec $targets,
  String[1] $disk_name,
  String[1] $linux_disk_yum_cache_clear, 
  String[1] $linux_disk_clean_files,  
) {
  # load in StackStorm vairables form the datastore (if specified)
  run_plan('ntt_monitoring::st2kv_env', $targets)

  # Run the disk utilization script
  $memory = run_task('ntt_monitoring::lnx_disk_usage_check', $targets,
                     disk_name    => $disk_name,
					 linux_disk_yum_cache_clear => $linux_disk_yum_cache_clear,
					 linux_disk_clean_files => $linux_disk_clean_files)

  $script_output = $memory.first().value['_output']

  $current_disk_util_split = split($script_output, 'Current disk utilization :')[1]
  $current_disk_util = split($current_disk_util_split, "%")[0]
  $current_disk_util_lstrip = $current_disk_util.lstrip()
  $current_disk_util_rstrip = $current_disk_util_lstrip.rstrip() 
  # Create hash to return the utilization value as well as the enire script output
  $result_hash = {"output" => $script_output, "current_disk_util" => $current_disk_util_rstrip}

  return $result_hash
}

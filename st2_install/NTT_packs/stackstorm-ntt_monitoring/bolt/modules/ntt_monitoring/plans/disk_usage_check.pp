# Gather hard drive utilization information for the given VM and drive
plan ntt_monitoring::disk_usage_check (
  TargetSpec $targets,
  String[1] $ci_address,
  String[1] $disk_name
) {
  # load in StackStorm variables from the datastore (if specified)
  run_plan('ntt_monitoring::st2kv_env', $targets)

  $result = run_task('ntt_monitoring::disk_usage_check', $targets,
                      ci_address => $ci_address,
                      disk_name => $disk_name)

  unless $result.ok {
    fail("Task disk_usage_check failed on the targets ${result.error_set.names}")
  }

  return {size => $result[0].value['size'], free_space => $result[0].value['free_space']}
}

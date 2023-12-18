plan ntt_monitoring::tsm_backup_getprocesstime (
  TargetSpec $targets,
  String $ip_address,
  String $ci_name,
  String $affected_drive,
  String $username,
  String $password,
  String $is_eighthour_ci,
  String $service_window_check,
  String $dignity_healthservers
) {
  # load in StackStorm vairables form the datastore (if specified)
  run_plan('ntt_monitoring::st2kv_env', $targets)

  $output = run_task('ntt_monitoring::tsm_backup_getprocesstime', $targets,
                     ip_address    => $ip_address,
                     ci_name => $ci_name,
                     affected_drive => $affected_drive,
                     username => $username,
                     password => $password,
                     is_eighthour_ci => $is_eighthour_ci,
                     service_window_check => $service_window_check,
                     dignity_healthservers => $dignity_healthservers)

  $script_output = $output.first().value['_output']

  $value = split($script_output, 'CI = ')[1]
  $backup_processing_time = split($value, 'minutes')[0]

  $result_hash = {"backup_processing_time" => $backup_processing_time, "output" => $script_output}

  return $result_hash
}

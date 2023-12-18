plan ntt_monitoring::tsm_backup_healthcheck (
  TargetSpec $targets,
  String $ip_address,
  String $ci_name,
  String $affected_drive,
  String $username,
  String $password
) {
  # load in StackStorm vairables form the datastore (if specified)
  run_plan('ntt_monitoring::st2kv_env', $targets)

  $output = run_task('ntt_monitoring::tsm_backup_healthcheck', $targets,
                     ip_address    => $ip_address,
                     ci_name => $ci_name,
                     affected_drive => $affected_drive,
                     username => $username,
                     password => $password)

  $script_output = $output.first().value['_output']
  
  $value = split($script_output, 'identified as ')[1]
  $system_drive_letter = split($value, ' ')[0]  


  # Create hash to return output
  $result_hash = { "system_drive_letter" => $system_drive_letter, "output" => $script_output}

  return $result_hash
}

plan ntt_monitoring::tsm_backup_checkcompletion (
  TargetSpec $targets,
  String $ip_address,
  String $ci_name,
  String $system_drive_letter,
  String $username,
  String $password,
  String $file_name_string,
  String $process_id,
  String $last_iteration,
  String $incident_state
) {
  # load in StackStorm vairables form the datastore (if specified)
  run_plan('ntt_monitoring::st2kv_env', $targets)

  $output = run_task('ntt_monitoring::tsm_backup_checkcompletion', $targets,
                     ip_address    => $ip_address,
                     ci_name => $ci_name,
                     system_drive_letter => $system_drive_letter,
                     username => $username,
                     password => $password,
                     file_name_string => $file_name_string,
                     process_id => $process_id,
                     last_iteration => $last_iteration,
					 incident_state => $incident_state)

  $script_output = $output.first().value['_output']

  $value = split($script_output, 'BACKUP STATUS : ')[1]
  $backup_status = split($value, ' ')[0]

  # Create hash to return output
  $result_hash = {"backup_status" => $backup_status, "output" => $script_output}

  return $result_hash
}

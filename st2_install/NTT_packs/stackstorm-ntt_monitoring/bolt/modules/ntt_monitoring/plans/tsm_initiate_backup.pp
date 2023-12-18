plan ntt_monitoring::tsm_initiate_backup (
  TargetSpec $targets,
  String $ip_address,
  String $ci_name,
  String $system_drive_letter,
  String $username,
  String $password
) {
  # load in StackStorm vairables form the datastore (if specified)
  run_plan('ntt_monitoring::st2kv_env', $targets)

  $output = run_task('ntt_monitoring::tsm_initiate_backup', $targets,
                     ip_address    => $ip_address,
                     ci_name => $ci_name,
                     system_drive_letter => $system_drive_letter,
                     username => $username,
                     password => $password)

  $script_output = $output.first().value['_output']

  $value = split($script_output, 'Process ID : ')[1]
  $process_id = split($value, ' ')[0]
  $batchfile = split($script_output, 'BatchFile ')[1]
  $batch_file_name = split($batchfile, ' ')[0]

  # Create hash to return output
  $result_hash = {"process_id" => $process_id, "output" => $script_output, "batch_file_name" => $batch_file_name }

  return $result_hash
}

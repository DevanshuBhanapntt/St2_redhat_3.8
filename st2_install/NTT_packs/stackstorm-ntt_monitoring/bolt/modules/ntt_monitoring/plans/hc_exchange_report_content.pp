# Gather db white space and incremental back up for Exchange servers 
plan ntt_monitoring::hc_exchange_report_content (
  TargetSpec $targets,   
  String $filepath,
  String $filematchstring,
  String $username,
  String $password
  
) {
  # load in StackStorm variables from the datastore (if specified)
  run_plan('ntt_monitoring::st2kv_env', $targets)  
  $result = run_task('ntt_monitoring::hc_exchange_report_content', $targets,
                      filepath => $filepath,
                      filematchstring => $filematchstring,
					  username => $username,
					  password => $password)
  $script_output = $result.first().value['_output']
  $result_hash = {"output" => $script_output}
  return $result_hash
}
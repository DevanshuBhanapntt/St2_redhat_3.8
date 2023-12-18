# Reads st2 KV data from environment variables
plan ntt_monitoring::st2kv_env (
  TargetSpec $targets
) {
  $_targets = get_targets($targets)

  # Read in data from environment variables that overwrites the config items in Bolt.
  # The ST2KV_CONFIG variable is a JSON hash
  $config_json = system::env('ST2KV_CONFIG')
  if $config_json {
    $config = run_plan('ntt_monitoring::st2kv_json_read',
                        json => $config_json)
    $config.each |$config_key, $st2kv_value| {
      $_targets.each |$t| {
        $config_key_split = $config_key.split('\.')
        out::message("Setting config ['${config_key}' split=${config_key_split}] on node [${t}] with value from datastore")
        set_config($t, $config_key_split, $st2kv_value)
      }
    }
  }

  # Read in data from environment variables that overwrites the facts in Bolt.
  # The ST2KV_FACTS variable is a JSON hash
  $facts_json = system::env('ST2KV_FACTS')
  if $facts_json {
    $st2_facts = run_plan('ntt_monitoring::st2kv_json_read',
                          json => $facts_json)
    $st2_facts.each |$facts_key, $st2kv_value| {
      $_targets.each |$t| {
        out::message("Setting fact [${facts_key}] on node [${t}] with value from datastore")
        add_facts($t, {$facts_key => $st2kv_value})
      }
    }
  }

  # Read in data from environment variables that overwrites the vars in Bolt.
  # The ST2KV_VARS variable is a JSON hash
  $vars_json = system::env('ST2KV_VARS')
  if $vars_json {
    $st2_vars = run_plan('ntt_monitoring::st2kv_json_read',
                          json => $vars_json)
    $st2_vars.each |$vars_key, $st2kv_value| {
      $_targets.each |$t| {
        out::message("Setting var [${vars_key}] on node [${t}] with value from datastore")
        set_var($t, $vars_key, $st2kv_value)
      }
    }
  }
}

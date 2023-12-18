# Read in data from a JSON string that overwrites the config items in Bolt.
# The ST2KV_CONFIG variable is a JSON hash with the following syntax:
#   {
#     'config_key': 'system.data.xxx',
#     'another_config_key': 'system.example.yyy',
#   }
#
# Each key represents a path in the bolt config.
# Each value represents the name of a a StackStorm key in the datastore
# (with the scope prefix ex: 'system.xxx' or 'user.yyy').
#
# Nested elements in the bolt config need to have a '.' that separate the different levels
# Example:
#
#  Bolt Config:
#
#   ssh:
#     username: xxx
#     password: yyy
#
#  ST2KV_CONFIG data (must be JSON encoded):
#    {
#      'ssh.username': 'system.xxx',
#      'ssh.password': 'system.yyy'
#    }
plan ntt_monitoring::st2kv_json_read (
  String $json,
) {
  $localhost = get_targets('local://localhost')

  if system::env('ST2_AUTH_TOKEN') {
    $auth_token = system::env('ST2_AUTH_TOKEN')
  }
  else {
    $auth_token = system::env('ST2_ACTION_AUTH_TOKEN')
  }
  $api_key = system::env('ST2_API_KEY')

  if $json {
    # convert JSON to hash
    $data = parsejson($json)
    # map hash of config keys and datstore keys to....
    # a hash of config keys and datastore values
    return $data.reduce({}) |$memo, $value| {
      $data_key = $value[0]
      $st2kv_key = $value[1]

      # value is of format: <scope>.<key.parts.blah>
      # example:
      #   system.linux.username
      #
      # scope = system
      # key = linux.username
      $parts = split($st2kv_key, '\.')
      $scope = $parts[0]
      $key = join($parts[1, -1], '.')

      # read data from StackStorm
      $res = run_task('st2::key_get', $localhost,
                      scope      => $scope,
                      key        => $key,
                      decrypt    => true,
                      convert    => true,
                      api_key    => $api_key,
                      auth_token => $auth_token)

      # add this new value to the existing memo
      $st2kv_value = $res.first.value['result']['value']
      $memo + {$data_key => $st2kv_value}
    }
  }
  else {
    return []
  }
}

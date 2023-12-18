# Try to clear space for the given hard drive
plan ntt_monitoring::disk_cleanup (
  TargetSpec       $targets,
  String[1]        $ci_address,
  Boolean          $cleanmgr_tasks,
  Boolean          $compress_files,
  Integer          $compress_file_age_days,
  Array[String]    $compress_file_exts,
  Integer          $compress_file_min_size_mb,
  Array[String]    $directories,
  String[1]        $disk_name,
  Array[Hash]      $file_exts,
  Array[String]    $file_names,
  Integer          $profile_age_days,
  Boolean          $remove_profiles,
  Boolean          $remove_temp_files,
  Boolean          $remove_temp_ie_files,
  Array[String]    $temp_folders
) {
  # load in StackStorm variables from the datastore (if specified)
  run_plan('ntt_monitoring::st2kv_env', $targets)
  ###########################################
  # Run cleanmgr tasks
  ###########################################

  if $cleanmgr_tasks {
    $cleanmgr_result = run_task('ntt_monitoring::disk_cleanmgr', $targets,
                                ci_address => $ci_address,
                                disk_name  => $disk_name)

    unless $cleanmgr_result.ok {
      fail("disk_cleanup failed on cleanmgr tasks for targets ${result.error_set.names}")
    }

    $cleanmgr_output = $cleanmgr_result.first().value['_output']

    # Check if any files were deleted
    $cleanmgr_del_split = split($cleanmgr_output, 'Total deleted files: ')[1]
    $cleanmgr_del = split($cleanmgr_del_split, "\n")[0].scanf('%d')[0]
  }
  else {
    $cleanmgr_output = ''
    $cleanmgr_del = 0
  }

  ###########################################
  # Clean Given Directories
  ###########################################

  if $directories {
    $dir_result = run_task('ntt_monitoring::disk_clean_dirs', $targets,
                            ci_address  => $ci_address,
                            directories => $directories,
                            disk_name   => $disk_name)

    unless $dir_result.ok {
      fail("disk_cleanup failed to clean directories for targets ${result.error_set.names}")
    }

    $dirs_output = $dir_result.first().value['_output']

    # Check if any files were deleted
    $dirs_del_split = split($dirs_output, 'Total deleted files: ')[1]
    $dirs_del = split($dirs_del_split, "\n")[0].scanf('%d')[0]
  }
  else {
    $dirs_output = ''
    $dirs_del = 0
  }

  ###########################################
  # Remove All Files With Given Extension
  ###########################################

  if $file_exts {
    $file_ext_result = run_task('ntt_monitoring::disk_clean_file_exts', $targets,
                                ci_address => $ci_address,
                                disk_name  => $disk_name,
                                file_exts  => $file_exts)

    unless $file_ext_result.ok {
      fail("disk_cleanup failed to remove files with extensions for targets ${result.error_set.names}")
    }

    $file_ext_output = $file_ext_result.first().value['_output']

    # Check if any files were deleted
    $ext_del_split = split($file_ext_output, 'Total deleted files: ')[1]
    $ext_del = split($ext_del_split, "\n")[0].scanf('%d')[0]
  }
  else {
    $file_ext_output = ''
    $ext_del = 0
  }

  ###########################################
  # Remove All Files With Given Name
  ###########################################

  if $file_names {
    $file_name_result = run_task('ntt_monitoring::disk_clean_file_names', $targets,
                                  ci_address => $ci_address,
                                  disk_name  => $disk_name,
                                  file_names => $file_names)

    unless $file_name_result.ok {
      fail("disk_cleanup failed to remove files with names for targets ${result.error_set.names}")
    }

    $file_name_output = $file_name_result.first().value['_output']

    # Check if any files were deleted
    $name_del_split = split($file_name_output, 'Total deleted files: ')[1]
    $name_del = split($name_del_split, "\n")[0].scanf('%d')[0]
  }
  else {
    $file_name_output = ''
    $name_del = 0
  }

  ###########################################
  # Remove Old User Profiles
  ###########################################

  if $remove_profiles {
    $prof_result = run_task('ntt_monitoring::disk_clean_profiles', $targets,
                            ci_address       => $ci_address,
                            disk_name        => $disk_name,
                            profile_age_days => $profile_age_days)

    unless $prof_result.ok {
      fail("disk_cleanup failed to clean profiles for targets ${result.error_set.names}")
    }

    $prof_output = $prof_result.first().value['_output']

    # Check if any profiles were deleted
    $prof_del_split = split($prof_output, 'Total deleted profiles: ')[1]
    $prof_del = split($prof_del_split, "\n")[0].scanf('%d')[0]
  }
  else {
    $prof_output = ''
    $prof_del = 0
  }

  ###########################################
  # Remove Temp Files
  ###########################################

  if $remove_temp_files or $remove_temp_ie_files {
    $temp_result = run_task('ntt_monitoring::disk_clean_temp_files', $targets,
                            ci_address           => $ci_address,
                            disk_name            => $disk_name,
                            remove_temp_files    => $remove_temp_files,
                            remove_temp_ie_files => $remove_temp_ie_files)

    unless $temp_result.ok {
      fail("disk_cleanup failed to clean temp files for targets ${result.error_set.names}")
    }
    $temp_output = $temp_result.first().value['_output']

    # Check if any files were deleted
    $temp_del_split = split($temp_output, 'Total deleted files: ')[1]
    $temp_del = split($temp_del_split, "\n")[0].scanf('%d')[0]
  }
  else {
    $temp_output = ''
    $temp_del = 0
  }

  ###########################################
  # Compress Files
  ###########################################

  if $compress_files {
    $comp_result = run_task('ntt_monitoring::disk_compress_files', $targets,
                            ci_address          => $ci_address,
                            disk_name           => $disk_name,
                            file_age_days       => $compress_file_age_days,
                            file_extensions     => $compress_file_exts,
                            file_min_size_mb    => $compress_file_min_size_mb)

    unless $comp_result.ok {
      fail("disk_cleanup failed to compress files for targets ${result.error_set.names}")
    }

    $comp_output = $comp_result.first().value['_output']

    # Check if any files were compressed
    $comp_files_split = split($comp_output, 'Files Compressed: ')[1]
    $comp_files = split($comp_files_split, "\n")[0].scanf('%d')[0]
  }
  else {
    $comp_output = ''
    $comp_files = 0
  }

  # Count the number of files that were deleted or compressed
  $files_deleted = $cleanmgr_del + $dirs_del + $ext_del + $name_del + $prof_del + $temp_del + $comp_files

  $result_string = "${dirs_output} \n ${prof_output} \n ${file_ext_output} \n ${file_name_output} \n ${temp_output} \n ${comp_output} \n ${files_deleted}$" 

  $result_hash = {
    'output'        => $result_string,
    'files_deleted'   => $files_deleted
  }

  return $result_hash
}

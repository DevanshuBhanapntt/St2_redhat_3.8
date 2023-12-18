#!/bin/bash
disk_name=$PT_disk_name
linux_disk_yum_cache_clear=$PT_linux_disk_yum_cache_clear
linux_disk_clean_files=$PT_linux_disk_clean_files
os_type=$(uname);
echo  "Disk Name: $disk_name"
echo  "linux_disk_yum_cache_clear: $linux_disk_yum_cache_clear"
echo  "linux_disk_clean_files: $linux_disk_clean_files"
###### Checking the utilization ######### 
pre_check_utilization=$(df -Th $disk_name) 
echo -e "pre check disk utilization:\n$pre_check_utilization"
if [[ "$linux_disk_yum_cache_clear" == "true" ]]
then
echo "Clearing Cache:-"
du -sh $disk/cache/yum ; yum clean all ;  rm -rf $disk/cache/yum/
fi
#linux_disk_clean_files="*messages*:10,*maillog*:10,*test_arul*:1"
my_array_commna=($(echo $linux_disk_clean_files | tr "," "\n"))

#Print the split string
for arr_comma_value in "${my_array_commna[@]}"
do
    #echo $arr_comma_value
	my_array_colon=($(echo $arr_comma_value | tr ":" "\n"))     
    rm_file_name=${my_array_colon[0]} 
    rm_file_aging_days=${my_array_colon[1]}	
	deleting_file=$(find $disk_name -type f \( -name "*$rm_file_name*" \) ! -mtime +$rm_file_aging_days -type f -printf '%s %p\n' ) ;echo "Deleted Files: $deleting_file" ; rm -f $deleting_file
	#deleting_file=$(find $disk -type f \( -name "*messages*" -o -name "*maillog*" -o -name "*yum*" -o -name "*audit*" -o -name "*waagent*" -o -name "*secure*" -o -name "*ntp*" -o -name "*cron*" \) ! -mtime +10 -type f -printf '%s %p\n' ) ; echo "Deleted Files: $deleting_file" ; rm -f $deleting_file

done
 
post_check_utilization=$(df -Th $disk_name) 
echo -e "post check disk utilization:\n$post_check_utilization"
current_disk_util=$(df --output=pcent $disk_name | grep -o '[0-9]*')
echo -e "Current disk utilization : $current_disk_util""%"

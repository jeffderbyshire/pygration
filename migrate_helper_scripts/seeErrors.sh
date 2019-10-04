#!/usr/bin/env bash


for log in `bash /root/migrate_helper_scripts/listMigrationLogs.sh errors |sort`

    do

        volume_serial=`echo ${log} | awk -F'-' '{print $4;}' | awk -F'.' '{print $1;}'`

        error_message=`grep -m 1 "ERR" ${log}`

        echo "${volume_serial} ---- ${log} ---- ${error_message}"

    done

exit
#!/usr/bin/env bash


mkdir -p /var/migration/errors

error_path=/var/migration/errors/migrate.errors

touch ${error_path}

error_message=/root/migrate_errors/`hostname -s`.log

echo "Volumes with more than 2 errors:" > ${error_path}
echo "" >> ${error_path}
echo $1 >> ${error_path}
echo "" >> ${error_path}
echo "" >> ${error_path}

for log in `bash /root/migrate_helper_scripts/listMigrationLogs.sh errors $1`

    do

        echo "________Migration Log File:___________________________________" >> ${error_path}
        echo ${log} >> ${error_path}
        echo "________head -1 log_file______________________________________" >> ${error_path}
        head -1 ${log} >> ${error_path}
        echo "________grep -m 1 'ERR'_______________________________________" >> ${error_path}
        grep -m 1 'ERR' ${log} >> ${error_path}
        echo "______________________________________________________________" >> ${error_path}
        echo "" >> ${error_path}
        echo "" >> ${error_path}


    done


cat ${error_message} | mail -s "migration log errors on `hostname`" jeffderb@fnal.gov


exit
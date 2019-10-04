#!/usr/bin/env bash


error_path=/var/migration/errors/

mkdir -p ${error_path}

for i in `bash /root/migrate_helper_scripts/listMigrationLogs.sh errors |sort`

    do

        # echo ${i};

        output=`grep -m 1 -E 'ERR' ${i} |awk -F'/pnfs/fs/usr/' '{print $2;}' |awk -F'/' '{print $1;}'`

        if [[ ! -z ${output} ]]

            then

                if [[ ${output} == "Migration" ]]

                    then

                        output=`grep -m 1 -E 'ERR' ${i} |awk -F'/pnfs/fs/usr/' '{print $2;}' |awk -F'/' '{print $2;}'`

                fi

                if [[ ${output} == "file_aggregation" ]]

                    then

                        output=`grep -m 1 -E 'ERR' ${i} |awk -F'/pnfs/fs/usr/' '{print $2;}' |awk -F'/' '{print $3;}'`

                fi

                touch ${error_path}${output}

                echo ${i} >> ${error_path}${output}

                # echo "${output} Done"

        fi

    done

    ls ${error_path}

exit
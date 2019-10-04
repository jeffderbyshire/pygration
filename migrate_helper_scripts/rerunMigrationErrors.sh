#!/usr/bin/env bash

cd /tmp

# rerun_script=/tmp/`mktemp migrate.XXXXXXXX`
rerun_script=/tmp/migrate.rerun

rm -f ${rerun_script}

touch ${rerun_script}

cat <<EOF >> ${rerun_script}
#!/usr/bin/env bash
cd /var/migration
source ~enstore/.bashrc
EOF

chmod 700 ${rerun_script}

mkdir -p /var/migration/retry

for i in `bash /root/migrate_helper_scripts/listMigrationLogs.sh errors $1`

do

    if test -f "$i"

    then

        retry=`head -1 ${i} |awk '/migrate_chimera/ && ! /--restore/ && ! /--scan/ {print $NF;}'`

        retry_path=/var/migration/retry/${retry}

        touch ${retry_path}

        head -1 ${i} | awk '/migrate_chimera/ && ! /--restore/ && ! /--scan/ {printf "%s ", strftime("%m/%d/%Y %H:%M:%S", systime()) >> "'${retry_path}'"; for(i=8;i<=NF;i++){printf "%s ", $i >> "'${retry_path}'"}; printf "\n" >> "'${retry_path}'"}'

        if ! grep -q "${retry}" ${rerun_script}; then

            head -1 ${i} | awk '/migrate_chimera/ && ! /--restore/ && ! /--scan/ {for(i=8;i<=NF;i++){printf "%s ", $i >> "'${rerun_script}'"}; printf "\n" >> "'${rerun_script}'"}'

        fi

    fi

done

node=`hostname`
echo "running script at "${rerun_script}
echo "ssh root@$node 'screen -d -m $rerun_script'"
/usr/bin/screen -d -m ${rerun_script}

exit
#!/usr/bin/env bash


usage()
{

    echo "usage: archiveProcessedLogs.sh [ archive | archive_with_errors ]"

}

main()
{
    for i in `bash /root/migrate_helper_scripts/listMigrationLogs.sh $1 $2`
        do
            if test -f "$i"
            then
                gzip ${i}
                year=`echo ${i} |cut -d'@' -f 2 |cut -d'-' -f 1`
                month=`echo ${i} |cut -d'@' -f 2 |cut -d'-' -f 2`
                echo "moving ${i}.gz file to ${year}/${month}"
                mkdir -p /var/migration/${year}/${month}/
                mv ${i}.gz /var/migration/${year}/${month}/
            fi
        done

    echo "Finished archiving log files"

}

while [[ "$1" != "" ]]; do
    case $1 in
        archive )               main "archive"
                                exit
                                ;;
        archive_with_errors )   main "archive_with_errors" $2
                                exit
                                ;;
        -h | --help )           usage
                                exit
                                ;;
        * )                     usage
                                exit 1
    esac
    shift
done

exit

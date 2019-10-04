#!/usr/bin/env bash


usage()
{

    echo "usage: listMigrationLogs [ all | errors | no-errors | archive | archive_with_errors ]"

}

list_all()
{

    eval ${m_command_1}

}

list_errors()
{

    eval ${m_command_1} |grep '\.0$'

}

list_no-errors()
{

    eval ${m_command_1} |grep -vE '\.0$|\-V|\-P|\-I'

}

list_archivable()
{

    eval ${m_command_archive} |grep -vE '\.0$' |grep -E '\-V|\-P|\-I'

}

list_archivable_with_errors()
{

    eval ${m_command_archive} |grep -E '\-V|\-P|\-I'

}

list_volumes()
{
    if [[ $1 != "" ]]

    then

        eval ${m_command_1} |grep -E "$1"

    fi

}

m_command_1='find /var/migration/  -maxdepth 1 -name "MigrationLog*" -mtime +0.5'

m_command_archive='find /var/migration/ -maxdepth 1 -name "MigrationLog*" -mtime +2'

while [[ "$1" != "" ]]; do
    case $1 in
        all )   list_all
                exit
                ;;
        errors )
            if [[ $2 != "" ]]
                then
                    list_volumes $2
            else
                list_errors
            fi
                exit
                ;;
        no-errors )
            list_no-errors
            exit
            ;;
        archive )
            list_archivable
            exit
            ;;
        archive_with_errors )
            if [[ $2 != "" ]]
                then
                    list_volumes $2
            else
                list_archivable_with_errors
            fi
            exit
            ;;
        volumes )
            list_volumes "$2"
            exit
            ;;
        -h | --help )   usage
                        exit
                        ;;
        * )             usage
                        exit 1
    esac
    shift
done


exit

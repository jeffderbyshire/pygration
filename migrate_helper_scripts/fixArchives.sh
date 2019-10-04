#!/usr/bin/env bash


for num in {05..08}
do
    path='/var/migration/2019/'${num}
    echo "${path}/${num}"
    for i in `ls ${path} |grep '\.duplicated'`
        do
            echo "Found ${path}/${i}"
            output=`echo ${i} |awk -F'.duplicated' '{print $1;}'`
            echo "Moving to ${path}/${output}.0.gz"
            mv ${path}/${i} ${path}/${output}".0.gz"
        done

    for i in `ls ${path} |grep -E '(#[0-9]+\.0\.gz)'`
        do
            echo "Found ${path}/${i}"
            output=`echo ${i} |awk -F'.0.gz' '{print $1;}'`
            vol=`cat ${path}/${i} |gunzip |head -1 |awk '{print $NF;}'`
            echo "Moving to ${path}/${output}-${vol}.0.gz"
            mv ${path}/${i} ${path}/${output}"-"${vol}".0.gz"
        done

    for i in `ls ${path} |grep -E '(#[0-9]+\-\.0\.gz)'`
        do
            echo "Found ${path}/${i}"
            output=`echo ${i} |awk -F'-.0.gz' '{print $1;}'`
            vol=`cat ${path}/${i} |gunzip |head -1 |awk '{print $NF;}'`
            echo "Moving to ${path}/${output}-${vol}.0.gz"
            mv ${path}/${i} ${path}/${output}"-"${vol}".0.gz"
        done

    for i in `ls ${path} |grep -E '(\-update\.0\.gz)'`
        do
            echo "Found ${path}/${i}"
            output=`echo ${i} |awk -F'-update.0.gz' '{print $1;}'`
            vol=`cat ${path}/${i} |gunzip |head -1 |awk '{print $NF;}'`
            echo "Moving to ${path}/${output}-${vol}.0.gz"
            mv ${path}/${i} ${path}/${output}"-"${vol}".0.gz"
        done

    for i in `ls ${path} |grep -E '(\-not\.0\.gz)'`
        do
            echo "Found ${path}/${i}"
            output=`echo ${i} |awk -F'-not.0.gz' '{print $1;}'`
            vol=`cat ${path}/${i} |gunzip |head -1 |awk '{print $NF;}'`
            echo "Moving to ${path}/${output}-${vol}.0.gz"
            mv ${path}/${i} ${path}/${output}"-"${vol}".0.gz"
        done

    for i in `ls ${path} |grep -e '-migrated'`
        do
            echo "Found ${path}/${i}"
            output=`echo ${i} |awk -F'-migrated' '{print $1;}'`
            echo "Moving to ${path}/${output}.0.gz"
            mv ${path}/${i} ${path}/${output}".0.gz"
        done

    for i in `ls ${path} |grep '\.migrated'`
        do
            echo "Found ${path}/${i}"
            output=`echo ${i} |awk -F'.migrated' '{print $1;}'`
            echo "Moving to ${path}/${output}.0.gz"
            mv ${path}/${i} ${path}/${output}".0.gz"
        done

    for i in `ls ${path} |grep -e '-migrating'`
        do
            echo "Found ${path}/${i}"
            output=`echo ${i} |awk -F'-migrating' '{print $1;}'`
            echo "Moving to ${path}/${output}.0.gz"
            mv ${path}/${i} ${path}/${output}".0.gz"
        done
done

exit
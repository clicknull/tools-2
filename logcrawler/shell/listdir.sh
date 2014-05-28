#!/bin/bash


ROOT=$1
SERVICE="/web/haproxy_access/"
TIME=`date -d "1 hour ago" +%Y%m%d%H`
TARGET_DIR=${ROOT}${SERVICE}${TIME}

OUTPUT_DIR="/var/log/logcrawler/listdir/"
OUTPUT_FILE=${OUTPUT_DIR}${TIME}

if [ ! -d ${OUTPUT_DIR} ]; then
    mkdir ${OUTPUT_DIR}
fi

ls -lhR ${TARGET_DIR} | awk '{print $9, $5, $8}' | tee ${OUTPUT_FILE}

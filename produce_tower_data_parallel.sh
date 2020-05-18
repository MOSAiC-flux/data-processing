#!/bin/bash
# set -x
# this could probably be done MUCH more gracefully, but at least it's done...
# ... run 8 days at a time (8 cpu cores) until yesterdays full day of data.
START_DATE="20191015"
END_DATE="$(date -d "february 28 2020" '+%Y%m%d')" # leg2 
LOG_DIR="./data_logs/"
echo "Creating the tower data product in parallel to speed up processing time..."
echo "... we will be running from ${START_DATE} to yesterday, ${END_DATE}"
echo "-------------------------------------------------------------------------------------"
read -p "Would you like to remove all log files in ${LOG_DIR}!? (y/n)" 
if [[ $REPLY = [yY] ]]; then
    rm ${LOG_DIR}/*
fi
TODAY=${START_DATE}
while (( 1 )); do

    TODAY_AND_ONE=$(date -d "$TODAY +1 days" '+%Y%m%d')
    TODAY_AND_TWO=$(date -d "$TODAY +2 days" '+%Y%m%d')
    TODAY_AND_THREE=$(date -d "$TODAY +3 days" '+%Y%m%d')
    TODAY_AND_FOUR=$(date -d "$TODAY +4 days" '+%Y%m%d')
    TODAY_AND_FIVE=$(date -d "$TODAY +5 days" '+%Y%m%d')
    TODAY_AND_SIX=$(date -d "$TODAY +6 days" '+%Y%m%d')
    TODAY_AND_SEVEN=$(date -d "$TODAY +7 days" '+%Y%m%d')

    echo "Currently running the 8 days that start on ${TODAY}"
    coproc python3 create_Daily_Tower_NetCDF.py -v -s ${TODAY} -e ${TODAY} > "${LOG_DIR}"/${TODAY}_create_data.log 2>&1
    if [ "${TODAY}" -eq "${END_DATE}" ]; then
        echo "Finished with the data on day ${END_DATE}"
        exit
    fi

    echo "... running ${TODAY_AND_ONE}"
    coproc python3 create_Daily_Tower_NetCDF.py -v -s ${TODAY_AND_ONE} -e ${TODAY_AND_ONE} > "${LOG_DIR}"/${TODAY_AND_ONE}_create_data.log 2>&1
    if [ "${TODAY_AND_ONE}" -eq "${END_DATE}" ]; then
        echo "Finished with the data on day ${END_DATE}"
        exit
    fi

    echo "... running ${TODAY_AND_TWO}"   
    coproc python3 create_Daily_Tower_NetCDF.py -v -s ${TODAY_AND_TWO} -e ${TODAY_AND_TWO} > "${LOG_DIR}"/${TODAY_AND_TWO}_create_data.log 2>&1
    if [ "${TODAY_AND_TWO}" -eq "${END_DATE}" ]; then
        echo "Finished with the data on day ${END_DATE}"
        exit
    fi

    echo "... running ${TODAY_AND_THREE}"
    coproc python3 create_Daily_Tower_NetCDF.py -v -s ${TODAY_AND_THREE} -e ${TODAY_AND_THREE} > "${LOG_DIR}"/${TODAY_AND_THREE}_create_data.log 2>&1
    if [ "${TODAY_AND_THREE}" -eq "${END_DATE}" ]; then
        echo "Finished with the data on day ${END_DATE}"
        exit
    fi

    echo "... running ${TODAY_AND_FOUR}"
    coproc python3 create_Daily_Tower_NetCDF.py -v -s ${TODAY_AND_FOUR} -e ${TODAY_AND_FOUR} > "${LOG_DIR}"/${TODAY_AND_FOUR}_create_data.log 2>&1
    if [ "${TODAY_AND_FOUR}" -eq "${END_DATE}" ]; then
        echo "Finished with the data on day ${END_DATE}"
        exit
    fi

    echo "... running ${TODAY_AND_FIVE}"
    coproc python3 create_Daily_Tower_NetCDF.py -v -s ${TODAY_AND_FIVE} -e ${TODAY_AND_FIVE} > "${LOG_DIR}"/${TODAY_AND_FIVE}_create_data.log 2>&1
    if [ "${TODAY_AND_FIVE}" -eq "${END_DATE}" ]; then
        echo "Finished with the data on day ${END_DATE}"
        exit
    fi

    echo "... running ${TODAY_AND_SIX}"
    coproc python3 create_Daily_Tower_NetCDF.py -v -s ${TODAY_AND_SIX} -e ${TODAY_AND_SIX} > "${LOG_DIR}"/${TODAY_AND_SIX}_create_data.log 2>&1
    if [ "${TODAY_AND_SIX}" -eq "${END_DATE}" ]; then
        echo "Finished with the data on day ${END_DATE}"
        exit
    fi

    echo "... running ${TODAY_AND_SEVEN}"
    python3 create_Daily_Tower_NetCDF.py -v -s ${TODAY_AND_SEVEN} -e ${TODAY_AND_SEVEN} | tee "${LOG_DIR}"/${TODAY_AND_SEVEN}_create_data.log  
    if [ "${TODAY_AND_SEVEN}" -eq "${END_DATE}" ]; then
        echo "Finished with the data on day ${END_DATE}"
        exit
    fi
    
    TODAY=$(date -d "$TODAY +8 days" '+%Y%m%d')

done

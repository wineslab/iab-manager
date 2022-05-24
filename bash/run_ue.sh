#!/bin/bash

# Run OAI nrUE1 in end-to-end SA mode
cd openairinterface5g/
source oaienv
cd cmake_targets/ran_build/build/

ue_id=$(ip -f inet addr show col0 | grep -Po 'inet \K[\d.]+' | cut -d '.' -f4);
#echo $ue_id
imsi_string=${ue_id:1:2}
#echo $imsi_string

# Run with PHY scope
#numactl --cpunodebind=netdev:usrp0 --membind=netdev:usrp0 ./nr-uesoftmodem --dlsch-parallel 8 -d --sa --uicc0.imsi 2089900007486 --usrp-args "addr=192.168.40.2" -E --numerology 1 -r 106 --band 78 -C 3619200000 --nokrnmod 1 --ue-txgain 0 -A 2539 --clock-source 1 --time-source 1 2>&1 | tee ../../../../mylogs/UE1-$(date +"%m%d%H%M").log

# Run without PHY scope
numactl --cpunodebind=netdev:usrp0 --membind=netdev:usrp0 ./nr-uesoftmodem --dlsch-parallel 8 --sa --uicc0.imsi 20899000074$imsi_string --usrp-args "addr=192.168.40.2" -E --numerology 1 -r 106 --band 78 -C 3619200000 --nokrnmod 1 --ue-txgain 0 -A 2539 --clock-source 1 --time-source 1 2>&1 | tee ../../../../mylogs/UE1-$(date +"%m%d%H%M").log | tee last_log

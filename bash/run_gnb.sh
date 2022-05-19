
#!/bin/bash

usage() { printf "Usage:\n -t donor: run gnb as donor \n -t iab: run gnb as iab\n" 1>&2; exit 1; }

cn_route() { python3 set_route_to_cn.py -i col0; }

col0_ip() {
col0_ip=$(ip -f inet addr show col0 | grep -Po 'inet \K[\d.]+');
sed -i "/GNB_IPV4_ADDRESS_FOR_NG_AMF/ c \        GNB_IPV4_ADDRESS_FOR_NG_AMF              = \"$col0_ip\/24\";" openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf;
sed -i "/GNB_IPV4_ADDRESS_FOR_NGU/ c \        GNB_IPV4_ADDRESS_FOR_NGU                 = \"${col0_ip}\/24\";" openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf;
}

tr0_ip() {
tr0_ip=$(ip -f inet addr show tr0 | grep -Po 'inet \K[\d.]+');
sed -i "/GNB_IPV4_ADDRESS_FOR_NG_AMF/ c \        GNB_IPV4_ADDRESS_FOR_NG_AMF              = \"$tr0_ip\/24\";" openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf;
sed -i "/GNB_IPV4_ADDRESS_FOR_NGU/ c \        GNB_IPV4_ADDRESS_FOR_NGU                 = \"${tr0_ip}\/24\";" openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf;
}

set_gnb_id() {
    gnb_id=$(ip -f inet addr show col0 | grep -Po 'inet \K[\d.]+' | cut -d '.' -f4);
    sed -i "/gNB_ID/ c \        gNB_ID                 = 0xe$gnb_id\;" openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf;

}

while getopts t: flag
do
    case "${flag}" in
        t) type=${OPTARG};;
   esac
done

case $type in
  donor)
    echo "running in donor mode";cn_route;col0_ip;;
  iab)
    echo "running in iab mode";tr0_ip;;
  *)
    usage;;
esac

set_gnb_id

# Run OAI gNB
cd openairinterface5g/
source oaienv
cd cmake_targets/ran_build/build/

numactl --cpunodebind=netdev:usrp0 --membind=netdev:usrp0  ./nr-softmodem -O ../../../targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf --sa -E --usrp-tx-thread-config 1 2>&1 | tee ../../../../mylogs/GNB-$(date +"%m%d%H%M").log

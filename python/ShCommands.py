class ShCommands:
    UNAME = 'uname'
    CAT_SNR_TYPE = 'cat /srn_type'
    PUSH_SRN_TYPE = "echo \'{}\' > /srn_type"
    START_CORE = 'cd oai-cn5g-fed/docker-compose/; ./core-network.sh start nrf spgwu'
    STOP_CORE = 'cd oai-cn5g-fed/docker-compose/; ./core-network.sh stop nrf spgwu'
    CORE_STATUS_WCL = 'docker ps | wc -l'
    SOFTMODEM_STATUS_WCL = 'pgrep softmodem | wc -l'
    START_UE_TMUX = 'tmux new-session -d -s ue_softmodem \'/root/run_ue_autoimsi.sh\''
    STOP_SOFTMODEM = 'kill $(pgrep softmodem)'
    START_DONOR_TMUX = 'tmux new-session -d -s ue_softmodem \'/root/run_gnb.sh -t donor\''
    START_DU_TMUX = 'tmux new-session -d -s ue_softmodem \'/root/run_gnb.sh -t iab\''
    CHECK_IFACE_EXISTS = 'ifconfig | grep {}'
    GET_IFACE_IP = 'ifconfig {} | grep \'inet addr:\' | cut -d: -f2| cut -d\' \' -f1'
    SINGLE_PING = 'ping -c 1 -I {} {}'

    @staticmethod
    def single_ping(bind_ip, dst_ip):
        return ShCommands.SINGLE_PING.format(bind_ip, dst_ip)

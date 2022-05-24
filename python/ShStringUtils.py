class ShCommands:
    UNAME = 'uname'
    CAT_SNR_TYPE = 'cat /snr_type'
    PUSH_SRN_TYPE = "echo \'{}\' > /srn_type"
    START_CORE = 'cd oai-cn5g-fed/docker-compose/; ./core-network.sh start nrf spgwu'
    STOP_CORE = 'cd oai-cn5g-fed/docker-compose/; ./core-network.sh stop nrf spgwu'
    CORE_STATUS_WCL = 'docker ps | wc -l'
    SOFTMODEM_STATUS_WCL = 'pgrep softmodem | wc -l'
    START_UE_TMUX = 'tmux new-session -d -s ue_softmodem \'/root/run_ue.sh\''
    STOP_SOFTMODEM = 'kill $(pgrep softmodem)'
    START_DONOR_TMUX = 'tmux new-session -d -s ue_softmodem \'/root/run_gnb.sh -t donor\''
    START_DU_TMUX = 'tmux new-session -d -s ue_softmodem \'/root/run_gnb.sh -t iab\''
    CHECK_IFACE_EXISTS = 'ifconfig | grep {}'
    GET_IFACE_IP = r"ip -f inet addr show {} | sed -En -e 's/.*inet ([0-9.]+).*/\1/p'"
    SINGLE_PING = 'ping -c 1 -I {} {}'
    START_RF_SCENARIO = 'colosseumcli rf start -c {}'
    STOP_RF_SCENARIO = 'colosseumcli rf stop'
    CHECK_UE_READY = './check_ue_ready.sh'
    ADD_IP_ROUTE = 'ip route add {} via {}'
    DOCKER_EXEC_COMMAND_SPGWU = 'docker exec oai-spgwu \'{}\''

    @staticmethod
    def single_ping(bind_ip, dst_ip):
        return ShCommands.SINGLE_PING.format(bind_ip, dst_ip)

    @staticmethod
    def start_rf_scenario(scenario_id):
        return ShCommands.START_RF_SCENARIO.format(scenario_id)

    @staticmethod
    def add_ip_route(target, nh):
        return ShCommands.ADD_IP_ROUTE.format(target, nh)


class NetIdentities:
    SPGWU = '192.168.70.134'
    DOCKER_NET = '192.168.70.128/26'
    TUN_NET = '12.1.1.0/24'
    SPGWU_TUN_EP = '12.1.1.1'
    BROAD_TR_NET = '192.168.0.0/16'
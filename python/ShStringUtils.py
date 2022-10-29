class ShCommands:
    UNAME = 'uname'
    CAT_SNR_TYPE = 'cat /snr_type'
    PUSH_SRN_TYPE = "echo \'{}\' > /srn_type"
    START_CORE = 'cd oai-cn5g-fed/docker-compose/; docker-compose -f docker-compose-mini-nrf.yaml up -d && ip route add 12.1.1.0/24 via 192.168.70.134'
    STOP_CORE = 'cd oai-cn5g-fed/docker-compose/; docker-compose -f docker-compose-mini-nrf.yaml stop'
    CORE_STATUS_WCL = 'docker ps | wc -l'
    TAIL_CORE = 'docker logs -n {} oai-amf'
    SOFTMODEM_STATUS_WCL = 'ps x | grep ran.py | grep -v grep | wc -l'
    START_UE_TMUX = 'tmux new-session -d -s ue_softmodem \'cd /root/OAI-Colosseum/ && python3.6 ran.py -t ue -p {} -c {} -f\''
    STOP_SOFTMODEM = 'kill $(pgrep softmodem)'
    START_DONOR_TMUX = 'tmux new-session -d -s ue_softmodem \'cd /root/OAI-Colosseum/ && python3.6 ran.py -t donor  -p {} -c {} -f\''
    START_DU_TMUX = 'tmux new-session -d -s ue_softmodem \'cd /root/OAI-Colosseum/ && python3.6 ran.py -t relay  -p {} -c {}  -f\''
    PULL_REPOS = 'echo "8.8.8.8" > /etc/resolv.conf && ip r a default via  && cd /root/openairinterface5g/ && git pull && cd /root/OAI-Colosseum/ && git pull && ip r d default'
    TAIL_RADIONODE = 'tail -n 10 /root/last_log'
    KILL9_SOFTMODEM = 'kill -9 $(pgrep softmodem)'
    CHECK_IFACE_EXISTS = 'ifconfig | grep {}'
    GET_IFACE_IP = r"ip -f inet addr show {} | sed -En -e 's/.*inet ([0-9.]+).*/\1/p'"
    SINGLE_PING = 'ping -c 1 -I {} {}'
    START_RF_SCENARIO = 'colosseumcli rf start -c {}'
    START_RF_SCENARIO_RADIOMAP = 'colosseumcli rf start -m {} -c {}'
    STOP_RF_SCENARIO = 'colosseumcli rf stop'
    CHECK_UE_READY = './check_ue_ready.sh'
    ADD_IP_ROUTE = 'ip route add {} via {}'
    DEL_IP_ROUTE = 'ip route del {}'
    DOCKER_EXEC_COMMAND_SPGWU = 'docker exec oai-spgwu {}'
    START_IPERF3_SERVER_TMUX = r"kill $(pgrep iperf) &> /dev/null || true; sleep '0.5'; tmux new-session -d -s iperf3server 'iperf3 -s --bind {} --json'"
    START_IPERF3_CLIENT_TMUX = r"kill $(pgrep iperf) &> /dev/null || true; sleep '0.5'; tmux new-session -d -s iperf3client 'iperf3 -c {} --bind {} {} " \
                               r"{}' "
    START_IPERF3_CLIENT = r"kill $(pgrep iperf) &> /dev/null || true; sleep '0.5'; iperf3 -c {} --bind {} {} {} --json"

    @staticmethod
    def single_ping(bind_ip, dst_ip):
        return ShCommands.SINGLE_PING.format(bind_ip, dst_ip)

    @staticmethod
    def start_rf_scenario(scenario_id, radiomap=False):
        if radiomap:
            return ShCommands.START_RF_SCENARIO_RADIOMAP.format('/root/radiomap.json', scenario_id)
        else:
            return ShCommands.START_RF_SCENARIO.format(scenario_id)

    @staticmethod
    def add_ip_route(target, nh):
        return ShCommands.ADD_IP_ROUTE.format(target, nh)

    @staticmethod
    def del_ip_route(target):
        return ShCommands.DEL_IP_ROUTE.format(target)

    @staticmethod
    def start_iperf3_server(bind_addr):
        return ShCommands.START_IPERF3_SERVER_TMUX.format(bind_addr)

    @staticmethod
    def start_iperf3_client(use_tmux, server, bind_addr, proto_bw, args):
        if use_tmux:
            return ShCommands.START_IPERF3_CLIENT_TMUX.format(
                server,
                bind_addr,
                proto_bw,
                args,
            )
        else:
            return ShCommands.START_IPERF3_CLIENT.format(
                server,
                bind_addr,
                proto_bw,
                args,
            )


class NetIdentities:
    SPGWU = '192.168.70.134'
    DOCKER_NET = '192.168.70.128/26'
    TUN_NET = '12.1.1.0/24'
    SPGWU_TUN_EP = '12.1.1.1'
    BROAD_TR_NET = '192.168.0.0/16'
    CORE_DOCKER_IP = '192.168.70.129'

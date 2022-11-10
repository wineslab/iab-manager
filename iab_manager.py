import networkx as nx
import configargparse as argparse
from pathlib import Path
from python.SRN import Srn, SrnTypes
from python.IabNet import IabNet
from python.CmdPrompt import PromptWorker
from fabric import Connection
from python.Colosseum import Colosseum


def manager_init(args, sounding):
    topology: nx.DiGraph = nx.read_graphml(args.topology)
    colosseum = Colosseum()
    local = True if Path("/core_srn").is_file() else False
    gw_conn = None
    if not local:
        # create and test gateway connection
        print("Initializing gateway connection...")
        gw_conn = Connection(host='colosseum-gw', user=colosseum.colosseum_user)
        if gw_conn.run('uname', hide=True, warn=False).failed:
            raise Exception('Gateway connection failed')

    # parse srn from json, add gateway and test
    srn_list = colosseum.parse_snr_from_reservation(args.reservation_id, args.srn_blacklist)
    print('Testing srn connections...')
    for s_i, srn in enumerate(srn_list):
        srn.conn_gw = gw_conn
        try:
            srn.stat_srn_type()
        except Exception as e:
            print(f"Error {e} connecting to {srn}")
        if srn.type == SrnTypes.RAN:
            # Push some files to the RAN
            srn.connection.put(local='bash/conf.json', remote='/root/OAI-Colosseum/conf.json')
            srn.connection.put(local='bash/check_ue_ready.sh', remote='/root/check_ue_ready.sh')
            srn.connection.run('chmod +x /root/check_ue_ready.sh', hide=True)
        else:
            # Core
            pass

    # new iab network
    print('Assigning network roles...')
    iab_network = IabNet(srn_list)
    if sounding:
        iab_network.apply_roles_sounding(topology)
    else:
        assert(nx.is_directed(topology))
        assert(nx.is_tree(topology))
        iab_network.apply_roles(topology)
        iab_network.create_iab_nodes()

    print("Init Done")
    return iab_network


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='IAB-Manager', default_config_files=['./config.yaml'])
    parser.add_argument('-r', '--reservation_id', type=str, required=False, help="Reservation id on Colosseum")
    parser.add_argument('-t', '--topology', type=str, help="Graphml file describing the topology of the IAB node")
    parser.add_argument('-s', '--scenario', type=str, help="RF scenario id")
    parser.add_argument('-sn', '--scenario_nodes', type=str, help="RF scenario number of nodes")
    parser.add_argument('-b', '--srn_blacklist', type=int, action='append', help="list of blacklisted srn")
    args = parser.parse_args()

    iab_net = manager_init(args, sounding=True)
    PromptWorker(iab_net).do_rf_scenario("stop")
    PromptWorker(iab_net).do_rf_scenario(f'start {args.scenario} {args.scenario_nodes}')
    # iab_net.core.start()
    # for d in iab_net.donor_list:
    #     d.start()  # 23
    # print(f'DUs: {iab_net.du_list}')
    # print(f'MTs: {iab_net.mt_list}')
    # iab_net.add_iab_node(iab_net.get_mt_by_id(24), iab_net.get_du_by_id(28))
    # n1 = iab_net.get_iab_by_id(2428)
    # n1.set_parent(iab_net.donor)

    # PromptWorker(iab_net).do_donor("start")
    # PromptWorker(iab_net).do_iab_node("add 28 24")
    # PromptWorker(iab_net).do_iab_node("set 2428 parent donor")
    # PromptWorker(iab_net).do_iab_node("start 2428")
    # PromptWorker(iab_net).do_iab_node("add 30 29")
    # PromptWorker(iab_net).do_iab_node("set 2930 parent node 2428")
    # PromptWorker(iab_net).do_test('tp down core donor')
    PromptWorker(iab_net).cmdloop()

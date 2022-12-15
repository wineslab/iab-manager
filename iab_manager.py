import networkx as nx
import configargparse as argparse
from pathlib import Path
from python.SRN import SrnTypes
from python.IabNet import IabNet
from python.CmdPrompt import PromptWorker
from fabric import Connection
from python.Colosseum import Colosseum
import time


def manager_init(args, sounding):
    topology: nx.DiGraph = nx.read_graphml(f'topologies/{args.topology}')
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
        print(srn)
        srn.conn_gw = gw_conn
        try:
            srn.stat_srn_type()
        except Exception as e:
            print(f"Error {e} connecting to {srn}")
        if srn.type == SrnTypes.RAN:
            pass
            # Push some files to the RAN
            print("Not updating local files, check that Image on colosseum is updated!")
            # srn.connection.put(local='misc/conf.json', remote='/root/OAI-Colosseum/conf.json')
            # srn.connection.put(local='misc/base.conf', remote='/root/OAI-Colosseum/oai-confs/base.conf')
            # srn.connection.put(local='misc/server.py', remote='/root/openairinterface5g/openair3/O1/o1_proto/server.py')
            #srn.connection.put(local='bash/check_ue_ready.sh', remote='/root/check_ue_ready.sh')
            # srn.connection.run('chmod +x /root/check_ue_ready.sh', hide=True)
        else:
            # Core
            pass

    # new iab network
    print('Assigning network roles...')
    iab_network = IabNet(srn_list)
    iab_network.topo_name = args.topology.split('.')[0]
    assert(nx.is_directed(topology))
    assert(nx.is_forest(topology))
    iab_network.apply_roles(topology, args.if_freqs)
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
    parser.add_argument('--results_folder', type=str, required=True)
    parser.add_argument('--if_freqs', type=int, required=True)
    args = parser.parse_args()

    iab_net = manager_init(args)
    #PromptWorker(iab_net,  args.results_folder).do_rf_scenario("stop")
    #time.sleep(5)
    #PromptWorker(iab_net,  args.results_folder).do_rf_scenario(f'start {args.scenario} {args.scenario_nodes}')
    iab_net.core.start()

    PromptWorker(iab_net, args.results_folder).cmdloop()

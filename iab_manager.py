# This is an iab network manager


import networkx as nx
import configargparse as argparse
from dotenv import load_dotenv
from pathlib import Path
from python.SRN import Srn, SrnTypes
from python.IabNet import IabNet
from python.CmdPrompt import PromptWorker
from fabric import Connection
from typing import List
import os
import requests
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

COLOSSEUM_USER = os.getenv('COLOSSEUM_USER')
COLOSSEUM_PWD = os.getenv('COLOSSEUM_PWD')


def login_colosseum():
    json_data = {
        'username': COLOSSEUM_USER,
        'password': COLOSSEUM_PWD,
    }
    response = requests.post('https://experiments.colosseum.net/api/v1/auth/login/',  json=json_data,  verify=False)
    if response.status_code != 200:
        raise Exception("Error logging in")
    for c in response.cookies:
        if c.name == 'sessionid':
            return c.value
    raise Exception("No cookie found")


def get_reservation(session_id, reservation_id):
    cookies = {
        'sessionid': session_id,
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
    }

    response = requests.get(f'https://experiments.colosseum.net/api/v1/reservations/{reservation_id}/', cookies=cookies, headers=headers, verify=False)
    if response.status_code != 200:
        raise Exception("Error getting reservation")
    return response.json()


def parse_snr_from_reservation(reservation_id: str, blacklist: list[int]) -> List[Srn]:
    session = login_colosseum()
    data = get_reservation(session, reservation_id)[0]
    snr_list = []
    for node in data['nodes']:
        nid = node['srn_id']
        if nid not in blacklist:
            hn = data['team_name'] + '-' + ('00' if nid <= 9 else '0' if nid <= 99 else '') + str(nid)
            snr_list.append(Srn(hostname=hn, id=node['srn_id']))
    snr_list.sort(key=lambda x: x.id)
    return snr_list


def manager_init(args, sounding):
    topology: nx.DiGraph = nx.read_graphml(args.topology)

    local = True if Path("/core_srn").is_file() else False
    gw_conn = None
    if not local:
        # create and test gateway connection
        print("Initializing gateway connection...")
        gw_conn = Connection(host='colosseum-gw', user=COLOSSEUM_USER)
        if gw_conn.run('uname', hide=True, warn=False).failed:
            raise Exception('Gateway connection failed')

    # parse srn from json, add gateway and test
    srn_list = parse_snr_from_reservation(args.reservation_id, args.srn_blacklist)
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
    parser.add_argument('-r', '--reservation_id', type=str, required=True, help="Reservation id on Colosseum")
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

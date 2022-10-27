# This is an iab network manager


from pathlib import Path
from python.SRN import Srn, SrnTypes
from python.IabNet import IabNet
from python.CmdPrompt import PromptWorker
from fabric import Connection
import os
import requests
from dotenv import load_dotenv
import argparse
import networkx as nx

load_dotenv()

COLOSSEUM_USER = os.getenv('COLOSSEUM_USER')
COLOSSEUM_PWD = os.getenv('COLOSSEUM_PWD')


def login_colosseum():
    json_data = {
        'username': COLOSSEUM_USER,
        'password': COLOSSEUM_PWD,
    }
    print(json_data)
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


def parse_snr_from_reservation(reservation_id: str):
    session = login_colosseum()
    data = get_reservation(session, reservation_id)[0]
    snr_list = []
    for node in data['nodes']:
        nid = node['srn_id']
        hn = data['team_name'] + '-' + ('00' if nid <= 9 else '0' if nid <= 99 else '') + str(nid)
        snr_list.append(Srn(hostname=hn, id=node['srn_id']))
    snr_list.sort(key=lambda x: x.id)
    return snr_list


def scan_subnet(entry_point: Connection, col0_prefix: str, **kwargs):
    id_range = kwargs.get('id_range', range(1, 100))
    use_arp = kwargs.get('use_arp', False)
    snr_list = []
    for host in id_range:
        if use_arp:
            if entry_point.run("arpsend -D -e {} col0 -c 1".format(col0_prefix + str(host)), warn=True,
                               hide=True).exited == 3:
                snr_list.append(host)
        else:
            if entry_point.run("ping -c 1 " + col0_prefix + str(host), hide=True):
                snr_list.append(host)


def get_snr_fromlist(snr_list: list, col0_prefix: str, **kwargs):
    c_gw = kwargs.get('conn_gw', False)
    for host in snr_list:
        print("SRN found at " + col0_prefix + str(host))
        s = Srn(ip=(col0_prefix + str(host)), id=str(host), conn_gw=c_gw)
        snr_list.append(s)

        # test ssh connection
        s.test_ssh_conn()
        print("---SSH connection established")

        # retrieve type
        s.stat_srn_type()
        print("---SRN Type: " + str(s.type))
    return snr_list


def manager_init(reservation_id: str, topology: nx.Graph):

    local = True if Path("/core_srn").is_file() else False

    if not local:
        # create and test gateway connection
        print("Initializing gateway connection...")
        gw_conn = Connection(host='colosseum-gw', user=COLOSSEUM_USER)
        if gw_conn.run('uname', hide=True, warn=False).failed:
            raise Exception('Gateway connection failed')

        # parse srn from json, add gateway and test
        srn_list = parse_snr_from_reservation(reservation_id)
        print('Testing srn connections...')
        for s_i, srn in enumerate(srn_list):
            #print(s_i, srn.hostname)
            srn.conn_gw = gw_conn
            if s_i > 1:
                srn.push_srn_type('ran')
            else:
                srn.push_srn_type('core')
            srn.stat_srn_type()
        # srn.connection.put(local='bash/run_ue.sh', remote='/root/')
        # srn.connection.run('chmod +x run_ue.sh', hide=True)
        # assert srn.test_ssh_conn()
        # print('Testing srn connections... ' + str(round((s_i/len(srn_list))*100)) + 'done', end='\r')

    # new iab network
    print('Assigning network roles...')
    iab_network = IabNet(srn_list)
    iab_network.apply_roles(topology)

    print("Init Done")
    return iab_network


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='IAB-Manager')
    parser.add_argument('-r', '--reservation', type=str, required=True)
    parser.add_argument('-t', '--topology', type=str)
    args = parser.parse_args()

    T = nx.read_graphml(args.topology)

    iab_net = manager_init(args.reservation, T)
    # for d in iab_net.donor_list:
    #     d.start()  # 23
    # print(f'DUs: {iab_net.du_list}')
    # print(f'MTs: {iab_net.mt_list}')
    # iab_net.add_iab_node(iab_net.get_mt_by_id(24), iab_net.get_du_by_id(28))
    # n1 = iab_net.get_iab_by_id(2428)
    # n1.set_parent(iab_net.donor)

    #PromptWorker(iab_net).do_rf_scenario("start 10011")
    # PromptWorker(iab_net).do_donor("start")
    # PromptWorker(iab_net).do_iab_node("add 28 24")
    # PromptWorker(iab_net).do_iab_node("set 2428 parent donor")
    # PromptWorker(iab_net).do_iab_node("start 2428")
    # PromptWorker(iab_net).do_iab_node("add 30 29")
    # PromptWorker(iab_net).do_iab_node("set 2930 parent node 2428")
    #PromptWorker(iab_net).do_test('tp down core donor')
    PromptWorker(iab_net).cmdloop()

# This is an iab network manager

# import warnings
# from cryptography.utils import CryptographyDeprecationWarning
# with warnings.catch_warnings():
#    warnings.filterwarnings('ignore', category=CryptographyDeprecationWarning)
#    import fabric
#    from paramiko import SSHConfig
# from socket import gethostbyname
import functools

from promise import Promise


from pathlib import Path
from python.SRN import Srn, SrnTypes
from python.NetElements import IabNet, NodeRoleSequences
from python.CmdPrompt import PromptWorker
from fabric import Connection
import json
import sys
import os
from dotenv import load_dotenv

load_dotenv()

COLOSSEUM_USER = os.getenv('COLOSSEUM_USER')


def parse_snr_from_reservation(filepath: str):
    with open(filepath) as f:
        data = json.load(f)
        snr_list = []
        for node in data['nodes']:
            nid = node['srn_id']
            hn = data['team_name'] + '-' + ('00' if nid <= 9 else '0' if nid <= 99 else '') + str(nid)
            snr_list.append(Srn(hostname=hn, id=node['srn_id']))
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


def manager_init():

    local = True if Path("/core_srn").is_file() else False

    if not local:

        # create and test gateway connection
        print("Initializing gateway connection...")
        gw_conn = Connection(host='colosseum-gw', user=COLOSSEUM_USER)
        if gw_conn.run('uname', hide=True, warn=False).failed:
            raise Exception('Gateway connection failed')

        # parse srn from json, add gateway and test
        srn_list = parse_snr_from_reservation('reservations_data/reservation_126148.json')
        print('Testing srn connections...')
        for s_i, srn in enumerate(srn_list):
            # print(s_i)
            srn.conn_gw = gw_conn
            # if s_i > 1:
            #     srn.push_srn_type('ran')
            # else:
            #     srn.push_srn_type('core')
            srn.stat_srn_type()
            # srn.connection.put(local='bash/run_ue.sh', remote='/root/')
            # srn.connection.run('chmod +x run_ue.sh', hide=True)
            # assert srn.test_ssh_conn()
            # print('Testing srn connections... ' + str(round((s_i/len(srn_list))*100)) + 'done', end='\r')

    # gw_conn = Connection(host='colosseum-gw', user='eugeniomoro')
    # ep_conn = Connection(host='wineslab-001', user='root', gateway=gw_conn, connect_kwargs={"password": "pass"})
    # # get srn ip and id
    # get_snr_id_cmd = "ip -f inet addr show col0 | grep -Po 'inet \K[\d.]+'"
    # col0_self_ip = ep_conn.run(get_snr_id_cmd, hide=True).stdout.strip()
    # octects = col0_self_ip.split(".")
    # self_id = octects[-1]
    # col0_prefix = octects[0] + "." + octects[1] + "." + octects[2] + "."
    #
    # srn_list = parse_reservation('reservation_126023.json')
    # srn_list = get_snr_fromlist(srn_list, col0_prefix, conn_gw=gw_conn)

    # new iab network
    print('Assigning network roles...')
    iab_network = IabNet(srn_list)
    iab_network.apply_roles(NodeRoleSequences.DEFAULT_11_SRN_SEQUENCE)
    # iab_network.apply_roles(NodeRoleSequences.DEFAULT_5_SRN_SEQUENCE)

    print("Init Done")
    return iab_network


if __name__ == '__main__':
    iab_net = manager_init()
    #PromptWorker(iab_net).do_iab_node("add 5 4")
    #PromptWorker(iab_net).do_iab_node("set 45 parent donor")
    #PromptWorker(iab_net).do_iab_node("start 45")
    #PromptWorker(iab_net).do_test('tp down core donor')
    PromptWorker(iab_net).cmdloop()

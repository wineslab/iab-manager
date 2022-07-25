# This is a modified version of the IAB manager exploiting the SRN class to launch ns-3 campaign
import argparse

from python.SRN import Srn
from fabric import Connection
import json


def parse_srn_from_reservation(filepath: str):
    with open(filepath) as f:
        data = json.load(f)
        snr_list = []
        for node in data['nodes']:
            nid = node['srn_id']
            hn = data['team_name'] + '-' + ('00' if nid <= 9 else '0' if nid <= 99 else '') + str(nid)
            snr_list.append(Srn(hostname=hn, id=node['srn_id']))
        return snr_list


def main():
    #######################
    # Parse data #
    #######################
    parser = argparse.ArgumentParser(description="Provide Colosseum username and path to JSON reservation")
    parser.add_argument('user', type=str, nargs='?', help='Colosseum username that needs to access to the SRNs')
    parser.add_argument('reservation_path', type=int, nargs='?', help='Path to JSON reservation')

    args = parser.parse_args()

    if args.user:
        user = args.user
    else:
        user = 'alacava'

    if args.reservation_path:
        reservation_path = args.reservation_path
    else:
        reservation_path = 'C:\\Users\\Andrea\\Downloads\\reservation_127988.json'

    print(f"Username: {user}")
    print(f"Reservation path: {reservation_path}")

    # Create and test gateway connection
    print("Initializing gateway connection... ", end='')
    gw_conn = Connection(host='colosseum-gw', user=user)
    if gw_conn.run('uname', hide=True, warn=False).failed:
        raise Exception('Gateway connection failed')
    else:
        print("Done")

    # Parse srn from json, add gateway and test
    srn_list = parse_srn_from_reservation(reservation_path)
    print('Launching SRNs')
    for s_i, srn in enumerate(srn_list):
        print(f'[{s_i}] Starting SRN... ', end='')
        srn.conn_gw = gw_conn
        start_sem_command = "tmux new-session -d 'cd oran-campaign; ./launch_sims.sh ; bash -i'"  # this must be changed
        res = srn.run_command(start_sem_command)
        if res:
            print("Done")
        else:
            print("Failed")

    print("Campaign launched")


if __name__ == '__main__':
    main()

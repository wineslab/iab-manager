from dotenv import load_dotenv
import os
from python.SRN import Srn
from typing import List
import requests
from pprint import pprint
import time
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


load_dotenv()
COLOSSEUM_USER = os.getenv('COLOSSEUM_USER')
COLOSSEUM_PWD = os.getenv('COLOSSEUM_PWD')
COLOSSEUM_URL = 'https://experiments.colosseum.net'


class Colosseum():
    def __init__(self):
        self.colosseum_user = COLOSSEUM_USER
        self.colosseum_pwd = COLOSSEUM_PWD
        json_data = {
            'username': self.colosseum_user,
            'password': self.colosseum_pwd,
        }
        response = requests.post(f'{COLOSSEUM_URL}/api/v1/auth/login/',  json=json_data,  verify=False)
        if response.status_code != 200:
            raise Exception("Error logging in")
        self.sessionid = None
        for c in response.cookies:
            if c.name == 'sessionid':
                self.sessionid = c.value
        if not self.sessionid:
            raise Exception("No cookie found")
        self.cookies = {
            'sessionid': self.sessionid,
        }
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
        }

    def get_myreservations(self):
        params = {
            'start_time': int(time.time())-14*24*3600,
            'stop_time': int(time.time())+7*24*3600,
        }
        reservations = []

        response = requests.get(f'{COLOSSEUM_URL}/api/v1/reservations/',
                                params=params,
                                cookies=self.cookies,
                                headers=self.headers,
                                verify=False)
        for r in response.json():
            if r['competitor_id'] == COLOSSEUM_USER and r['res_status'] not in ('Complete', 'Future'):
                reservations.append({'res_id': r['res_id'],
                                     'res_status': r['res_status'],
                                     'start': r['start'],
                                     'end': r['end']})
        return reservations

    def get_reservation(self, reservation_id):
        if not reservation_id:
            reservations = self.get_myreservations()
            if len(reservations) > 1:
                print("More than one active reservation, pleace specify manually")
                return
            elif len(reservations) == 0:
                print("No active reservation")
                return
            else:
                reservation_id = reservations[0]['res_id']
                print(f"Automatically selected reservation {reservation_id}")
        response = requests.get(
            f'{COLOSSEUM_URL}/api/v1/reservations/{reservation_id}/',
            cookies=self.cookies,
            headers=self.headers,
            verify=False)
        if response.status_code != 200:
            raise Exception("Error getting reservation")
        return response.json()

    def parse_snr_from_reservation(self, reservation_id: str = '', blacklist: list[int] = []) -> List[Srn]:
        data = self.get_reservation(reservation_id)[0]
        if not data:
            return []
        snr_list = []
        for node in data['nodes']:
            nid = node['srn_id']
            if nid not in blacklist:
                hn = data['team_name'] + '-' + ('00' if nid <= 9 else '0' if nid <= 99 else '') + str(nid)
                snr_list.append(Srn(hostname=hn, id=node['srn_id']))
        snr_list.sort(key=lambda x: x.id)
        return snr_list

from __future__ import annotations
import warnings
from cryptography.utils import CryptographyDeprecationWarning

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=CryptographyDeprecationWarning)
    import fabric

from python.NetRoles import NetRoles
import string

from invoke import exceptions as invoke_exc

from python.ShStringUtils import ShCommands


class Srn:
    net_role: NetRoles
    connected: bool
    connection: fabric.Connection
    conn_gw: fabric.Connection
    hostname: str
    col0_ip: str
    tr0_ip: str
    is_manager_host: bool

    def __init__(self, *args, **kwargs):

        self.conn_gw = kwargs.get('conn_gw', False)
        self.hostname = kwargs.get('hostname')
        self.col0_ip = kwargs.get('col0_ip')
        self.id = kwargs.get('id')
        self.is_manager_host = kwargs.get('is_manager_host', False)

        self.connection = None
        self.type = None
        self.connected = False

    def connect(self):
        if self.is_manager_host:
            # dummy local connection
            self.connection = fabric.Connection('local')
            self.connected = True
        else:
            self.connection = fabric.Connection(host=self.hostname, user='root', connect_kwargs={"password": "pass"},
                                                gateway=self.conn_gw)
            self.connected = True

    def supports_role(self, net_role):
        match net_role:
            case NetRoles.CORE:
                return True if self.type == SrnTypes.CORE else False

            case NetRoles.DU | NetRoles.DONOR | NetRoles.MT | NetRoles.UE:
                return True if self.type == SrnTypes.RAN else False

    def run_command(self, command: string):
        return self.__run_command(command, hide=True)

    def run_command_disown(self, command: string):
        return self.__run_command(command, hide=False, disown=True)

    def run_command_no_hide(self, command: string):
        return self.__run_command(command)

    def __run_command(self, command: string, **kwargs):
        if not self.connected:
            self.connect()
        try:
            if self.is_manager_host:
                res = self.connection.local(command, **kwargs)
            else:
                res = self.connection.run(command, **kwargs)
        except invoke_exc.UnexpectedExit:
            res = False
        return res

    def test_ssh_conn(self):
        return self.run_command(ShCommands.UNAME)

    def stat_srn_type(self):
        res = self.run_command(ShCommands.CAT_SNR_TYPE)
        if not res:
            raise Exception('Snr type description file not found')
        match res.stdout.strip():
            case 'core':
                self.type = SrnTypes.CORE
            case 'ran':
                self.type = SrnTypes.RAN
            case _:
                raise Exception('Unrecognized snr type')

    def push_srn_type(self, s_type: str):
        self.run_command(ShCommands.PUSH_SRN_TYPE.format(s_type))

    def get_tun_ep(self):
        if self.iface_exists('oaitun_ue1'):
            res = self.run_command(ShCommands.GET_IFACE_IP.format('oaitun_ue1'))
            if res:
                return res.stdout.strip()
        return False

    def get_tr0_ip(self):
        if self.iface_exists('tr0'):
            res = self.run_command(ShCommands.GET_IFACE_IP.format('tr0'))
            if res:
                return res.stdout.strip()
        return False

    def iface_exists(self, iface: str):
        res = self.run_command(ShCommands.CHECK_IFACE_EXISTS.format(iface))
        if res:
            return res.exited == 0

    def add_ip_route(self, target, nh):
        res = self.run_command(ShCommands.add_ip_route(target, nh))
        if not res:
            return False
        return True

    def get_col0_ip(self):
        if self.iface_exists('col0'):
            res = self.run_command(ShCommands.GET_IFACE_IP.format('col0'))
            if res:
                return res.stdout.strip()
        return False

class SrnTypes:
    CORE = 0
    RAN = 1

from __future__ import annotations
import warnings
from cryptography.utils import CryptographyDeprecationWarning

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=CryptographyDeprecationWarning)
    import fabric

from NetElements import NetRoles
import string

from invoke import exceptions as invoke_exc

from ShCommands import ShCommands


class Srn:
    net_role: NetRoles
    connected: bool
    connection: fabric.Connection
    conn_gw: fabric.Connection

    def __init__(self, *args, **kwargs):
        self.local = kwargs.get('local')
        self.ip = kwargs.get('ip', None)
        self.id = kwargs.get('id', None)
        self.conn_gw = kwargs.get('conn_gw',False)
        if id is None:
            self.name = None
        else:
            self.name = "wineslab-0" + str(self.id)
        self.connection = None
        self.type = None
        self.connected = False
        self.overriding_conn = kwargs.get('overriding_conn', None)
        if self.overriding_conn is not None:
            self.connection = self.overriding_conn

    def connect(self):
        if self.overriding_conn is None:
            self.connection = fabric.Connection(host=self.ip, user='root', connect_kwargs={"password": "pass"}, gateway=self.conn_gw)
            self.connected = True
        else:
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
            res = self.connection.run(command, **kwargs)
        except invoke_exc.UnexpectedExit:
            res = False
        return res

    def test_ssh_conn(self):
        return self.run_command(ShCommands.UNAME)

    def set_srn_type(self):
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


class SrnTypes:
    CORE = 0
    RAN = 1

from __future__ import annotations
import warnings
from cryptography.utils import CryptographyDeprecationWarning

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=CryptographyDeprecationWarning)
    import fabric

from net_config import NetRoles
import string


class Srn:
    net_role: NetRoles
    connected: bool
    connection: fabric.Connection

    def __init__(self, *args, **kwargs):
        self.local = kwargs.get('local')
        self.ip = kwargs.get('ip', None)
        self.id = kwargs.get('id', None)
        if id is None:
            self.name = None
        else:
            self.name = "wineslab-0" + str(self.id)
        self.connection = None
        self.type = None
        self.connected = False

    def connect(self):
        if not self.local:
            self.connection = fabric.Connection(host=self.ip, connect_kwargs={"password": "pass"})
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
        if not self.connected:
            self.connect()
        return self.connection.run(command, hide=True)

    def test_ssh_conn(self):
        return self.run_command(ShCommands.UNAME)

    def set_srn_type(self):
        match self.run_command(ShCommands.CAT_SNR_TYPE).stdout.strip():
            case 'core':
                self.type = SrnTypes.CORE
            case 'ran':
                self.type = SrnTypes.RAN
            case _:
                raise Exception('Unrecognized snr type')


class SrnTypes:
    CORE = 0
    RAN = 1


class ShCommands:
    UNAME = 'uname'
    CAT_SNR_TYPE = 'cat /snr_type'

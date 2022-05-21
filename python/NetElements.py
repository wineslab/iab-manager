from __future__ import annotations
from python.SRN import Srn
from typing import List
from python.ShCommands import ShCommands


class IabNet:
    snr_list: List[Srn]
    core: Core
    donor: Donor
    du_list: List[Du]
    mt_list: List[Mt]
    ue_list: List[Ue]
    iab_list: List[IabNode]

    def __init__(self, snr_list: list[Srn]):
        self.snr_list = snr_list
        self.du_list = []
        self.mt_list = []
        self.ue_list = []
        self.core = Core(snr_list[0])
        self.iab_list = []

    def apply_roles(self, node_role_sequence):
        # check if enough snr
        if len(node_role_sequence) != len(self.snr_list):
            raise NetRoleMappingFailed("Role sequence list longer than available snrs")
        for seq, role in enumerate(node_role_sequence):
            # check if snr supports role
            if self.snr_list[seq].supports_role(role):
                # role is supported, so create new NetElem accordingly
                match role:
                    case NetRoles.DONOR:
                        self.donor = Donor(self.snr_list[seq])
                    case NetRoles.MT:
                        self.mt_list.append(Mt(self.snr_list[seq]))
                    case NetRoles.DU:
                        self.du_list.append(Du(self.snr_list[seq]))
                    case NetRoles.UE:
                        self.ue_list.append(Ue(self.snr_list[seq]))
                # save role in srn
                self.snr_list[seq].net_role = role
            else:
                raise NetRoleMappingFailed

    @staticmethod
    def __netel_list_tostring(lst: List[NetElem]):
        st = ""
        for net_el in lst:
            st = st + net_el.tostring() + '\n'
        return st

    def mt_list_tostring(self):
        return self.__netel_list_tostring(self.mt_list)

    def du_list_tostring(self):
        return self.__netel_list_tostring(self.du_list)

    def ue_list_tostring(self):
        return self.__netel_list_tostring(self.ue_list)

    def iab_node_list_tostring(self):
        if len(self.iab_list) == 0:
            return "Empty"
        else:
            return self.__netel_list_tostring(self.iab_list)

    def __get_netel_by_id(self, net_id, lst: List[NetElem]):
        for net_el in lst:
            if net_el.srn.id == net_id:
                return net_el
        raise NetElNotFoundException

    def get_mt_by_id(self, nid):
        return self.__get_netel_by_id(nid, self.mt_list)

    def get_du_by_id(self, nid):
        return self.__get_netel_by_id(nid, self.du_list)

    def get_ue_by_id(self, nid):
        return self.__get_netel_by_id(nid, self.ue_list)

    def add_iab_node(self, mt, du):
        if mt.iab_node is None and du.iab_node is None:
            new_node = IabNode(du, mt)
            self.iab_list.append(new_node)
            mt.iab_node = new_node
            du.iab_node = new_node
            return True
        else:
            return False


class NetElem:
    srn: Srn
    start_cmd: str
    stop_cmd: str
    status_cmd: str

    def __init__(self, srn, **kwargs):
        self.srn = srn

    def set_commands(self, **kwargs):
        self.stop_cmd = kwargs.get('stop_cmd')
        self.start_cmd = kwargs.get('start_cmd')
        self.status_cmd = kwargs.get('status_cmd')

    def start(self):
        return self.srn.run_command(self.start_cmd)

    def start_disown(self):
        return self.srn.run_command_disown(self.start_cmd)

    def stop(self):
        return self.srn.run_command(self.stop_cmd)

    def stop_disown(self):
        return self.srn.run_command_disown(self.stop_cmd)

    def status(self):
        return self.srn.run_command(self.status_cmd)

    def tostring(self):
        return "{} id {}".format(self.__class__.__name__, str(self.srn.id))

    def iface_exists(self, iface: str):
        res = self.srn.run_command(ShCommands.CHECK_IFACE_EXISTS.format(iface))
        if res:
            return res.exited == 0

    def get_tun_ep(self):
        if self.iface_exists('oaitun_ue1'):
            res = self.srn.run_command(ShCommands.GET_IFACE_IP.format('oaitun_ue1'))
            if res:
                return res.stdout.strip()
        return False

    def get_tr0_ip(self):
        if self.iface_exists('tr0'):
            res = self.srn.run_command(ShCommands.GET_IFACE_IP.format('tr0'))
            if res:
                return res.stdout.strip()
        return False


class Du(NetElem):
    start_cmd = ShCommands.START_DU_TMUX
    stop_cmd = ShCommands.STOP_SOFTMODEM
    status_cmd = ShCommands.SOFTMODEM_STATUS_WCL
    iab_node: IabNode = None

    def __init__(self, srn):
        super().__init__(srn)
        self.mt = None

    def status(self):
        res = super().status()
        if res:
            return int(res.stdout.strip()) >= 1

    def tostring(self):
        st = super().tostring()
        if self.iab_node is not None:
            return st + "\n Part of iab_node {}".format(self.iab_node.id)
        else:
            return st


class Mt(NetElem):
    start_cmd = ShCommands.START_UE_TMUX
    stop_cmd = ShCommands.STOP_SOFTMODEM
    status_cmd = ShCommands.SOFTMODEM_STATUS_WCL
    iab_node = None

    def __init__(self, srn):
        self.du = None
        super().__init__(srn)

    def status(self):
        res = super().status()
        if res:
            return int(res.stdout.strip()) >= 1

    def tostring(self):
        st = super().tostring()
        if self.iab_node is not None:
            return st + "\n Part of iab_node {}".format(self.iab_node.id)
        else:
            return st


class Ue(NetElem):
    start_cmd = ShCommands.START_UE_TMUX
    stop_cmd = ShCommands.STOP_SOFTMODEM
    status_cmd = ShCommands.SOFTMODEM_STATUS_WCL

    def __init__(self, srn):
        self.associated_bs = None
        super().__init__(srn)

    def status(self):
        res = super().status()
        if res:
            return int(res.stdout.strip()) >= 1


class Core(NetElem):
    start_cmd = ShCommands.START_CORE
    stop_cmd = ShCommands.STOP_CORE
    status_cmd = ShCommands.CORE_STATUS_WCL

    def __int__(self, srn):
        super().__init__(srn)

    def status(self):
        res = super().status()
        if res:
            return res.stdout.strip() == '6'

    def start(self):
        return self.srn.run_command_no_hide(self.start_cmd)


class IabNode:
    parent: IabNode = None  # or donor
    children_list: List[IabNode]

    def __init__(self, du: Du, mt: Mt):
        self.du = du
        self.mt = mt
        self.id = str(mt.srn.id) + str(du.srn.id)

    def set_parent(self, parent):
        self.parent = parent

    def add_child(self, child):
        self.children_list.append(child)

    def del_child(self, child):
        self.children_list.remove(child)

    def tostring(self):
        st = "IAB Node id {} - Mt id {} - Du id {}".format(self.id, self.mt.srn.id, self.du.srn.id)
        return st

class Donor(NetElem):
    start_cmd = ShCommands.START_DONOR_TMUX
    stop_cmd = ShCommands.STOP_SOFTMODEM
    status_cmd = ShCommands.SOFTMODEM_STATUS_WCL

    children_list: List[IabNode]

    def __init__(self, srn):
        super().__init__(srn)

    def status(self):
        res = super().status()
        if res:
            return int(res.stdout.strip()) >= 1

class NetRoles:
    CORE = 0
    DU = 1
    MT = 2
    UE = 3
    DONOR = 4


class NodeRoleSequences:
    DEFAULT_11_SRN_SEQUENCE = [
        NetRoles.CORE,
        NetRoles.DONOR,
        NetRoles.MT,
        NetRoles.DU,
        NetRoles.MT,
        NetRoles.DU,
        NetRoles.MT,
        NetRoles.DU,
        NetRoles.UE,
        NetRoles.UE,
        NetRoles.UE
    ]
    DEFAULT_5_SRN_SEQUENCE = [
        NetRoles.CORE,
        NetRoles.DONOR,
        NetRoles.MT,
        NetRoles.MT,
        NetRoles.MT,
    ]


class NetElNotFoundException(Exception):
    pass


class NetRoleMappingFailed(Exception):
    pass

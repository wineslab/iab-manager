from __future__ import annotations
from re import I
from python.SRN import Srn, SrnIfaces
from typing import List
from python.ShStringUtils import ShCommands, NetIdentities
from python.NetRoles import NetRoles


class NetElem:
    srn: Srn
    start_cmd: str
    stop_cmd: str
    status_cmd: str
    iperf_bind_iface: str

    def __init__(self, srn, **kwargs):
        self.srn = srn
        self.id = srn.id

    def __eq__(self, other):
        if isinstance(other, NetElem):
            return self.id == other.id
        elif isinstance(other, int):
            return int(self.id) == other
        elif isinstance(other, str):
            return str(self.id) == other
        else:
            return NotImplemented

    def __str__(self):
        return "{} id {}".format(self.__class__.__name__, str(self.srn.id))

    def __repr__(self):
        return str(self)

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

    def check_softmodem_ready(self):
        return self.srn.run_command_no_hide(ShCommands.CHECK_UE_READY)

    def start_iperf_server(self):
        return self.srn.start_iperf_server_iface(self.iperf_bind_iface)

    def start_iperf_client(self, use_tmux, server_addr, **kwargs):
        return self.srn.start_iperf_client_iface(use_tmux, server_addr, self.iperf_bind_iface, **kwargs)


class Du(NetElem):
    start_cmd = ShCommands.START_DU_TMUX
    stop_cmd = ShCommands.STOP_SOFTMODEM
    status_cmd = ShCommands.SOFTMODEM_STATUS_WCL
    iab_node: IabNode = None
    iperf_bind_iface = SrnIfaces.TR

    def __init__(self, srn):
        super().__init__(srn)
        self.mt = None

    def status(self):
        res = super().status()
        if res:
            return int(res.stdout.strip()) >= 1


class Mt(NetElem):
    start_cmd = ShCommands.START_UE_TMUX
    stop_cmd = ShCommands.STOP_SOFTMODEM
    status_cmd = ShCommands.SOFTMODEM_STATUS_WCL
    iab_node = None
    iperf_bind_iface = SrnIfaces.UE_TUN

    def __init__(self, srn, channel=0, prb=106):
        self.du = None
        self.channel = channel
        self.prb = prb
        super().__init__(srn)

    def status(self):
        res = super().status()
        if res:
            return int(res.stdout.strip()) >= 1


class Ue(NetElem):
    start_cmd = ShCommands.START_UE_TMUX
    stop_cmd = ShCommands.STOP_SOFTMODEM
    status_cmd = ShCommands.SOFTMODEM_STATUS_WCL
    iperf_bind_iface = SrnIfaces.UE_TUN

    def __init__(self, srn, channel=0, prb=106):
        self.associated_bs = None
        self.channel = channel
        self.prb = prb
        super().__init__(srn)

    def status(self):
        res = super().status()
        if res:
            return int(res.stdout.strip()) >= 1


class Core(NetElem):
    start_cmd = ShCommands.START_CORE
    stop_cmd = ShCommands.STOP_CORE
    status_cmd = ShCommands.CORE_STATUS_WCL
    iperf_bind_iface = SrnIfaces.DOCKER_NET

    def __int__(self, srn):
        super().__init__(srn)

    def status(self):
        res = super().status()
        if res:
            return res.stdout.strip() == '6'

    def start(self):
        res = self.srn.run_command_no_hide(self.start_cmd)
        return (res and self.srn.add_ip_route(target=NetIdentities.BROAD_TR_NET,
                                              nh=NetIdentities.SPGWU))

    def add_ip_route_in_spgwu(self, target, nh):
        res = self.srn.run_command(
            ShCommands.DOCKER_EXEC_COMMAND_SPGWU.format(ShCommands.add_ip_route(target, nh)))
        if res:
            return True
        return False

    def del_ip_route_in_spgwu(self, target):
        res = self.srn.run_command(
            ShCommands.DOCKER_EXEC_COMMAND_SPGWU.format(ShCommands.del_ip_route(target)))
        if res:
            return True
        return False


class IabNode:
    parent: IabNode = None  # or donor
    children_list: List[IabNode]
    srn: Srn  # needed to reuse functions written for NetElem without inheriting NetElem itself

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return str(self)

    def __init__(self, du: Du, mt: Mt):
        self.du = du
        self.mt = mt
        self.id = str(mt.srn.id) + str(du.srn.id)
        self.srn = du.srn  # this is done by choice, it could be mt as well

    def set_parent(self, parent):
        self.parent = parent

    def add_child(self, child):
        self.children_list.append(child)

    def del_child(self, child):
        self.children_list.remove(child)

    def start(self):
        if self.mt is not None and self.du is not None:
            rt = True
            if not self.mt.status():
                rt = self.mt.start()
            if not self.du.status():
                rt = rt and self.du.start()
            return rt and self.set_internal_route()
        else:
            return False

    def set_internal_route(self):
        print("Setting internal route")
        # in mt, route to du tr0 iface
        rt = self.mt.srn.add_ip_route(
            target=self.du.srn.get_tr0_ip(), nh=self.du.srn.get_col0_ip())

        # in du, route to core through mt col0
        rt = rt and self.du.srn.add_ip_route(
            target=NetIdentities.DOCKER_NET, nh=self.mt.srn.get_col0_ip()
        )

    def stop(self):
        # stopping is easier, since the stop bash command can be safely sent even if the softmodem is not running
        if self.mt is not None:
            self.mt.stop()
        if self.du is not None:
            self.du.stop()

    def get_tun_ep(self):
        return self.mt.srn.get_tun_ep()


class Donor(NetElem):
    start_cmd = ShCommands.START_DONOR_TMUX
    stop_cmd = ShCommands.STOP_SOFTMODEM
    status_cmd = ShCommands.SOFTMODEM_STATUS_WCL
    iperf_bind_iface = SrnIfaces.TR

    children_list: List[IabNode]

    def __init__(self, srn, channel=0, prb=106):
        self.channel = channel
        self.prb = prb
        super().__init__(srn)

    def status(self):
        res = super().status()
        if res:
            return int(res.stdout.strip()) >= 1


class NetElNotFoundException(Exception):
    pass


class NetRoleMappingFailed(Exception):
    pass

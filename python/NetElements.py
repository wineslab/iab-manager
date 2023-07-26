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
        self.type = self.__class__.__name__

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
        return "{} id {}".format(self.type, str(self.srn.id))

    def __repr__(self):
        return str(self)

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

    def clean_routes(self):
        #Clean custom routes we addedd
        return self.srn.run_command_no_hide(ShCommands.CLEAN_ROUTES)


class RadioElem(NetElem):
    pullrepos_cmd = ShCommands.PULL_REPOS

    def __init__(self, srn, topo_id, radio_id, channel=0, prb=106, nonrtric_url='http://127.0.0.1', if_freqs=0):
        self.topo_id = topo_id
        self.channel = channel
        self.prb = prb
        self.radio_id = radio_id
        self.nonrtric_url = nonrtric_url
        self.if_freqs = if_freqs
        super().__init__(srn)
        self.srn.push_topo_node(self.type, self.topo_id)

    def start(self, flash=False):
        if flash:
            cmd = self.start_cmd.format(self.nonrtric_url, self.prb, self.channel, self.if_freqs, '-f')
        else:
            cmd = self.start_cmd.format(self.nonrtric_url, self.prb, self.channel, self.if_freqs, '')
        return self.srn.run_command(cmd)

    def start_disown(self):
        return self.srn.run_command_disown(self.start_cmd.format(self.nonrtric_url, self.prb, self.channel, self.if_freqs))

    def status(self):
        res = super().status()
        if res:
            return int(res.stdout.strip()) >= 1

    def tail(self):
        self.srn.run_command_no_hide(ShCommands.TAIL_RADIONODE)

    def kill(self):
        self.srn.run_command(ShCommands.KILL9_SOFTMODEM)
    
    def start_ping_bg(self):
        if isinstance(self, Ue):
            self.srn.add_ip_route(NetIdentities.DOCKER_NET, NetIdentities.SPGWU_TUN_EP)
        self.srn.run_command_disown(ShCommands.START_PING_BACKGROUND)
    
    def kill_ping_bg(self):
        self.srn.run_command(ShCommands.KILL_PING)


class Donor(RadioElem):
    start_cmd = ShCommands.START_DONOR_TMUX
    stop_cmd = ShCommands.STOP_SOFTMODEM
    status_cmd = ShCommands.SOFTMODEM_STATUS_WCL
    iperf_bind_iface = SrnIfaces.TR

    children_list: List[IabNode]  # This might be replaced by networkx topology

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)


class Du(RadioElem):
    start_cmd = ShCommands.START_DU_TMUX
    stop_cmd = ShCommands.STOP_SOFTMODEM
    status_cmd = ShCommands.SOFTMODEM_STATUS_WCL
    iab_node: IabNode = None
    iperf_bind_iface = SrnIfaces.TR
    type = "Du"

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.mt = None


class Ue(RadioElem):
    start_cmd = ShCommands.START_UE_TMUX
    stop_cmd = ShCommands.STOP_SOFTMODEM
    status_cmd = ShCommands.SOFTMODEM_STATUS_WCL
    iperf_bind_iface = SrnIfaces.UE_TUN

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)


class Mt(Ue):
    start_cmd = ShCommands.START_UE_TMUX
    stop_cmd = ShCommands.STOP_SOFTMODEM
    status_cmd = ShCommands.SOFTMODEM_STATUS_WCL
    iab_node = None
    iperf_bind_iface = SrnIfaces.UE_TUN

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.du = None


class Sounder(Ue):
    '''Net element that enables the scan mode of a ue, which do channel hopping and report the available gNBs'''
    start_cmd = ShCommands.START_SOUNDER_TMUX
    stop_cmd = ShCommands.STOP_SOUNDER
    status_cmd = ShCommands.SOFTMODEM_STATUS_WCL

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

    def start(self):
        if flash:
            return self.srn.run_command(self.start_cmd.format(self.nonrtric_url, self.prb))

    def start_disown(self):
        return self.srn.run_command_disown(self.start_cmd.format(self.nonrtric_url, self.prb))

    def status(self):
        return 0  # To implement

    def tail(self):
        self.srn.run_command_no_hide(ShCommands.TAIL_RADIONODE)

    def kill(self):
        self.srn.run_command(ShCommands.STOP_SOUNDER)


class Core(NetElem):
    start_cmd = ShCommands.START_CORE
    stop_cmd = ShCommands.STOP_CORE
    status_cmd = ShCommands.CORE_STATUS_WCL
    iperf_bind_iface = SrnIfaces.DOCKER_NET

    def __init__(self, srn):
        super().__init__(srn)

    def status(self):
        res = super().status()
        if res:
            return res.stdout.strip() == '6'

    def start(self):
        res = self.srn.run_command_no_hide(self.start_cmd)
        return (res and self.srn.add_ip_route(target=NetIdentities.BROAD_TR_NET,
                                              nh=NetIdentities.SPGWU))

    def restart(self):
        res = self.srn.run_command_no_hide(ShCommands.RESTART_CORE)
        return (res and self.srn.add_ip_route(target=NetIdentities.BROAD_TR_NET,
                                              nh=NetIdentities.SPGWU))

    def tail(self, lines=10):
        self.srn.run_command_no_hide(ShCommands.TAIL_CORE.format(lines))

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
        self.srn = du.srn  # this is done by choice, it could be mt as well #G: Do we need it anywhere? we always use self.du.srn or self.mt.srn

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


class NetElNotFoundException(Exception):
    pass


class NetRoleMappingFailed(Exception):
    pass

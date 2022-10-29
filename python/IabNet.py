from __future__ import annotations
from ast import Index
from re import I
from python.SRN import Srn, SrnIfaces
from typing import List
from python.ShStringUtils import ShCommands, NetIdentities
from python.NetRoles import NetRoles
import networkx as nx
from python.NetElements import Core, Donor, Du, Mt, Ue, IabNode, NetRoleMappingFailed, NetElem, NetElNotFoundException
import io
import json


class IabNet:
    snr_list: List[Srn]
    core: Core
    du_list: List[Du]
    mt_list: List[Mt]
    ue_list: List[Ue]
    iab_list: List[IabNode]

    def __init__(self, snr_list: list[Srn]):
        self.snr_list = snr_list
        self.du_list = []
        self.mt_list = []
        self.ue_list = []
        self.donor_list = []
        self.netelem_list = []
        # TODO: this assumes that 0 is always core. Either make it mandatory and assert or generalize
        # Where do we deploy the ric?
        self.core = Core(snr_list[0])
        self.iab_list = []

    def apply_roles(self, topology: nx.DiGraph):
        self.topology = topology
        # check if enough snr
        if len(topology) > len(self.snr_list):
            raise NetRoleMappingFailed(f"Role sequence list {len(topology)} longer than available snrs {len(self.snr_list)}")
        for seq, (n, d) in enumerate(topology.nodes(data=True)):
            # check if snr supports role
            srn = self.snr_list[seq+1]
            if self.snr_list[seq+1].supports_role(d['role']):
                netelem = None
                # role is supported, so create new NetElem accordingly
                match d['role']:
                    case NetRoles.DONOR:
                        netelem = Donor(srn, n, d['radio_id'], channel=d['channel'], prb=d['prb'])
                        self.donor_list.append(netelem)
                    case NetRoles.MT:
                        netelem = Mt(srn, n, d['radio_id'], channel=d['channel'], prb=d['prb'])
                        self.mt_list.append(netelem)
                    case NetRoles.DU:
                        netelem = Du(srn, n, d['radio_id'], channel=d['channel'], prb=d['prb'])
                        self.du_list.append(netelem)
                    case NetRoles.UE:
                        netelem = Ue(srn, n, d['radio_id'], channel=d['channel'], prb=d['prb'])
                        self.ue_list.append(netelem)
                    case default:
                        raise NetRoleMappingFailed

                # save srn in graph
                d['netelem'] = netelem
                print(srn, d['role'], n, d['radio_id'], d['channel'], d['prb'])
                d['srn'] = srn
                self.netelem_list.append(netelem)

                # save role in srn
                srn.net_role = d['role']
            else:
                raise NetRoleMappingFailed
        # kind of an outlier in this function, we need to set core to donor routes
        for donor in self.donor_list:
            self.core.srn.add_ip_route(
                target=donor.srn.get_tr0_ip(), nh=donor.srn.get_col0_ip())
            donor.srn.add_ip_route(
                target=self.core.get_tr0_ip(), nh=self.core.srn.get_col0_ip())

    def create_iab_nodes(self):
        iab_nodes = {}
        for n, d in self.topology.nodes(data=True):
            if d['role'] == NetRoles.MT:
                try:
                    iab_nodes[d['iab']]['mt'] = d['netelem']
                except KeyError:
                    iab_nodes[d['iab']] = {'mt': d['netelem']}
            elif d['role'] == NetRoles.DU:
                try:
                    iab_nodes[d['iab']]['du'] = d['netelem']
                except KeyError:
                    iab_nodes[d['iab']] = {'du': d['netelem']}
            else:
                pass
        for iab_node, val in iab_nodes.items():
            self.add_iab_node(val['mt'], val['du'])
            # TODO: Maybe add_iab_node should return the node itself
            iab_node = self.get_iab_by_id(f"{val['mt'].id}{val['du'].id}")
            nexthops = list(self.topology[val['mt'].topo_id])
            assert(len(nexthops) == 1)
            assert(self.topology[val['mt'].topo_id][nexthops[0]]['type'] == 'wireless')
            iab_node.set_parent(self.topology.nodes[nexthops[0]]['netelem'])

    def push_radiomap(self, tot_nodes):
        # Generate the radiomap based on the assigned SRN and radio_ids
        self.radiomap = {f"Node {n}": "None" for n in range(1, tot_nodes+1)}
        for n in self.netelem_list:
            self.radiomap[f"Node {n.radio_id}"] = {"SRN": n.id, "RadioA": 1, "RadioB": 2}
        json_radiomap = io.StringIO(json.dumps(self.radiomap))
        if not self.core.srn.connected:
            self.core.srn.connect()
        self.core.srn.connection.put(json_radiomap, '/root/radiomap.json')

    def __get_netel_by_id(self, net_id, lst: List[NetElem]):
        for net_el in lst:
            if net_el.id == net_id:
                return net_el
        raise NetElNotFoundException

    def get_mt_by_id(self, nid: str | int) -> Mt:
        return self.__get_netel_by_id(int(nid), self.mt_list)

    def get_du_by_id(self, nid: str | int) -> Du:
        return self.__get_netel_by_id(int(nid), self.du_list)

    def get_donor_by_id(self, nid: str | int) -> Donor:
        return self.__get_netel_by_id(int(nid), self.donor_list)

    def get_ue_by_id(self, nid: str | int) -> Ue:
        return self.__get_netel_by_id(int(nid), self.ue_list)

    def get_iab_by_id(self, iid: str | int) -> IabNode:
        return self.__get_netel_by_id(str(iid), self.iab_list)

    def add_iab_node(self, mt, du):
        if mt.iab_node is None and du.iab_node is None:
            new_node = IabNode(du, mt)
            self.iab_list.append(new_node)
            mt.iab_node = new_node
            du.iab_node = new_node
            return True
        else:
            return False

    def del_iab_node(self, iab_n: IabNode):
        iab_n.stop()
        iab_n.du.iab_node = None
        iab_n.mt.iab_node = None
        self.iab_list.remove(iab_n)

    def start_rf_scenario(self, s_id, radiomap=False):
        self.core.srn.run_command(ShCommands.start_rf_scenario(s_id, radiomap))

    def stop_rf_scenario(self):
        self.core.srn.run_command(ShCommands.STOP_RF_SCENARIO)

    def update_iabnode_route(self, node: IabNode):
        # in mt, route to oai-net through mt's tun, first delete any
        node.mt.srn.run_command(ShCommands.del_ip_route(NetIdentities.DOCKER_NET))
        node.mt.srn.add_ip_route(target=NetIdentities.DOCKER_NET,
                                 nh=node.mt.get_tun_ep())
        # in du, route through mt col0
        #node.du.srn.add_ip_route(target=NetIdentities.DOCKER_NET, nh=node.mt.get)
        node.set_internal_route()
        # in spgwu, route to du through mt's tun ip - first delete any previous route
        self.core.del_ip_route_in_spgwu(target=node.du.srn.get_tr0_ip())
        self.core.add_ip_route_in_spgwu(target=node.du.srn.get_tr0_ip(),
                                        nh=node.mt.get_tun_ep())

    def update_tree_routes(self):
        queue = []
        queue.extend(self.donor.children_list)

        while len(queue) > 0:
            node = queue.pop(0)
            if isinstance(node, IabNode):
                # first append children to queue
                queue.extend(node.children_list)
                self.update_iabnode_route(node)

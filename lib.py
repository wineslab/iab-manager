import sys
sys.path.append(__file__.rsplit("/", 1)[0])  # workaround for relative import
from python.CmdActions import IabNodeActions
from python.NetElements import IabNode
from python.Colosseum import Colosseum
from fabric import Connection
from python.IabNet import IabNet
from pathlib import Path
import networkx as nx



class Iab:
    def __init__(self, reservation_id, srn_blacklist):
        colosseum = Colosseum()
        local = True if Path("/core_srn").is_file() else False
        if not local:
            # create and test gateway connection
            print("Initializing gateway connection...")
            gw_conn = Connection(host='colosseum-gw', user=colosseum.colosseum_user)
            if gw_conn.run('uname', hide=True, warn=False).failed:
                raise Exception('Gateway connection failed')
        self.srn_list = colosseum.parse_snr_from_reservation(reservation_id, srn_blacklist)
        self.iab_network = IabNet(self.srn_list)

    def get_iab_network(self, topology_xml):
        topology = nx.parse_graphml(topology_xml)
        assert(nx.is_directed(topology))
        assert(nx.is_forest(topology))
        self.iab_network.apply_roles(topology, 1)
        self.iab_network.create_iab_nodes()

    def autostart(self):
        for netelem in self.iab_network.get_srn_startup_order():
            if type(netelem) == IabNode:
                if not IabNodeActions.start(netelem, self.iab_network):
                    return
            else:
                if not netelem.status():
                    if not netelem.start():
                        return


sys.path.append(__file__.rsplit("/", 1)[0])  # workaround for relative import


class Iab:
    def __init__(self, reservation_id, srn_blacklist):
        colosseum = Colosseum()
        local = True if Path("/core_srn").is_file() else False
        if not local:
            # create and test gateway connection
            print("Initializing gateway connection...")
            gw_conn = Connection(host='colosseum-gw', user=colosseum.colosseum_user)
            if gw_conn.run('uname', hide=True, warn=False).failed:
                raise Exception('Gateway connection failed')
        self.srn_list = colosseum.parse_snr_from_reservation(reservation_id, srn_blacklist)
        self.iab_network = IabNet(self.srn_list)

    def get_iab_network(self, topology_xml):
        topology = nx.parse_graphml(topology_xml)
        assert(nx.is_directed(topology))
        assert(nx.is_forest(topology))
        self.iab_network.apply_roles(topology, 1)
        self.iab_network.create_iab_nodes()

    def autostart(self):
        for netelem in self.iab_network.get_srn_startup_order():
            if type(netelem) == IabNode:
                if not IabNodeActions.start(netelem, self.iab_network):
                    return
            else:
                if not netelem.status():
                    if not netelem.start():
                        return

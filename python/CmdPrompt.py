from __future__ import annotations

from python.MyCmd import MyCmd

from python.CmdActions import IabNodeActions, \
    NetTestActions
from python.NetElements import NetElNotFoundException, IabNode, Core, RadioElem
from python.IabNet import IabNet
from python.NetTests import ping_test, iperf_test


class PromptWorker(MyCmd):

    iab_net: IabNet

    def __init__(self, iab_net, results_folder):
        self.iab_net = iab_net
        self.results_folder = results_folder
        super().__init__()

    def do_help(self, arg: str) -> bool | None:
        print("Todo: help page")

    def do_cleanup(self, args):
        #Kill everything in the RAN and clean all routes
        print("Cleaning up the RAN")
        ran = self.iab_net.ue_list + self.iab_net.du_list + self.iab_net.mt_list + self.iab_net.donor_list
        for n in ran:
            n.kill()
            n.clean_routes()
        
        print("Cleaning up the core")
        #restart and clean the core
        self.iab_net.core.stop()
        self.iab_net.core.clean_routes()
        self.iab_net.core.start()

    def do_core(self, args: str):
        args = args.split()
        if len(args) < 1:
            print("Usage: core ACTION")
            return
        match args[0]:
            case 'restart':
                if self.iab_net.core.status():
                    if self.iab_net.core.restart():
                        print("Done")
                    else:
                        print("Failed")
            case 'start':
                if not self.iab_net.core.status():
                    if self.iab_net.core.start():
                        print("Done")
                    else:
                        print("Failed")
            case 'stop':
                if self.iab_net.core.status():
                    if self.iab_net.core.stop():
                        print("Done")
                    else:
                        print("Failed")
            case 'status':
                if self.iab_net.core.status():
                    print("Core running")
                else:
                    print("Core not running")
            case 'stop -f':
                CoreActions.core_stop_action(self.iab_net)
            case 'clean':
                self.iab_net.core.clean_routes()
            case 'tail':
                if len(args) == 2:
                    self.iab_net.core.tail(args[1])
                if len(args) == 1:
                    self.iab_net.core.tail()
                else:
                    print("Usage: core tail [n]")
                    return

            case _:
                print("Unrecognized action")

    def do_printmap(self, args):
        print("SRN\t\tRole\tRadio\tTopo\tChannel\n")
        print(f"{self.iab_net.core.srn.hostname}\tCore\tNA\tNA\tNA")
        for n in self.iab_net.netelem_list:
            try:
                print(f"{n.srn.hostname}\t{n.type}\t{n.radio_id}\t{n.topo_id}\t{n.channel}")
            except:
                import pdb
                pdb.set_trace()

    def do_autostart(self, args):
        for netelem in self.iab_net.get_srn_startup_order():
            if type(netelem) == IabNode:
                if not IabNodeActions.start(netelem, self.iab_net):
                    return
            else:
                if not netelem.status():
                    print(f"Starting {netelem}")
                    if not netelem.start():
                        return
                else:
                    print(f"{netelem} already running")

    def do_list(self, target: str):
        match target:
            case 'donor':
                print(self.iab_net.donor_list)
            case 'mt':
                print(self.iab_net.mt_list)
            case 'du':
                print(self.iab_net.du_list)
            case 'ue':
                print(self.iab_net.ue_list)
            case 'iab_node':
                print(self.iab_net.iab_list)
            case 'sounder':
                print(self.iab_net.sounder_list)
            case _:
                print("Unrecognized action")

    def _do_generic(self, args, type):
        args = args.split()
        match type:
            case 'du':
                nodes = self.iab_net.du_list
            case 'mt':
                nodes = self.iab_net.mt_list
            case 'ue':
                nodes = self.iab_net.ue_list
            case 'donor':
                nodes = self.iab_net.donor_list
            case 'sounder':
                nodes = self.iab_net.sounder_list
            case default:
                print("Node type wrong")
                return
        if len(args) < 2:
            print(f"Usage: {type} ID | all ACTION")
            return

        if args[0] == 'all':
            # If 'all' we apply the command to all the list, else we select one
            pass
        elif args[0].isdigit():
            try:
                nodes = [self.iab_net._get_netel_by_id(int(args[0]), nodes)]
            except NetElNotFoundException:
                print(f"{type} {args[0]} not found")
                return
        else:
            print(f"Usage: {type} ID | all ACTION")
            return
        for n in nodes:
            match args[1]:
                case 'status':
                    print(f"Checking {type} {n.id} status...")
                    if n.status():
                        print(f"{type} {n.id} running")
                    else:
                        print(f"{type} {n.id} not running")
                case 'start':
                    if not n.status():
                        flash : bool = len(args)>2 and args[2] == 'flash'
                        n.start(flash=flash)
                case 'stop':
                    if n.status():
                        n.stop()
                case 'tail':
                    if n.status():
                        n.tail()
                case 'bg_ping':
                    n.start_ping_bg()
                case 'stop_ping':
                    n.kill_ping_bg()
                    res = n.srn.run_command("cat ~/results/ping.dat")
                    with open(f'{self.results_folder}/{self.iab_net.topo_name}/{n.topo_id}.rtt', 'w') as fw:
                        fw.write(res.stdout)
                case 'ping':
                    ping_test(n, f'{self.results_folder}/{self.iab_net.topo_name}')
                case 'iperf':
                    iperf_test(n, self.iab_net.core, direction=args[2], bw=args[3], out_dir=f'{self.results_folder}/{self.iab_net.topo_name}')
                case 'kill':
                    n.kill()
                    n.clean_routes()
                case 'clean':
                    n.clean_routes()
                case _:
                    print(f'Action {args[1]} not recognized')

    def do_mt(self, args: str):
        return self._do_generic(args, 'mt')

    def do_ue(self, args: str):
        return self._do_generic(args, 'ue')

    def do_sounder(self, args: str):
        return self._do_generic(args, 'sounder')

    def do_du(self, args: str):
        return self._do_generic(args, 'du')

    def do_donor(self, args: str):
        return self._do_generic(args, 'donor')

    def do_iab_node(self, args: str):
        usage_str = "Usage:\t iab_node add {{du_id} {mt_id}}\n"
        "\t\tdel | status | start | stop {iab_id}\n"
        "\t\tset {iab_id} parent  {donor | node id}"
        args = args.split()
        if len(args) < 2:
            print(usage_str)
            return
        match args[0]:
            case 'add':
                if len(args) != 3:
                    print(usage_str)
                    return
                mt_id = args[2]
                du_id = args[1]
                try:
                    du = self.iab_net.get_du_by_id(int(du_id))
                except NetElNotFoundException:
                    print("DU {} not found".format(du_id))
                    return
                try:
                    mt = self.iab_net.get_mt_by_id(int(mt_id))
                except NetElNotFoundException:
                    print("MT {} not found".format(mt_id))
                    return
                if self.iab_net.add_iab_node(mt, du):
                    print("Successfully added iab node with id {}".format(self.iab_net.iab_list[-1].id))
                else:
                    print('Add failed')
            case 'del':
                if len(args) != 2:
                    print(usage_str)
                    return
                try:
                    iab_n = self.iab_net.get_iab_by_id(args[1])
                except NetElNotFoundException:
                    print("IAB node {} not found".format(args[1]))
                    return
                self.iab_net.del_iab_node(iab_n)
                print("IAB node {} removed".format(args[1]))
            case 'status':
                if len(args) != 2:
                    print(usage_str)
                    return
                try:
                    iab_n = self.iab_net.get_iab_by_id(args[1])
                except NetElNotFoundException:
                    print("IAB node {} not found".format(args[1]))
                    return
                print(iab_n)
                if iab_n.mt is not None:
                    if iab_n.mt.status():
                        print(f"MT {iab_n.mt.id} running")
                if iab_n.du is not None:
                    if iab_n.du.status():
                        print(f"DU {iab_n.du.id} running")
            case 'start':
                if len(args) != 2:
                    print(usage_str)
                    return
                try:
                    iab_n = self.iab_net.get_iab_by_id(args[1])
                except NetElNotFoundException:
                    print("IAB node {} not found".format(args[1]))
                    return
                IabNodeActions.start(iab_n, self.iab_net)
            case 'stop':
                if len(args) != 2:
                    print(usage_str)
                    return
                try:
                    iab_n = self.iab_net.get_iab_by_id(args[1])
                except NetElNotFoundException:
                    print("IAB node {} not found".format(args[1]))
                    return
                iab_n.stop()
                print("Iab node {} stopped".format(iab_n.id))
            case 'set':
                if len(args) <= 3:
                    print(usage_str)
                    return
                try:
                    iab_n = self.iab_net.get_iab_by_id(args[1])
                except NetElNotFoundException:
                    print("IAB node {} not found".format(args[1]))
                    return
                match args[2]:
                    case 'parent':
                        match args[3]:
                            case 'node':
                                if len(args) != 5:
                                    print(usage_str)
                                    return
                                try:
                                    parent_iab_n = self.iab_net.get_iab_by_id(args[4])
                                except NetElNotFoundException:
                                    print("IAB node {} not found".format(args[4]))
                                    return
                                print("Setting IAB node {} parent as {}".format(iab_n.id, parent_iab_n.id))
                                iab_n.set_parent(parent_iab_n)
                    case _:
                        print(usage_str)
                        return
            case _:
                print(usage_str)
                return

    def do_rf_scenario(self, args: str):
        # TODO: find a way to know the number of nodes in the rf scenario
        if args == '':
            print("Usage: rf_scenario {start id n_nodes| stop}")
            return
        args = args.split()
        match args[0]:
            case 'start':
                if len(args) != 3:
                    print("Usage: rf_scenario {start id n_nodes | stop}")
                    return
                self.iab_net.push_radiomap(int(args[2]))
                self.iab_net.start_rf_scenario(args[1], True)
            case 'stop':
                self.iab_net.stop_rf_scenario()

    def do_test(self, args: str):
        # args example: connectivity down core donor
        # args example: connectivity down core mt 1
        # args example: connectivity down mt 1 core
        # args example: connectivity down mt 1 du 1
        usage_str = 'Usage: test {connectivity | latency | tp} {up | down} {core | donor | iab id | mt id | du id | ue id}x2'
        if args == '':
            print(usage_str)
            return
        args = args.split()
        if len(args) < 4:
            print(usage_str)
            return
        if args[-1] == '&':
            run_asynch = True
        else:
            run_asynch = False
        # get source and dest
        dst_arg_offset = 0
        match args[2]:  # match on source descriptor

            case 'core':
                src = self.iab_net.core
            case 'donor':
                src = self.iab_net.donor

            case 'iab':
                if len(args) < 6:
                    print(usage_str)
                    return
                try:
                    src = self.iab_net.get_iab_by_id(args[3])
                    dst_arg_offset = 1
                except NetElNotFoundException:
                    print("IAB node {} not found".format(args[3]))
                    return

            case 'mt':
                if len(args) < 5:
                    print(usage_str)
                    return
                try:
                    src = self.iab_net.get_mt_by_id(args[3])
                    dst_arg_offset = 1
                except NetElNotFoundException:
                    print("MT {} not found".format(args[3]))
                    return

            case 'du':
                if len(args) < 5:
                    print(usage_str)
                    return
                try:
                    src = self.iab_net.get_du_by_id(args[3])
                    dst_arg_offset = 1
                except NetElNotFoundException:
                    print("DU {} not found".format(args[3]))
                    return

            case 'ue':
                if len(args) < 5:
                    print(usage_str)
                    return
                try:
                    src = self.iab_net.get_ue_by_id(args[3])
                    dst_arg_offset = 1
                except NetElNotFoundException:
                    print("UE {} not found".format(args[3]))
                    return

            case _:
                print(usage_str)
                return

        match args[3+dst_arg_offset]:  # match on destination descriptor

            case 'core':
                dst = self.iab_net.core
            case 'donor':
                dst = self.iab_net.donor

            case 'iab_node':
                if len(args) < 6 - (1-dst_arg_offset):
                    print(usage_str)
                    return
                try:
                    dst = self.iab_net.get_iab_by_id(args[4+dst_arg_offset])
                except NetElNotFoundException:
                    print("IAB node {} not found".format(args[3+dst_arg_offset]))
                    return

            case 'mt':
                if len(args) < 6 - (1-dst_arg_offset):
                    print(usage_str)
                    return
                try:
                    dst = self.iab_net.get_mt_by_id(args[4+dst_arg_offset])
                except NetElNotFoundException:
                    print("MT {} not found".format(args[4+dst_arg_offset]))
                    return

            case 'du':
                if len(args) < 6 + (1-dst_arg_offset):
                    print(usage_str)
                    return
                try:
                    dst = self.iab_net.get_du_by_id(args[4+dst_arg_offset])
                except NetElNotFoundException:
                    print("DU {} not found".format(args[4+dst_arg_offset]))
                    return

            case 'ue':
                if len(args) < 6 - (1-dst_arg_offset):
                    print(usage_str)
                    return
                try:
                    dst = self.iab_net.get_ue_by_id(args[4+dst_arg_offset])
                except NetElNotFoundException:
                    print("UE {} not found".format(args[4+dst_arg_offset]))
                    return

            case _:
                print(usage_str)
                return

        # invert src dest if up
        match args[1]:
            case 'down':
                pass
            case 'up':
                src, dst = dst, src
            case _:
                print(usage_str)

        # finally match action
        match args[0]:
            case 'connectivity':
                NetTestActions.test_connectivity(src, dst)
            case 'latency':
                pass
            case 'tp':
                NetTestActions.test_tp(src, dst, run_asynch)
            case _:
                print(usage_str)
                return

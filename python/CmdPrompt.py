from __future__ import annotations

import cmd
from python.MyCmd import MyCmd

from python.CmdActions import CoreActions, DonorActions, MtActions, UeActions, DuActions, IabNodeActions, \
    NetTestActions
from python.NetElements import NetElNotFoundException
from python.IabNet import IabNet
import sys


class PromptWorker(MyCmd):

    iab_net: IabNet

    def __init__(self, iab_net):
        self.iab_net = iab_net
        super().__init__()

    def do_help(self, arg: str) -> bool | None:
        print("Todo: help page")

    def do_core(self, args: str):
        args = args.split()
        if len(args) < 1:
            print("Usage: core ACTION")
            return
        match args[0]:
            case 'start':
                if not CoreActions.core_status_action(self.iab_net):
                    CoreActions.core_start_action(self.iab_net)
            case 'stop':
                if CoreActions.core_status_action(self.iab_net):
                    CoreActions.core_stop_action(self.iab_net)
            case 'status':
                CoreActions.core_status_action(self.iab_net)
            case 'stop -f':
                CoreActions.core_stop_action(self.iab_net)
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
            case _:
                print("Unrecognized action")

    def do_mt(self, args: str):
        args = args.split()
        if len(args) < 2:
            print("Usage: mt ID ACTION")
            return
        try:
            mt = self.iab_net.get_mt_by_id(int(args[0]))
        except NetElNotFoundException:
            print("MT not found")
            return

        match args[1]:
            case 'status':
                MtActions.status(mt)
            case 'start':
                MtActions.start(mt)
            case 'stop':
                MtActions.stop(mt)
            case 'tail':
                mt.tail()
            case 'kill':
                mt.kill()
            case _:
                print('Action {} not recognized'.format(args[1]))

    def do_ue(self, args: str):
        args = args.split()
        if len(args) < 2:
            print("Usage: ue ID ACTION")
            return
        try:
            ue = self.iab_net.get_ue_by_id(int(args[0]))
        except NetElNotFoundException:
            print("UE not found")
            return

        match args[1]:
            case 'status':
                UeActions.status(ue)
            case 'start':
                UeActions.start(ue)
            case 'stop':
                UeActions.stop(ue)
            case 'tail':
                ue.tail()
            case 'kill':
                ue.kill()
            case _:
                print('Action {} not recognized'.format(args[1]))

    def do_du(self, args: str):
        args = args.split()
        if len(args) < 2:
            print("Usage: du ID ACTION")
            return
        try:
            du = self.iab_net.get_du_by_id(int(args[0]))
        except NetElNotFoundException:
            print("DU not found")
            return

        match args[1]:
            case 'status':
                DuActions.status(du)
            case 'start':
                DuActions.start(du)
            case 'stop':
                DuActions.stop(du)
            case 'tail':
                du.tail()
            case 'kill':
                du.kill()
            case _:
                print('Action {} not recognized'.format(args[1]))

    def do_donor(self, args: str):
        args = args.split()
        if len(args) < 2:
            print("Usage: donor ID ACTION")
            return
        try:
            donor = self.iab_net.get_donor_by_id(int(args[0]))
        except NetElNotFoundException:
            print("DU not found")
            return

        match args[1]:
            case 'status':
                DonorActions.status(donor)
            case 'start':
                DonorActions.start(donor)
            case 'stop':
                DonorActions.stop(donor)
            case 'tail':
                donor.tail()
            case 'kill':
                donor.kill()
            case _:
                print('Action {} not recognized'.format(args[1]))

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
                IabNodeActions.add(mt=mt, du=du, iab_net=self.iab_net)
            case 'del':
                if len(args) != 2:
                    print(usage_str)
                    return
                try:
                    iab_n = self.iab_net.get_iab_by_id(args[1])
                except NetElNotFoundException:
                    print("IAB node {} not found".format(args[1]))
                    return
                IabNodeActions.delete(iab_n, self.iab_net)
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
                    MtActions.status(iab_n.mt)
                if iab_n.du is not None:
                    DuActions.status(iab_n.du)
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
                IabNodeActions.stop(iab_n)
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
                            case 'donor':
                                IabNodeActions.set_parent(iab_n, self.iab_net.donor)
                            case 'node':
                                if len(args) != 5:
                                    print(usage_str)
                                    return
                                try:
                                    parent_iab_n = self.iab_net.get_iab_by_id(args[4])
                                except NetElNotFoundException:
                                    print("IAB node {} not found".format(args[4]))
                                    return
                                IabNodeActions.set_parent(iab_n, parent_iab_n)
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

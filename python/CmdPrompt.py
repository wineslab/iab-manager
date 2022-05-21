from __future__ import annotations

import cmd

from python.CmdActions import CoreActions, NetActions, DonorActions, MtActions, UeActions, DuActions, IabNodeActions
from python.NetElements import IabNet, NetElNotFoundException


class PromptWorker(cmd.Cmd):

    iab_net: IabNet

    def __init__(self,iab_net):
        self.iab_net = iab_net
        super().__init__()

    def do_help(self, arg: str) -> bool | None:
        print("Todo: help page")

    def do_list_mt(self, arg: str):
        print(len(self.iab_net.mt_list))

    def do_core(self, act: str):
        match act:
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
            case _:
                print("Unrecognized action")

    def do_list(self, target: str):
        match target:
            case 'mt':
                NetActions.print_mt_list(self.iab_net)
            case 'du':
                NetActions.print_du_list(self.iab_net)
            case 'ue':
                NetActions.print_ue_list(self.iab_net)
            case 'iab_node':
                NetActions.print_iab_node_list(self.iab_net)
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
            case _:
                print('Action {} not recognized'.format(args[1]))

    def do_donor(self, args: str):
        usage_str = "Usage: donor {start | stop | status}"
        if args is None:
            print(usage_str)
            return
        match args:
            case 'start':
                DonorActions.start(self.iab_net)
            case 'stop':
                DonorActions.stop(self.iab_net)
            case 'status':
                DonorActions.status(self.iab_net)
            case _:
                print(usage_str)

    def do_iab_node(self, args: str):
        usage_str = "Usage: iab-node {add | del | status} {{du_id} {mt_id} | iab_id}"
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
                pass
            case 'status':
                pass

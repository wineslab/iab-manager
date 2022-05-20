from __future__ import annotations
import cmd
from python.NetElements import IabNet, NetElNotFoundException
from python.CmdActions import CoreActions, NetActions, DonorActions, MtActions


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
            case _:
                print("Unrecognized action")

    def do_mt(self, args: str):
        args = args.split()
        if len(args) < 2:
            print("Usage: mt ID ACTION")
            return
        try:
            mt = self.iab_net.get_mt_by_id(args[0])
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

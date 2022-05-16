from __future__ import annotations
import cmd
from net_config import IabNet

class PromptWorker(cmd.Cmd):
    iab_net: IabNet

    def __init__(self,iab_net):
        self.iab_net = iab_net
        super().__init__()

    def do_help(self, arg: str) -> bool | None:
        print("Todo: help page")

    def do_list_mt(self, arg: str):
        print(len(self.iab_net.mt_list))

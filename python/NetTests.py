from __future__ import annotations
from python.SRN import Srn
from python.NetElements import NetElem, Mt, Du, Ue, Donor, Core
from python.ShCommands import ShCommands


def connectivity_test(src: NetElem, dest: NetElem):

    if isinstance(src, Mt):
        src_ip = src.get_tr0_ip()
    elif isinstance(src, Du):
        src_ip = src.get_tr0_ip()
    elif isinstance(src, Ue):
        src_ip = src.get_tun_ep()
    elif isinstance(src, Donor):
        src_ip = src.get_tr0_ip()
    elif isinstance(src, Core):
        src_ip = src.get_tr0_ip()

    if isinstance(dest, Mt):
        dst_ip = src.get_tr0_ip()
    elif isinstance(dest, Du):
        dst_ip = src.get_tr0_ip()
    elif isinstance(dest, Ue):
        dst_ip = src.get_tun_ep()
    elif isinstance(dest, Donor):
        dst_ip = src.get_tr0_ip()
    elif isinstance(dest, Core):
        dst_ip = src.get_tr0_ip()

    return src.srn.run_command(ShCommands.single_ping(src_ip, dst_ip))

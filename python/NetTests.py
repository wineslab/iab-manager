from __future__ import annotations
from python.SRN import Srn
from python.NetElements import NetElem, Mt, Du, Ue, Donor, Core, IabNode
from python.ShStringUtils import ShCommands


def connectivity_test(src: NetElem, dest: NetElem):
    """
    Test connectivity between source NetElem and dest NetElem through ping
    :param src:
    :param dest:
    :return: True if connectivity, else false
    """
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
    elif isinstance(src, IabNode):
        src_ip = src.du.srn.get_tr0_ip()

    if isinstance(dest, Mt):
        dst_ip = dest.get_tr0_ip()
    elif isinstance(dest, Du):
        dst_ip = dest.get_tr0_ip()
    elif isinstance(dest, Ue):
        dst_ip = dest.get_tun_ep()
    elif isinstance(dest, Donor):
        dst_ip = dest.get_tr0_ip()
    elif isinstance(dest, Core):
        dst_ip = dest.get_tr0_ip()
    elif isinstance(dest, IabNode):
        dst_ip = dest.du.srn.get_tr0_ip()

    return src.srn.run_command(ShCommands.single_ping(src_ip, dst_ip))

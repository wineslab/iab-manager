from __future__ import annotations
from python.SRN import Srn
from python.NetElements import NetElem, Mt, Du, Ue, Donor, Core, IabNode
from python.ShStringUtils import ShCommands
from json import loads as json_parse
from types import SimpleNamespace
from time import strftime
from os import makedirs


def connectivity_test(src: NetElem, dest: NetElem):
    """
    Test connectivity between source NetElem and dest NetElem through ping
    :param src:
    :param dest:
    :return: True if connectivity, else false
    """
    src_ip, dst_ip = __extract_src_dst_addr(src, dest)
    return src.srn.run_command(ShCommands.single_ping(src_ip, dst_ip))


def tp_test_task(src: NetElem, dest: NetElem, verbose, reverse, **kwargs):
    asynchronous = kwargs.get('asynchronous', False)
    # 1: test
    src_ip, dst_ip = __extract_src_dst_addr(src, dest)
    # start iperf server on dest srn
    if verbose:
        print("Starting iperf server on NetElem id {}".format(dest.id))
    res = dest.start_iperf_server()
    if not res:
        if verbose:
            print("Failed")
        return False
    # start iperf server on source srn
    if verbose:
        print("Starting iperf client on NetElem id {}".format(src.id))
    res = src.start_iperf_client(use_tmux=False,
                                 server_addr=dst_ip,
                                 rev=reverse,
                                 asynchronous=asynchronous)
    if asynchronous:
        res = res.join()
        #return res
    if not res:
        if verbose:
            print("Failed")
        return False

    # 2: parse json
    iperf_data = json_parse(res.stdout.strip(), object_hook=lambda d: SimpleNamespace(**d))
    # 3: save json locally
    makedirs("iperf_results", exist_ok=True)
    with open("iperf_results/"+strftime("%Y%m%d-%H%M%S"), "w") as json_target:
        json_target.write(res.stdout.strip())
    # 3: inform (verbose/non-verbose)
    st = "Throughput test between {} {} and {} {} completed\n".format(
        src.__class__.__name__,
        src.id,
        dest.__class__.__name__,
        dest.id,
    )
    if verbose:
        st = st + "Throughput: {} Mbps - Packet loss: {}".format(
            str(round(iperf_data.end.sum.bits_per_second/1e6)),
            str(iperf_data.end.sum.lost_percent)
        )
    print(st)
    return True, st


def __extract_src_dst_addr(src: NetElem, dest: NetElem):
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

    return src_ip, dst_ip

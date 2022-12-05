from __future__ import annotations
from python.SRN import Srn
from python.NetElements import NetElem, Mt, Du, Ue, Donor, Core, IabNode, RadioElem
from python.ShStringUtils import ShCommands, NetIdentities
from json import loads as json_parse
from types import SimpleNamespace
from time import strftime, sleep
from os import makedirs
import re
import numpy as np
import os


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
        # return res
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
        #src_ip = src.get_tr0_ip()
        src_ip = NetIdentities.CORE_DOCKER_IP
    elif isinstance(src, IabNode):
        src_ip = src.du.srn.get_tr0_ip()

    if isinstance(dest, Mt):
        if isinstance(src, Core):
            dst_ip = dest.get_tun_ep()
        else:
            dst_ip = dest.get_tr0_ip()
    elif isinstance(dest, Du):
        dst_ip = dest.get_tr0_ip()
    elif isinstance(dest, Ue):
        dst_ip = dest.get_tun_ep()
    elif isinstance(dest, Donor):
        dst_ip = dest.get_tr0_ip()
    elif isinstance(dest, Core):
        #dst_ip = dest.get_tr0_ip()
        dst_ip = NetIdentities.CORE_DOCKER_IP
    elif isinstance(dest, IabNode):
        dst_ip = dest.du.srn.get_tr0_ip()

    return src_ip, dst_ip


def ping_test(netelem, out_dir=None):
    reg_ping = re.compile("time=(([0-9])*(\.*)([0-9])*) ms$")
    rtts = []
    if isinstance(netelem, Ue):
        netelem.srn.add_ip_route(NetIdentities.DOCKER_NET, NetIdentities.SPGWU_TUN_EP)

    print(f"Pinging {NetIdentities.CORE_DOCKER_IP} from {netelem} ...", end='', flush=True)
    for i in range(5):
        # OAI has some weird issue, sometime the ping (1hop) is 15ms, sometime is 8. We repeat 5 times to average this out
        res = netelem.srn.run_command(ShCommands.PING.format(NetIdentities.CORE_DOCKER_IP))
        if not res:
            print("Ping Failed")
            return 0
        for l in res.stdout.split('\n'):
            m = reg_ping.search(l)
            if m:
                rtt = float(m.group(1))
                rtts.append(rtt)
        print(".", end='', flush=True)
    print("")
    rtts = np.array(rtts)
    print(f'Average RTT is {rtts.mean():.3f} ms')
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        np.savetxt(f'{out_dir}/{netelem.topo_id}.rtt', rtts)
    return bool(len(rtts))


def iperf_test(netelem: RadioElem, core: Core, direction: str, out_dir=None, bw=10):
    reg_iperf = re.compile("([0-9]*\.[0-9]*) Mbits.*ms  ([0-9]+\/[0-9]+) \(([0-9]+.*[0-9]*)%\)  $")

    if isinstance(netelem, Ue):
        netelem.srn.add_ip_route(NetIdentities.DOCKER_NET, NetIdentities.SPGWU_TUN_EP)

    # Perform an UDP test between the node and the Core
    if direction == "ul":
        res = iperf_test_up(netelem, core, bw)
    elif direction == "dl":
        res = iperf_test_dl(netelem, core, bw)
    else:
        return
    thrs = []
    losses = []
    for l in res.stdout.split('\n'):
        if '- - - -' in l:
            # Workaround to remove last line
            break
        m = reg_iperf.search(l)
        if m:
            thrs.append(float(m.group(1)))
            losses.append(float(m.group(3)))
    thrs = np.array(thrs)
    losses = np.array(losses)
    if out_dir:
        np.savetxt(f'{out_dir}/{netelem.topo_id}.{direction}.thr', thrs)
        np.savetxt(f'{out_dir}/{netelem.topo_id}.{direction}.loss', losses)
    print(f'Average Throughput is {thrs.mean():.3f} Mbps, with {losses.mean():.3f} % packet loss')
    return(bool(len(thrs)))


def iperf_test_up(netelem: RadioElem, core: Core, bw):
    print(f"Performing upload test from {netelem} to Core")
    core.srn.run_command_disown('iperf3 -s > /tmp/iperf_out 2>&1')
    res = netelem.srn.run_command_disown(f'iperf3 -uc {NetIdentities.CORE_DOCKER_IP} -b {bw}M')
    sleep(12)
    res = core.srn.run_command('pkill iperf3; cat /tmp/iperf_out; rm /tmp/iperf_out')
    print(res)
    return res


def iperf_test_dl(netelem: RadioElem, core: Core, bw):
    print(f"Performing download test from {netelem} to Core")
    core.srn.run_command_disown('iperf3 -s')
    res = netelem.srn.run_command_disown(f'iperf3 -Ruc {NetIdentities.CORE_DOCKER_IP} -b {bw}M > /tmp/iperf_out 2>&1')
    sleep(12)
    core.srn.run_command('pkill iperf3')
    res = netelem.srn.run_command('cat /tmp/iperf_out; rm /tmp/iperf_out')
    print(res)
    return res

# This is a iab network manager

# import warnings
# from cryptography.utils import CryptographyDeprecationWarning
# with warnings.catch_warnings():
#    warnings.filterwarnings('ignore', category=CryptographyDeprecationWarning)
#    import fabric
#    from paramiko import SSHConfig
# from socket import gethostbyname


from pathlib import Path
import subprocess
from SRN import Srn, SrnTypes
from NetElements import IabNet, NodeRoleSequences
from CmdPrompt import PromptWorker
from fabric import Connection
from invoke import exceptions as invoke_exc


def manager_init():
    local = True if Path("/core_srn").is_file() else False

    if not local:
        gw_conn = Connection(host='colosseum-gw', user='eugeniomoro')
        ep_conn = Connection(host='wineslab-001', user='root', gateway=gw_conn, connect_kwargs={"password": "pass"})
        # get srn ip and id
        get_snr_id_cmd = "ip -f inet addr show col0 | grep -Po 'inet \K[\d.]+'"
        col0_self_ip = ep_conn.run(get_snr_id_cmd, hide=True).stdout.strip()
        octects = col0_self_ip.split(".")
        self_id = octects[-1]
        col0_prefix = octects[0] + "." + octects[1] + "." + octects[2] + "."
        srn_list = [Srn(local=True, ip=col0_self_ip, id=self_id, overriding_conn=ep_conn)]
        srn_list[0].type = SrnTypes.CORE

    # res = ep_conn.run('arpsend -D -e 172.30.101.102 col0 -c 1', warn=True)

    # find active srns
    for host in range(int(self_id) + 1, 121):
        # ep_conn.run("ping -c 1 " + col0_prefix + str(host), hide=True)

        if ep_conn.run("arpsend -D -e {} col0 -c 1".format(col0_prefix + str(host)), warn=True, hide=True).exited == 3:
            print("SRN found at " + col0_prefix + str(host))

            # add to list
            s = Srn(ip=(col0_prefix + str(host)), id=str(host), conn_gw=ep_conn)
            srn_list.append(s)

            # test ssh connection
            s.test_ssh_conn()
            print("---SSH connection established")

            # retrieve type
            s.set_srn_type()
            print("---SRN Type: " + str(s.type))

    # new iab network
    iab_network = IabNet(srn_list)
    iab_network.apply_roles(NodeRoleSequences.DEFAULT_11_SRN_SEQUENCE)

    print("Init Done")
    return iab_network


if __name__ == '__main__':
    iab_net = manager_init()
    PromptWorker(iab_net).cmdloop()

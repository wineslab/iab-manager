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
from net_config import IabNet, NodeRoleSequences
from CmdPrompt import PromptWorker


def manager_init():

    # can only run on core machine
    assert Path("/core_srn").is_file(), "This is not a core srn"

    # get srn ip and id
    get_snr_id_cmd = "ip -f inet addr show col0 | grep -Po 'inet \K[\d.]+'"
    col0_self_ip = subprocess.getoutput(get_snr_id_cmd)
    octects = col0_self_ip.split(".")
    self_id = octects[-1]
    col0_prefix = octects[0] + "." + octects[1] + "." + octects[2] + "."

    srn_list = [Srn(local=True, ip=col0_self_ip, id=self_id)]
    srn_list[0].type = SrnTypes.CORE

    # find active srns
    for host in range(int(self_id) + 1, 121):
        # print("ping -c 1 " + str(host))
        if subprocess.getstatusoutput("ping -c 1 " + col0_prefix + str(host))[0] == 0:
            print("SRN found at " + col0_prefix + str(host))

            # add to list
            s = Srn(ip=(col0_prefix + str(host)), id=str(host))
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

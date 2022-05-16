from __future__ import annotations
import SRN
from typing import List


class IabNet:
    snr_list: List[SRN.Srn]
    donor: Donor
    du_list: List[Du]
    mt_list: List[Mt]
    ue_list: List[Ue]

    def __init__(self, snr_list: list[SRN.Srn]):
        self.snr_list = snr_list
        self.du_list = []
        self.mt_list = []
        self.ue_list = []

    def apply_roles(self, node_role_sequence):
        # check if enough snr
        if len(node_role_sequence) > len(self.snr_list):
            raise NameError("Role sequence list longer than available snrs")
        for seq, role in enumerate(node_role_sequence):
            # check if snr supports role
            if self.snr_list[seq].supports_role(role):
                # role is supported, so create new NetElem accordingly
                match role:
                    case NetRoles.DONOR:
                        donor = Donor(self.snr_list[seq])
                    case NetRoles.MT:
                        self.mt_list.append(Mt(self.snr_list[seq]))
                    case NetRoles.DU:
                        self.du_list.append(Du(self.snr_list[seq]))
                    case NetRoles.UE:
                        self.ue_list.append(Ue(self.snr_list[seq]))
                # save role in srn
                self.snr_list[seq].net_role = role



class NetElem:
    srn: SRN.Srn

    def __init__(self, srn):
        self.srn = srn


class Du(NetElem):
    def __init__(self, srn):
        super().__init__(srn)
        self.mt = None


class Mt(NetElem):
    def __init__(self, srn):
        self.du = None
        super().__init__(srn)


class Donor(NetElem):
    def __init__(self, srn):
        self.du = None
        super().__init__(srn)


class Ue(NetElem):
    def __init__(self, srn):
        self.associated_bs = None
        super().__init__(srn)


class IabNode:
    def __init__(self, du, mt):
        self.du = du
        self.mt = mt


class NetRoles:
    CORE = 0
    DU = 1
    MT = 2
    UE = 3
    DONOR = 4


class NodeRoleSequences:
    DEFAULT_11_SRN_SEQUENCE = [
        NetRoles.CORE,
        NetRoles.DONOR,
        NetRoles.MT,
        NetRoles.DU,
        NetRoles.MT,
        NetRoles.DU,
        NetRoles.MT,
        NetRoles.DU,
        NetRoles.UE,
        NetRoles.UE,
        NetRoles.UE
    ]



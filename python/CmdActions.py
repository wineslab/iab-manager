from python.NetElements import IabNet, Mt, Ue, Du, IabNode


class CoreActions:
    @staticmethod
    def core_status_action(iab_net: IabNet):
        print("Checking core status...")
        if iab_net.core.status():
            print("Core running")
            return True
        else:
            print("Core not running")
            return False

    @staticmethod
    def core_start_action(iab_net: IabNet):
        print("Starting core...")
        if iab_net.core.start():
            print("Done")
        else:
            print("Failed")

    @staticmethod
    def core_stop_action(iab_net: IabNet):
        print("Stopping core...")
        if iab_net.core.stop():
            print("Done")
        else:
            print("Failed")


class NetActions:

    @staticmethod
    def print_mt_list(iab_net: IabNet):
        print(iab_net.mt_list_tostring())

    @staticmethod
    def print_du_list(iab_net: IabNet):
        print(iab_net.du_list_tostring())

    @staticmethod
    def print_ue_list(iab_net: IabNet):
        print(iab_net.ue_list_tostring())

    @staticmethod
    def print_iab_node_list(iab_net: IabNet):
        print(iab_net.iab_node_list_tostring())


class DonorActions:
    @staticmethod
    def status(iab_net: IabNet):
        print("Checking Donor status...")
        if iab_net.donor.status():
            print("Donor running")
            return True
        else:
            print("Donor not running")
            return False

    @staticmethod
    def start(iab_net: IabNet):
        if not DonorActions.status(iab_net):
            print("Starting donor in tmux")
            iab_net.donor.start_disown()

    @staticmethod
    def stop(iab_net: IabNet):
        if DonorActions.status(iab_net):
            print("Stopping donor")
            iab_net.donor.stop()


class MtActions:
    @staticmethod
    def status(mt: Mt):
        print("Checking MT status...")
        if mt.status():
            print("MT running")
            return True
        else:
            print("MT not running")
            return False

    @staticmethod
    def start(mt: Mt):
        if not MtActions.status(mt):
            print("Starting MT in tmux")
            mt.start()

    @staticmethod
    def stop(mt: Mt):
        if MtActions.status(mt):
            print("Stopping MT")
            mt.stop()


class UeActions:
    @staticmethod
    def status(ue: Ue):
        print("Checking UE status...")
        if ue.status():
            print("UE running")
            return True
        else:
            print("UE not running")
            return False

    @staticmethod
    def start(ue: Ue):
        if not UeActions.status(ue):
            print("Starting UE in tmux")
            ue.start_disown()

    @staticmethod
    def stop(ue: Ue):
        if UeActions.status(ue):
            print("Stopping UE")
            ue.stop()


class DuActions:
    @staticmethod
    def status(du: Du):
        print("Checking DU status...")
        if du.status():
            print("DU running")
            return True
        else:
            print("DU not running")
            return False

    @staticmethod
    def start(du: Du):
        if not DuActions.status(du):
            print("Starting DU in tmux")
            du.start_disown()

    @staticmethod
    def stop(du: Du):
        if DuActions.status(du):
            print("Stopping DU")
            du.stop()


class IabNodeActions:
    @staticmethod
    def add(mt: Mt, du: Du, iab_net: IabNet):
        if iab_net.add_iab_node(mt,du):
            print("Successfully added iab node with id {}".format(iab_net.iab_list[-1].id))
        else:
            print('Add failed')
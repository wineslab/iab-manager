from python.NetElements import IabNet, Mt


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
        if not MtActions.status():
            print("Starting MT in tmux")
            mt.start()

    @staticmethod
    def stop(mt: Mt):
        if MtActions.status():
            print("Stopping MT")
            mt.stop()

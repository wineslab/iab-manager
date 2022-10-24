from python.NetElements import IabNet, Mt, Ue, Du, IabNode
import python.NetTests as NetTests
from python.TaskManager import TaskManager


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
        print("Checking MT {} status...".format(mt.id))
        if mt.status():
            print("MT {} running".format(mt.id))
            return True
        else:
            print("MT {} not running".format(mt.id))
            return False

    @staticmethod
    def start(mt: Mt):
        if not MtActions.status(mt):
            print("Starting MT {} in tmux".format(mt.id))
            mt.start()

    @staticmethod
    def stop(mt: Mt):
        if MtActions.status(mt):
            print("Stopping MT {}".format(mt.id))
            mt.stop()


class UeActions:
    @staticmethod
    def status(ue: Ue):
        print("Checking UE {} status...".format(ue.id))
        if ue.status():
            print("UE {} running".format(ue.id))
            return True
        else:
            print("UE {} not running".format(ue.id))
            return False

    @staticmethod
    def start(ue: Ue):
        if not UeActions.status(ue):
            print("Starting UE {} in tmux".format(ue.id))
            ue.start_disown()

    @staticmethod
    def stop(ue: Ue):
        if UeActions.status(ue):
            print("Stopping UE {}".format(ue.id))
            ue.stop()


class DuActions:
    @staticmethod
    def status(du: Du):
        print("Checking DU {} status...".format(du.id))
        if du.status():
            print("DU {} running".format(du.id))
            return True
        else:
            print("DU {} not running".format(du.id))
            return False

    @staticmethod
    def start(du: Du):
        if not DuActions.status(du):
            print("Starting DU {} in tmux".format(du.id))
            du.start_disown()

    @staticmethod
    def stop(du: Du):
        if DuActions.status(du):
            print("Stopping DU {}".format(du.id))
            du.stop()


class IabNodeActions:
    @staticmethod
    def add(mt: Mt, du: Du, iab_net: IabNet):
        if iab_net.add_iab_node(mt, du):
            print("Successfully added iab node with id {}".format(iab_net.iab_list[-1].id))
        else:
            print('Add failed')

    @staticmethod
    def delete(iab_node: IabNode, iab_net: IabNet):
        iab_net.del_iab_node(iab_node)

    @staticmethod
    def start(iab_node: IabNode, iab_net: IabNet):
        if iab_node.parent is None:
            print("IAB node {} does not have a parent".format(iab_node.id))
            return
        print("Starting IAB node {}...".format(iab_node.id))
        if iab_node.du is None:
            print("IAB node {} has no du".format(iab_node.id))
            return
        if iab_node.mt is None:
            print("IAB node {} has no mt".format(iab_node.id))
            return
        rt = True
        MtActions.start(iab_node.mt)
        print("Checking if MT {} is ready... (will wait 20s max)".format(iab_node.mt.id))
        if iab_node.mt.check_softmodem_ready():
            print("MT {} is ready".format(iab_node.mt.id))
        else:
            print("MT {} failed, aborting...".format(iab_node.mt.id))
            return
        print('Adding core routes')
        iab_net.update_iabnode_route(iab_node)
        print('Restarting DU..')
        iab_node.du.stop()
        iab_node.du.start()
        print("Iab node {} started".format(iab_node.id))

    @staticmethod
    def stop(iab_node: IabNode):
        iab_node.stop()
        print("Iab node {} stopped".format(iab_node.id))

    @staticmethod
    def set_parent(iab_node: IabNode, parent):
        print("Setting IAB node {} parent as {}".format(iab_node.id, parent.id))
        iab_node.set_parent(parent)


class NetTestActions:

    @staticmethod
    def test_connectivity(src, dst):
        print("Connectivity test between {} {} and {} {}...".format(
            src.__class__.__name__,
            src.id,
            dst.__class__.__name__,
            dst.id,
        ))
        if NetTests.connectivity_test(src, dst):
            print("Successful")
            return True
        else:
            print("Failed")
            return False

    @staticmethod
    def test_tp(src, dst, run_asynch):
        print("Throughput test between {} {} and {} {} started".format(
            src.__class__.__name__,
            src.id,
            dst.__class__.__name__,
            dst.id,
        ))
        if run_asynch:
            kwargs = {'src': src, 'dest': dst, 'verbose': False, 'reverse': False, 'asynchronous': True}
            TaskManager.launch_task_thread(NetTests.tp_test_task, kwargs=kwargs)
        else:
            kwargs = {'src': src, 'dest': dst, 'verbose': False, 'reverse': False, 'asynchronous': True}
            NetTests.tp_test_task(kwargs)
        # TaskManager.launch_task(print, ('ciao',))

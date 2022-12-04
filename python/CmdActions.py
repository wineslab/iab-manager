from python.NetElements import Donor, Mt, Ue, Du, IabNode
from python.IabNet import IabNet
import python.NetTests as NetTests
from python.TaskManager import TaskManager


class IabNodeActions:
    @staticmethod
    def start(iab_node: IabNode, iab_net: IabNet):
        if iab_node.parent is None:
            print("IAB node {} does not have a parent".format(iab_node.id))
            return False
        print("Starting IAB node {}...".format(iab_node.id))
        if iab_node.du is None:
            print("IAB node {} has no du".format(iab_node.id))
            return False
        if iab_node.mt is None:
            print("IAB node {} has no mt".format(iab_node.id))
            return False
        rt = True
        if not iab_node.mt.status():
            print(f"Starting MT {iab_node.mt}")
            iab_node.mt.start()
        else:
            print(f"MT {iab_node.mt} already running")
        print("Checking if MT {} is ready... (will wait 20s max)".format(iab_node.mt.id))
        if iab_node.mt.check_softmodem_ready():
            print("MT {} is ready".format(iab_node.mt.id))
        else:
            print("MT {} failed, aborting...".format(iab_node.mt.id))
            return False
        print('Adding core routes')
        if iab_net.update_iabnode_route(iab_node):
            print('Restarting DU..')
            iab_node.du.stop()
            iab_node.du.start()
            print("Iab node {} started".format(iab_node.id))
            return True
        else:
            print(f"MT {iab_node.mt} has no gtpu tunnel")
            return False


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

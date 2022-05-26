from __future__ import annotations
import multiprocessing
import threading


class TaskManager:

    @staticmethod
    def launch_task(target, args):
        p = multiprocessing.Process(target=target, args=args)
        p.start()

    @staticmethod
    def launch_task_thread(target, kwargs):
        t = threading.Thread(target=target, kwargs=kwargs)
        t.start()

    @staticmethod
    def promise_joiner(promise):
        #res = promise.join()
        print('Promise terminated')
        #return res

    @staticmethod
    def test(target, args):
        prom = target(args)

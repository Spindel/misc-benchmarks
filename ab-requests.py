#!/bin/env python3
# vim: expandtab shiftwidth=4 softtabstop=4 tabstop=17 filetype=python :
"""
Upload a set of .csr files to a caramel endpoint. Used for some minor
benchmarking and to populate things"""


import requests
import hashlib
import random
import sys
import os

import threading

from queue import Queue

ENDPOINT = "devnull-as-a-service.com"
ENDPOINT = "modio.se"
CSRDIR = '/tmp/csr'
concurrent = 60  # 60 threads + 60 https connections


def pollQueue(MyQueue, sess):

    # Set up one connection per thread, and re-use that
    mydata  = threading.local()
    while True:
        fname, sha = MyQueue.get()
        result = sess.head("https://{}/".format(ENDPOINT))
        MyQueue.task_done()  # Mark a task as consumed, for queue.wait()
    conn.close()



if __name__ == "__main__":
    TheQueue = Queue()
    TheSession = requests.Session()
    print("Preparing queue")
    for _ in range(100000):
        data = (None, None)
        TheQueue.put(data)

    print("Setting up {} threads".format(concurrent))

    threads = []
    for i in range(concurrent):
        t = threading.Thread(target=pollQueue, args=(TheQueue, TheSession))
        t.daemon = True
        threads.append(t)

    print("starting threads")
    [t.start() for t in threads]

    try:
        TheQueue.join()
    except KeyboardInterrupt:
        sys.exit(1)

    print("All jobs done")

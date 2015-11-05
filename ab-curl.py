#!/bin/env python3
# vim: expandtab shiftwidth=4 softtabstop=4 tabstop=17 filetype=python :
"""
Upload a set of .csr files to a caramel endpoint. Used for some minor
benchmarking and to populate things"""


import random
import sys
import os

import threading
from io import BytesIO
import pycurl
from queue import Queue

ENDPOINT = "devnull-as-a-service.com"
ENDPOINT = "modio.se"
CSRDIR = '/tmp/csr'
concurrent = 60  # 60 threads + 60 https connections


def pollQueue(MyQueue):
    buf = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'https://{}/'.format(ENDPOINT))
    c.setopt(c.SSL_VERIFYPEER, False)
    c.setopt(c.WRITEDATA, buf)
    c.setopt(c.NOBODY, True)
    c.setopt(c.HEADER, True)

    # Set up one connection per thread, and re-use that
    mydata  = threading.local()
    while True:
        fname, sha = MyQueue.get()
        c.perform()
        buf.truncate(0)
        buf.seek(0)
        MyQueue.task_done()  # Mark a task as consumed, for queue.wait()



if __name__ == "__main__":
    TheQueue = Queue()

    print("Preparing queue")
    for _ in range(100000):
        data = (None, None)
        TheQueue.put(data)

    print("Setting up {} threads".format(concurrent))

    threads = []
    for i in range(concurrent):
        t = threading.Thread(target=pollQueue, args=(TheQueue,))
        t.daemon = True
        threads.append(t)

    print("starting threads")
    [t.start() for t in threads]

    try:
        TheQueue.join()
    except KeyboardInterrupt:
        sys.exit(1)

    print("All jobs done")

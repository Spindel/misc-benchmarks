#!/bin/env python3
# vim: expandtab shiftwidth=4 softtabstop=4 tabstop=17 filetype=python :
"""
Upload a set of .csr files to a caramel endpoint. Used for some minor
benchmarking and to populate things"""


import random
import sys
import os
import hashlib

import threading
from io import BytesIO
import pycurl
from queue import Queue

ENDPOINT = "devnull-as-a-service.com"
ENDPOINT = "caramel.modio.se"
CSRDIR = '/tmp/csr'
concurrent = 20  # 60 threads + 60 https connections



def postfile(name, conn):
    """The filename is the sha256sum in hex of the CSR.
    Calculate it, and post the data"""
    buf = BytesIO()
    conn.setopt(conn.WRITEDATA, buf)
    with open(name, 'rb') as f:
        data = f.read()
    sha = hashlib.sha256(data).hexdigest()
    conn.setopt(conn.URL, 'https://{}/{}'.format(ENDPOINT, sha))
    with open(fname, 'rb') as f:
        data = f.read()
    conn.setopt(conn.POSTFIELDS, data)
    conn.perform()


def pollQueue(MyQueue):
    c = pycurl.Curl()
    c.setopt(c.SSL_VERIFYPEER, False)
    c.setopt(c.NOBODY, True)
    c.setopt(c.HEADER, True)
    c.setopt(c.POST, True)
    # Set up one connection per thread, and re-use that
    count = 0
    while True:
        fname = MyQueue.get()
        MyQueue.task_done()  # Mark a task as consumed, for queue.wait()
        postfile(fname, c)
        count += 1
        if count % 100 == 0:
            print("{}: {}  ({} remaining)".format(threading.current_thread(),
                                                  count, MyQueue.qsize()))


def get_files(limit=None):
    """Returns an iterator of filenames, shuffled."""

    print("Listing files")
    files = os.listdir(CSRDIR)
    total = len(files)
    limit = limit if limit else total

    print("Shuffling: {} files".format(total))
    random.shuffle(files)
    print("Done shuffling.")
    for f in files[:limit]:
        yield os.path.join(CSRDIR, f)


if __name__ == "__main__":
    TheQueue = Queue()

    print("Preparing queue")
    for fname in get_files():
        TheQueue.put(fname)

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

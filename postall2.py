#!/bin/env python3
# vim: expandtab shiftwidth=4 softtabstop=4 tabstop=17 filetype=python :
"""
Upload a set of .csr files to a caramel endpoint. Used for some minor
benchmarking and to populate things"""


import http.client
import hashlib
import random
import sys
import os


from threading import Thread, current_thread
from queue import Queue

ENDPOINT = "caramel.modio.se"
CSRDIR = '/tmp/csr'
concurrent = 60  # 60 threads + 60 https connections


def pollQueue(q):
    conn = http.client.HTTPSConnection(ENDPOINT, 443)
    count = 0
    while True:
        fname = q.get()
        status = postfile(fname, conn)
        count += 1
        if status > 400: # 400 is already existing
            q.put(fname)
        if count % 100 == 0:
            print("{}: {}  ({} remaining)".format(current_thread(),
                                                  count, q.qsize()))
        q.task_done()
    conn.close()


def postfile(name, connection):
    with open(name, 'rb') as f:
        data = f.read()
    sha = hashlib.sha256(data).hexdigest()
    connection.request("POST", '/{}'.format(sha), body=data)
    result = connection.getresponse()
    result.read()
    return result.status


def get_files(limit=None):
    """Returns an iterator of filenames, shuffled."""

    print("Listing files")
    files = os.listdir(CSRDIR)
    total = len(files)
    limit = limit if limit else total

    print("Shuffling: {} files".format(total))
    random.shuffle(files)
    for f in files[:limit]:
        yield os.path.join(CSRDIR, f)



if __name__ == "__main__":
    TheQueue = Queue()

    print("Setting up {} threads".format(concurrent))
    for i in range(concurrent):
        t = Thread(target=pollQueue, args=(TheQueue, ))
        t.daemon = True
        t.start()

    for fname in get_files(5000):
        TheQueue.put(fname)

    try:
        TheQueue.join()
    except KeyboardInterrupt:
        sys.exit(1)

    print("All jobs done")
